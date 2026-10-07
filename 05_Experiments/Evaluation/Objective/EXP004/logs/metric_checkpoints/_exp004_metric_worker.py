
from pathlib import Path
import json
import math
import os
import sys
import time
import warnings


# --------------------------------------------------------------------------
# BLAS / OpenMP THREAD CONTROL
# --------------------------------------------------------------------------

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["BLIS_NUM_THREADS"] = "1"


import numpy as np
import soundfile as sf
import torch

from museval.metrics import bss_eval
from torchmetrics.audio import (
    ScaleInvariantSignalDistortionRatio,
)


# --------------------------------------------------------------------------
# HARDWARE THREAD CONTROL
# --------------------------------------------------------------------------

try:
    torch.set_num_threads(1)
except Exception:
    pass

try:
    torch.set_num_interop_threads(1)
except Exception:
    pass


# --------------------------------------------------------------------------
# JSON HELPERS
# --------------------------------------------------------------------------

def atomic_write_json(
    path,
    payload,
):

    path = Path(path)

    temporary_path = path.with_suffix(
        path.suffix + ".tmp"
    )

    with open(
        temporary_path,
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            payload,
            handle,
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
        )

        handle.flush()

        try:
            os.fsync(
                handle.fileno()
            )
        except OSError:
            pass

    os.replace(
        temporary_path,
        path,
    )


def metric_scalar(
    value,
):

    array = np.asarray(
        value,
        dtype=np.float64,
    )

    if array.size != 1:

        raise RuntimeError(
            "Expected one scalar metric value, "
            f"received shape={array.shape}, "
            f"size={array.size}."
        )

    return float(
        array.reshape(-1)[0]
    )


# --------------------------------------------------------------------------
# AUDIO LOADING
# --------------------------------------------------------------------------

def load_audio(
    path,
):

    path = Path(path)

    if not path.is_file():

        raise FileNotFoundError(
            f"Audio file does not exist:\n{path}"
        )

    audio, samplerate = sf.read(
        str(path),
        dtype="float32",
        always_2d=True,
    )

    audio = np.asarray(
        audio,
        dtype=np.float32,
    )

    if audio.ndim != 2:

        raise RuntimeError(
            f"Unexpected audio dimensions for {path}: "
            f"{audio.shape}"
        )

    if audio.shape[0] == 0:

        raise RuntimeError(
            f"Audio file is empty:\n{path}"
        )

    return audio, int(samplerate)


# --------------------------------------------------------------------------
# AUDIO PAIR VALIDATION
# --------------------------------------------------------------------------

def validate_audio_pair(
    reference,
    estimate,
    reference_rate,
    estimate_rate,
    track_name,
    source_name,
):

    if reference_rate != estimate_rate:

        raise RuntimeError(
            f"Sample-rate mismatch for "
            f"{track_name} / {source_name}: "
            f"reference={reference_rate}, "
            f"estimate={estimate_rate}"
        )

    if reference.shape != estimate.shape:

        raise RuntimeError(
            f"Shape mismatch for "
            f"{track_name} / {source_name}: "
            f"reference={reference.shape}, "
            f"estimate={estimate.shape}"
        )


# --------------------------------------------------------------------------
# SI-SDR
# --------------------------------------------------------------------------

def calculate_si_sdr(
    reference,
    estimate,
):

    reference_tensor = torch.from_numpy(
        np.asarray(
            reference.T,
            dtype=np.float32,
        )
    ).unsqueeze(0)

    estimate_tensor = torch.from_numpy(
        np.asarray(
            estimate.T,
            dtype=np.float32,
        )
    ).unsqueeze(0)


    metric = (
        ScaleInvariantSignalDistortionRatio()
    )


    with torch.no_grad():

        value = metric(
            estimate_tensor,
            reference_tensor,
        )


    return metric_scalar(
        value.detach().cpu().numpy()
    )


# --------------------------------------------------------------------------
# TRACK EVALUATION
# --------------------------------------------------------------------------

