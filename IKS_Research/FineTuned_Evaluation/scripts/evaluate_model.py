"""
evaluate_model.py  (v3)

Fixes:
  - Joint two-source bss_eval_sources (vocals + accompaniment together) → finite SIR
  - Uses demucs.apply.apply_model for correct internal chunking
  - SI-SDR computed per-source (scale-invariant, unaffected by joint/single convention)

Output root: D:\\IKS_Research\\FineTuned_Evaluation
Usage: C:\\iks_scripts\\venv\\Scripts\\python.exe evaluate_model.py
"""

import csv
import json
import os
import sys
import datetime
import platform
import numpy as np
import soundfile as sf
import torch
import warnings
import mir_eval
from demucs.htdemucs import HTDemucs
from demucs.apply import apply_model

BEST_PT     = r"D:\finetune_htdemucs_runs\run_002\best.pt"
INIT_PT     = r"D:\finetune_htdemucs_runs\init_2stem_model.pt"
VALID_DIR   = r"D:\dataset_prepared_saraga\valid"
EVAL_ROOT   = r"D:\IKS_Research\FineTuned_Evaluation"
TABLES_DIR  = os.path.join(EVAL_ROOT, "tables")
METRICS_DIR = os.path.join(EVAL_ROOT, "metrics")

SAMPLERATE  = 44100
SOURCES     = ["vocals", "accompaniment"]


def load_model(device):
    init_ckpt = torch.load(INIT_PT, weights_only=False, map_location="cpu")
    args, kwargs = init_ckpt["init_args_kwargs"]
    model = HTDemucs(*args, **kwargs) if args else HTDemucs(**kwargs)
    fine_ckpt = torch.load(BEST_PT, weights_only=False, map_location="cpu")
    model.load_state_dict(fine_ckpt["model_state"])
    model.eval()
    model.to(device)
    print(f"Model loaded: sources={model.sources}, step={fine_ckpt['step']}, "
          f"segment={model.segment}s, best_valid_loss={fine_ckpt['best_valid_loss']:.8f}")
    return model, fine_ckpt


def read_mono_wav(path):
    data, sr = sf.read(path, dtype="float32", always_2d=False)
    if sr != SAMPLERATE:
        raise ValueError(f"Unexpected sample rate {sr} in {path}")
    if data.ndim == 2:
        data = data.mean(axis=1)
    return data  # (N,) float32


def infer_track(model, mixture_mono, device):
    """
    Run HT-Demucs via demucs.apply.apply_model.
    Mono input is duplicated to stereo [1, 2, N] (matching training convention).
    Stereo output channels are averaged to mono for metric calculation.
    Returns dict {source: np.ndarray (N,) float32}
    """
    wav = torch.from_numpy(mixture_mono).float()
    wav = wav.unsqueeze(0).expand(2, -1).unsqueeze(0)  # (1, 2, N)
    with torch.no_grad():
        out = apply_model(
            model, wav, device=device,
            shifts=1, split=True, overlap=0.25, progress=False,
        )  # (1, n_sources, 2, N)
    estimates = {}
    for i, src in enumerate(SOURCES):
        estimates[src] = out[0, i].mean(dim=0).float().cpu().numpy()
    return estimates


def compute_si_sdr(reference_mono, estimate_mono):
    """Scale-Invariant SDR per Le Roux et al. 2019."""
    ref = torch.from_numpy(reference_mono).float()
    est = torch.from_numpy(estimate_mono).float()
    ref = ref - ref.mean()
    est = est - est.mean()
    alpha  = (est * ref).sum() / ((ref * ref).sum() + 1e-8)
    target = alpha * ref
    noise  = est - target
    return 10.0 * torch.log10(
        (target * target).sum() / ((noise * noise).sum() + 1e-8) + 1e-8
    ).item()


def compute_joint_bss_metrics(refs_dict, ests_dict, min_len):
    """
    Joint two-source bss_eval_sources evaluation.
    Passing both sources simultaneously gives finite, meaningful SIR values.

    refs_dict, ests_dict: {source_name: np.ndarray (N,)}
    Returns: {source_name: {SDR, SIR, SAR}}
    """
    ref_arr = np.stack([refs_dict[s][:min_len].astype(np.float64) for s in SOURCES])
    est_arr = np.stack([ests_dict[s][:min_len].astype(np.float64) for s in SOURCES])

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        warnings.simplefilter("ignore", RuntimeWarning)
        sdr, sir, sar, perm = mir_eval.separation.bss_eval_sources(ref_arr, est_arr)

    # perm maps estimated → reference; re-align to SOURCES order
    result = {}
    for out_idx, src in enumerate(SOURCES):
        ref_idx = perm[out_idx]   # which reference this estimate was matched to
        matched_src = SOURCES[ref_idx]
        result[matched_src] = {
            "SDR": float(sdr[out_idx]),
            "SIR": float(sir[out_idx]),
            "SAR": float(sar[out_idx]),
        }
    return result


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print(f"mir_eval version: {mir_eval.__version__}")

    model, fine_ckpt = load_model(device)

    tracks = sorted(
        [e for e in os.scandir(VALID_DIR) if e.is_dir()], key=lambda e: e.name
    )
    print(f"Found {len(tracks)} validation tracks.\n")

    rows   = []
    failed = []
    eval_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for t_idx, track in enumerate(tracks):
        print(f"[{t_idx+1}/{len(tracks)}] {track.name}")
        try:
            mix_path  = os.path.join(track.path, "mixture.wav")
            ref_paths = {
                "vocals":        os.path.join(track.path, "vocals.wav"),
                "accompaniment": os.path.join(track.path, "accompaniment.wav"),
            }
            mixture_mono = read_mono_wav(mix_path)
            estimates    = infer_track(model, mixture_mono, device)

            refs = {s: read_mono_wav(ref_paths[s]) for s in SOURCES}
            min_len = min(
                min(len(refs[s]) for s in SOURCES),
                min(len(estimates[s]) for s in SOURCES),
            )

            # Joint BSS metrics (SDR, SIR, SAR)
            bss = compute_joint_bss_metrics(refs, estimates, min_len)

            for src in SOURCES:
                si_sdr = compute_si_sdr(refs[src][:min_len], estimates[src][:min_len])
                m = {**bss[src], "SI_SDR": si_sdr}
                print(f"  {src:>14s}  SDR={m['SDR']:+.2f}  SI-SDR={m['SI_SDR']:+.2f}  "
                      f"SIR={m['SIR']:+.2f}  SAR={m['SAR']:+.2f}")
                rows.append({
                    "track_id":            t_idx + 1,
                    "track_name":          track.name,
                    "source":              src,
                    "SDR":                 round(m["SDR"],    6),
                    "SI_SDR":              round(m["SI_SDR"], 6),
                    "SIR":                 round(m["SIR"],    6),
                    "SAR":                 round(m["SAR"],    6),
                    "sample_rate":         SAMPLERATE,
                    "n_samples":           min_len,
                    "evaluation_timestamp": eval_time,
                    "metric_library":      f"mir_eval {mir_eval.__version__} (joint 2-source)",
                })
        except Exception as exc:
            failed.append({"track": track.name, "error": str(exc)})
            print(f"  ERROR: {exc}")

    if len(rows) == 0:
        print("ERROR: No tracks evaluated. Stopping."); sys.exit(1)
    if len(failed) >= 3:
        print(f"Too many failures: {failed}. Stopping."); sys.exit(1)

    # per_track_metrics.csv
    fieldnames = ["track_id","track_name","source","SDR","SI_SDR","SIR","SAR",
                  "sample_rate","n_samples","evaluation_timestamp","metric_library"]
    per_track_csv = os.path.join(TABLES_DIR, "per_track_metrics.csv")
    with open(per_track_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(rows)
    print(f"\nWrote: {per_track_csv}  ({len(rows)} rows)")

    # Aggregation
    metrics_list = ["SDR", "SI_SDR", "SIR", "SAR"]
    source_summary_rows = []
    for src in SOURCES:
        src_rows = [r for r in rows if r["source"] == src]
        if not src_rows: continue
        ss = {"source": src, "count": len(src_rows)}
        for m in metrics_list:
            arr = np.array([r[m] for r in src_rows])
            finite = arr[np.isfinite(arr)]
            ss[f"{m}_mean"]   = round(float(finite.mean())   if len(finite) else float("nan"), 6)
            ss[f"{m}_median"] = round(float(np.median(finite)) if len(finite) else float("nan"), 6)
            ss[f"{m}_std"]    = round(float(finite.std())    if len(finite) else float("nan"), 6)
            ss[f"{m}_min"]    = round(float(finite.min())    if len(finite) else float("nan"), 6)
            ss[f"{m}_max"]    = round(float(finite.max())    if len(finite) else float("nan"), 6)
        source_summary_rows.append(ss)

    ss_fields = ["source","count"] + [
        f"{m}_{s}" for m in metrics_list for s in ["mean","median","std","min","max"]
    ]
    with open(os.path.join(TABLES_DIR,"source_summary.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ss_fields)
        w.writeheader(); w.writerows(source_summary_rows)

    ms_rows = []
    for m in metrics_list:
        row = {"metric": m}
        for src in SOURCES:
            ss = next((r for r in source_summary_rows if r["source"] == src), None)
            if ss:
                row[f"{src}_mean"]   = ss[f"{m}_mean"]
                row[f"{src}_median"] = ss[f"{m}_median"]
                row[f"{src}_std"]    = ss[f"{m}_std"]
        ms_rows.append(row)
    ms_fields = ["metric"] + [f"{src}_{s}" for src in SOURCES for s in ["mean","median","std"]]
    with open(os.path.join(TABLES_DIR,"metric_summary.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ms_fields)
        w.writeheader(); w.writerows(ms_rows)

    es_rows = []
    for src in SOURCES:
        ss = next((r for r in source_summary_rows if r["source"] == src), None)
        if not ss: continue
        es_rows.append({
            "model_checkpoint":   BEST_PT, "checkpoint_step": fine_ckpt["step"],
            "dataset": VALID_DIR, "split": "valid", "n_tracks": len(tracks),
            "n_evaluated": ss["count"], "n_failed": len(failed), "source": src,
            "metric_library": f"mir_eval {mir_eval.__version__} (joint 2-source)",
            "mean_SDR": ss["SDR_mean"], "median_SDR": ss["SDR_median"],
            "mean_SI_SDR": ss["SI_SDR_mean"], "median_SI_SDR": ss["SI_SDR_median"],
            "mean_SIR": ss["SIR_mean"], "median_SIR": ss["SIR_median"],
            "mean_SAR": ss["SAR_mean"], "median_SAR": ss["SAR_median"],
            "evaluation_status": "COMPLETE" if not failed else "PARTIAL",
            "evaluation_time": eval_time,
        })
    es_fields = [
        "model_checkpoint","checkpoint_step","dataset","split","n_tracks",
        "n_evaluated","n_failed","source","metric_library",
        "mean_SDR","median_SDR","mean_SI_SDR","median_SI_SDR",
        "mean_SIR","median_SIR","mean_SAR","median_SAR",
        "evaluation_status","evaluation_time"
    ]
    with open(os.path.join(TABLES_DIR,"evaluation_summary.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=es_fields)
        w.writeheader(); w.writerows(es_rows)

    metadata = {
        "model_path": BEST_PT, "checkpoint_step": int(fine_ckpt["step"]),
        "best_valid_loss": float(fine_ckpt["best_valid_loss"]),
        "dataset_path": VALID_DIR, "split": "valid",
        "n_tracks": len(tracks), "source_list": SOURCES,
        "metric_library": "mir_eval", "metric_version": mir_eval.__version__,
        "metric_functions": [
            "mir_eval.separation.bss_eval_sources (joint 2-source: SDR, SIR, SAR)",
            "Scale-Invariant SDR (SI-SDR) per Le Roux et al. 2019 (per-source)"
        ],
        "bss_eval_convention": (
            "Both sources (vocals + accompaniment) evaluated jointly in a single "
            "bss_eval_sources call with reference shape (2, N) and estimate shape (2, N). "
            "This yields finite SIR values by including cross-source interference."
        ),
        "channel_handling": (
            "Mono duplicated to stereo [1,2,N] for inference. "
            "Stereo output averaged to mono before metrics."
        ),
        "inference_method": "demucs.apply.apply_model (split=True, overlap=0.25, shifts=1)",
        "model_segment_secs": float(model.segment),
        "sample_rate": SAMPLERATE,
        "evaluation_timestamp": eval_time,
        "python_version": sys.version, "platform": platform.platform(),
        "n_evaluated_rows": len(rows), "n_failed_tracks": len(failed),
        "failed_tracks": failed,
        "evaluation_status": "COMPLETE" if not failed else "PARTIAL",
    }
    with open(os.path.join(METRICS_DIR,"evaluation_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("\n=== EVALUATION COMPLETE ===")
    print(f"Successfully evaluated: {len(rows)//2}/{len(tracks)} tracks, {len(rows)} source evaluations")
    if failed: print(f"Failed: {failed}")
    print("\nAggregate results (mean):")
    for src in SOURCES:
        ss = next((r for r in source_summary_rows if r["source"] == src), None)
        if ss:
            print(f"  {src:>14s}:  SDR={ss['SDR_mean']:+.3f}  SI-SDR={ss['SI_SDR_mean']:+.3f}  "
                  f"SIR={ss['SIR_mean']:+.3f}  SAR={ss['SAR_mean']:+.3f}")

    return rows, source_summary_rows


if __name__ == "__main__":
    main()