def evaluate_track(
    task,
):

    track_name = task["track"]

    source_names = list(
        task["source_names"]
    )

    experiment_id = str(
        task["experiment"]
    )

    expected_sample_rate = int(
        task["sample_rate"]
    )

    expected_channels = int(
        task["channels"]
    )

    expected_sources = len(
        source_names
    )

    started = time.time()


    reference_sources = []
    estimate_sources = []
    sample_rates = []


    # ----------------------------------------------------------------------
    # LOAD ALL FOUR REFERENCE / PREDICTION STEMS
    # ----------------------------------------------------------------------

    for source_name in source_names:

        source_entry = task[
            "sources"
        ][source_name]

        reference_path = Path(
            source_entry["reference"]
        )

        prediction_path = Path(
            source_entry["prediction"]
        )


        reference_audio, reference_rate = (
            load_audio(
                reference_path
            )
        )

        prediction_audio, prediction_rate = (
            load_audio(
                prediction_path
            )
        )


        validate_audio_pair(
            reference_audio,
            prediction_audio,
            reference_rate,
            prediction_rate,
            track_name,
            source_name,
        )


        if reference_rate != (
            expected_sample_rate
        ):

            raise RuntimeError(
                f"Unexpected sample rate for "
                f"{track_name} / {source_name}: "
                f"{reference_rate}"
            )


        if reference_audio.shape[1] != (
            expected_channels
        ):

            raise RuntimeError(
                f"Unexpected channel count for "
                f"{track_name} / {source_name}: "
                f"{reference_audio.shape[1]}"
            )


        reference_sources.append(
            reference_audio
        )

        estimate_sources.append(
            prediction_audio
        )

        sample_rates.append(
            reference_rate
        )


    if len(set(sample_rates)) != 1:

        raise RuntimeError(
            f"Inconsistent source sample rates "
            f"for track {track_name}: "
            f"{sample_rates}"
        )


    samplerate = sample_rates[0]


    # ----------------------------------------------------------------------
    # STACK SOURCES
    #
    # Exact EXP003 layout:
    #
    #     (sources, samples, channels)
    # ----------------------------------------------------------------------

    references = np.stack(
        reference_sources,
        axis=0,
    ).astype(
        np.float32,
        copy=False,
    )


    estimates = np.stack(
        estimate_sources,
        axis=0,
    ).astype(
        np.float32,
        copy=False,
    )


    if references.shape != estimates.shape:

        raise RuntimeError(
            "Reference and estimate arrays "
            "have different shapes:\n"
            f"Reference: {references.shape}\n"
            f"Estimate:  {estimates.shape}"
        )


    if references.shape[0] != (
        expected_sources
    ):

        raise RuntimeError(
            "Unexpected source count:\n"
            f"Expected: {expected_sources}\n"
            f"Found:    {references.shape[0]}"
        )


    # ----------------------------------------------------------------------
    # BSSEVAL V4
    #
    # This intentionally matches EXP003.
    #
    # Museval internally calculates ISR as part of the BSSEval result.
    # ISR is deliberately discarded and NEVER written to EXP004 outputs.
    # ----------------------------------------------------------------------

    with warnings.catch_warnings():

        warnings.simplefilter(
            "ignore"
        )

        sdr, _, sir, sar, _ = bss_eval(
            references,
            estimates,
            window=np.inf,
            hop=np.inf,
            compute_permutation=False,
            filters_len=512,
            framewise_filters=False,
            bsseval_sources_version=False,
        )


    sdr = np.asarray(
        sdr,
        dtype=np.float64,
    ).reshape(-1)

    sir = np.asarray(
        sir,
        dtype=np.float64,
    ).reshape(-1)

    sar = np.asarray(
        sar,
        dtype=np.float64,
    ).reshape(-1)


    if sdr.size != expected_sources:
        raise RuntimeError(
            f"Unexpected SDR result size: "
            f"{sdr.size}"
        )

    if sir.size != expected_sources:
        raise RuntimeError(
            f"Unexpected SIR result size: "
            f"{sir.size}"
        )

    if sar.size != expected_sources:
        raise RuntimeError(
            f"Unexpected SAR result size: "
            f"{sar.size}"
        )


    # ----------------------------------------------------------------------
    # SI-SDR
    #
    # Exact EXP003 approach:
    # one TorchMetrics calculation per source.
    # ----------------------------------------------------------------------

    si_sdr_values = []


    for source_index in range(
        expected_sources
    ):

        value = calculate_si_sdr(
            references[
                source_index
            ],
            estimates[
                source_index
            ],
        )

        si_sdr_values.append(
            value
        )


    si_sdr_values = np.asarray(
        si_sdr_values,
        dtype=np.float64,
    ).reshape(-1)


    if si_sdr_values.size != (
        expected_sources
    ):

        raise RuntimeError(
            "Unexpected SI-SDR result size: "
            f"{si_sdr_values.size}"
        )


    # ----------------------------------------------------------------------
    # SOURCE-LEVEL METRICS
    # ----------------------------------------------------------------------

    source_metrics = {}


    for source_index, source_name in (
        enumerate(source_names)
    ):

        sdr_value = metric_scalar(
            np.nanmean(
                sdr[
                    source_index
                ]
            )
        )

        sir_value = metric_scalar(
            np.nanmean(
                sir[
                    source_index
                ]
            )
        )

        sar_value = metric_scalar(
            np.nanmean(
                sar[
                    source_index
                ]
            )
        )

        si_sdr_value = metric_scalar(
            si_sdr_values[
                source_index
            ]
        )


        metric_values = {
            "SDR": sdr_value,
            "SIR": sir_value,
            "SAR": sar_value,
            "SI-SDR": si_sdr_value,
        }


        for metric_name, value in (
            metric_values.items()
        ):

            if not math.isfinite(
                float(value)
            ):

                raise RuntimeError(
                    "Non-finite objective metric "
                    f"for {track_name} / "
                    f"{source_name} / "
                    f"{metric_name}: {value}"
                )


        source_metrics[
            source_name
        ] = metric_values


    # ----------------------------------------------------------------------
    # TRACK-LEVEL AVERAGES
    # ----------------------------------------------------------------------

    track_average = {}


    for metric_name in [
        "SDR",
        "SIR",
        "SAR",
        "SI-SDR",
    ]:

        values = [
            source_metrics[
                source_name
            ][metric_name]

            for source_name in (
                source_names
            )
        ]


        track_average[
            metric_name
        ] = float(
            np.mean(values)
        )


    elapsed = (
        time.time()
        - started
    )


    # ----------------------------------------------------------------------
    # FINAL RESULT
    # ----------------------------------------------------------------------

    result = {
        "experiment": experiment_id,
        "track": track_name,
        "status": "success",

        "sample_rate": samplerate,

        "num_samples": int(
            references.shape[1]
        ),

        "num_channels": int(
            references.shape[2]
        ),

        "sources": source_metrics,

        "track_average": track_average,

        "elapsed_seconds": round(
            elapsed,
            3,
        ),

        "worker_pid": os.getpid(),

        "metric_policy": {
            "bsseval_version": "BSSEval v4",
            "bsseval_window": "whole_track",
            "bsseval_filters_len": 512,
            "bsseval_framewise_filters": False,
            "bsseval_compute_permutation": False,
            "si_sdr": "TorchMetrics ScaleInvariantSignalDistortionRatio",
            "excluded_metrics": ["ISR"],
        },
    }


    return result


# --------------------------------------------------------------------------
# MAIN WORKER ENTRY
# --------------------------------------------------------------------------

def main():

    if len(sys.argv) != 3:

        raise SystemExit(
            "Usage: worker.py TASK_JSON RESULT_JSON"
        )


    task_path = Path(
        sys.argv[1]
    )

    result_path = Path(
        sys.argv[2]
    )


    with open(
        task_path,
        "r",
        encoding="utf-8",
    ) as handle:

        task = json.load(
            handle
        )


    try:

        result = evaluate_track(
            task
        )


        atomic_write_json(
            result_path,
            result,
        )


        print(
            f"SUCCESS: {task['track']}"
        )

        return 0


    except BaseException as exc:

        failure = {
            "experiment": task.get(
                "experiment",
                "EXP004",
            ),

            "track": task.get(
                "track",
                "UNKNOWN",
            ),

            "status": "failed",

            "error_type": type(
                exc
            ).__name__,

            "error": str(
                exc
            ),

            "traceback": traceback_text(
                exc
            ),
        }


        try:

            atomic_write_json(
                result_path,
                failure,
            )

        except Exception:

            pass


        print(
            f"FAILED: {task.get('track', 'UNKNOWN')}",
            file=sys.stderr,
        )

        print(
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )

        return 1


def traceback_text(
    exc,
):

    import traceback

    return traceback.format_exc()


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
