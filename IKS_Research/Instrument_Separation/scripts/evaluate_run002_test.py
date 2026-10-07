import os
import sys
import json
import torch
import hashlib
import pandas as pd
from collections import defaultdict
import soundfile as sf
import warnings
from omegaconf import OmegaConf
from torch.utils.data import DataLoader

sys.path.append(r'C:\iks_scripts\query-bandit')
warnings.filterwarnings('ignore')

from train import _build_model
from core.models.ebase import EndToEndLightningSystem
from core.losses.base import BaseLossHandler
from core.losses.l1snr import L1SNRLoss
from core.types import BatchedInputOutput, OperationMode

sys.path.append(r'D:\IKS_Research\Instrument_Separation\scripts')
from fixed_validation_dataset import IKSValidationDataset, validation_collate

class DummyHandler(dict):
    def __init__(self): super().__init__()
    def __call__(self, *args, **kwargs): pass
    def get_mode(self, mode): return self
    def update(self, *args, **kwargs): pass

def compute_sdr(reference, estimation):
    reference = reference - torch.mean(reference)
    estimation = estimation - torch.mean(estimation)
    ref_energy = torch.sum(reference ** 2)
    if ref_energy < 1e-6: return 0.0
    optimal_scaling = torch.sum(reference * estimation) / ref_energy
    projection = optimal_scaling * reference
    noise = estimation - projection
    noise_energy = torch.sum(noise ** 2)
    if noise_energy < 1e-6: return 100.0
    return (10 * torch.log10(torch.sum(projection ** 2) / noise_energy)).item()

def get_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def evaluate_validation_set(system, val_loader, out_audio_dir):
    system.eval()
    results = []
    
    # Track saved audio so we only save 1 representative example per instrument
    saved_insts = set()
    
    with torch.no_grad():
        for batch_idx, batch_dict in enumerate(val_loader):
            batch_dict["mixture"]["audio"] = batch_dict["mixture"]["audio"].cuda()
            batch_dict["queries"]["target"]["audio"] = batch_dict["queries"]["target"]["audio"].cuda()
            batch_dict["query"]["audio"] = batch_dict["query"]["audio"].cuda()
            batch_dict["sources"]["target"]["audio"] = batch_dict["sources"]["target"]["audio"].cuda()
            
            meta = batch_dict["meta"][0]
            batch = BatchedInputOutput.from_dict(batch_dict)
            loss_dict = system.common_step(batch, mode=OperationMode.VAL, batch_idx=0)
            
            l1snr = loss_dict['l1snr'].item()
            est = batch.estimates.target.audio[0]
            ref = batch.sources.target.audio[0]
            mix = batch.mixture.audio[0]
            qry = batch.query.audio[0]
            
            target_rms = torch.sqrt(torch.mean(ref ** 2)).item()
            output_rms = torch.sqrt(torch.mean(est ** 2)).item()
            l1_error = torch.mean(torch.abs(ref - est)).item()
            
            sdr = compute_sdr(ref, est) if meta['is_positive'] else 0.0
            
            results.append({
                "meta": meta, "l1snr": l1snr, "sdr": sdr,
                "target_rms": target_rms, "output_rms": output_rms, "l1": l1_error
            })
            
            # Save qualitative audio outputs
            inst = meta['target_instrument']
            if inst not in saved_insts:
                saved_insts.add(inst)
                os.makedirs(out_audio_dir, exist_ok=True)
                # Save tensors to WAV
                est_np = est.cpu().numpy().T
                ref_np = ref.cpu().numpy().T
                mix_np = mix.cpu().numpy().T
                qry_np = qry.cpu().numpy().T
                sf.write(os.path.join(out_audio_dir, f"{inst}_estimated.wav"), est_np, 44100)
                sf.write(os.path.join(out_audio_dir, f"{inst}_reference.wav"), ref_np, 44100)
                sf.write(os.path.join(out_audio_dir, f"{inst}_mixture.wav"), mix_np, 44100)
                sf.write(os.path.join(out_audio_dir, f"{inst}_query.wav"), qry_np, 44100)
                
    pos_l1snr = [r['l1snr'] for r in results if r['meta']['is_positive']]
    pos_sdr = [r['sdr'] for r in results if r['meta']['is_positive']]
    neg_rms = [r['output_rms'] for r in results if not r['meta']['is_positive']]
    
    mean_pos_l1snr = sum(pos_l1snr)/len(pos_l1snr) if pos_l1snr else 0.0
    mean_pos_sdr = sum(pos_sdr)/len(pos_sdr) if pos_sdr else 0.0
    mean_neg_rms = sum(neg_rms)/len(neg_rms) if neg_rms else 0.0
    max_neg_rms = max(neg_rms) if neg_rms else 0.0
    
    inst_sdr = {i: [] for i in ['tabla', 'harmonium', 'flute', 'dholak', 'dhul']}
    inst_l1snr = {i: [] for i in ['tabla', 'harmonium', 'flute', 'dholak', 'dhul']}
    inst_neg_rms = {i: [] for i in ['tabla', 'harmonium', 'flute', 'dholak', 'dhul']}
    
    for r in results:
        inst = r['meta']['target_instrument']
        if r['meta']['is_positive']:
            inst_sdr[inst].append(r['sdr'])
            inst_l1snr[inst].append(r['l1snr'])
        else:
            inst_neg_rms[inst].append(r['output_rms'])
            
    inst_metrics = []
    for inst in ['tabla', 'harmonium', 'flute', 'dholak', 'dhul']:
        if inst_sdr[inst] or inst_neg_rms[inst]:
            inst_metrics.append({
                "instrument": inst,
                "pos_l1snr": sum(inst_l1snr[inst])/len(inst_l1snr[inst]) if inst_l1snr[inst] else float('nan'),
                "pos_sdr": sum(inst_sdr[inst])/len(inst_sdr[inst]) if inst_sdr[inst] else float('nan'),
                "neg_rms": sum(inst_neg_rms[inst])/len(inst_neg_rms[inst]) if inst_neg_rms[inst] else float('nan'),
                "pos_count": len(inst_l1snr[inst]),
                "neg_count": len(inst_neg_rms[inst])
            })
            
    return {
        "mean_pos_l1snr": mean_pos_l1snr,
        "mean_pos_sdr": mean_pos_sdr,
        "mean_neg_rms": mean_neg_rms,
        "max_neg_rms": max_neg_rms,
        "pos_count": len(pos_l1snr),
        "neg_count": len(neg_rms)
    }, inst_metrics

def evaluate_checkpoint(ckpt_path, test_manifest_path, isolated_dir, device, output_dir, prefix):
    print(f"\n--- EVALUATING {prefix} ---")
    hash_before = get_hash(ckpt_path)
    
    dataset = IKSValidationDataset(test_manifest_path, isolated_dir)
    dataloader = DataLoader(dataset, batch_size=1, collate_fn=validation_collate, shuffle=False)
    
    config_path = r'C:\iks_scripts\query-bandit\config\models\bandit-query-pre.yml'
    config = OmegaConf.load(config_path)
    if 'pretrain_encoder' in config.kwargs: config.kwargs.pretrain_encoder = None
    class DummyConfig:
        def __init__(self, model): self.model = model
    root_cfg = DummyConfig(config)
    model = _build_model(root_cfg)

    loss_handler = BaseLossHandler(loss=L1SNRLoss(), modality="audio", name="l1snr")
    system = EndToEndLightningSystem(model=model, loss_handler=loss_handler, metrics=DummyHandler(), augmentation_handler=None, inference_handler=None, optimization_bundle=None)
    system = system.to(device)
    
    ckpt = torch.load(ckpt_path, map_location=device)
    system.load_state_dict(ckpt['state_dict'], strict=False)
    
    out_audio_dir = os.path.join(output_dir, "audio", prefix)
    agg, inst_mets = evaluate_validation_set(system, dataloader, out_audio_dir)
                             
    hash_after = get_hash(ckpt_path)
    assert hash_before == hash_after, "Checkpoint was modified during evaluation!"
    
    pd.DataFrame([agg]).to_csv(os.path.join(output_dir, f"{prefix}_aggregate.csv"), index=False)
    pd.DataFrame(inst_mets).to_csv(os.path.join(output_dir, f"{prefix}_instruments.csv"), index=False)
    
    return agg, inst_mets

def main():
    torch.manual_seed(42)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    test_manifest_path = r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\test_evaluation\test_manifest.json'
    isolated_dir = r'D:\ISOLATED_INSTRUMENTS_PREPARED'
    output_dir = r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\test_evaluation'
    
    # 1. Evaluate baseline
    baseline_ckpt = r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_001\checkpoint_step1400_backup.ckpt'
    evaluate_checkpoint(baseline_ckpt, test_manifest_path, isolated_dir, device, output_dir, "baseline")
    
    # 2. Evaluate Run 002
    run002_ckpt = r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\best.ckpt'
    evaluate_checkpoint(run002_ckpt, test_manifest_path, isolated_dir, device, output_dir, "run002")
    
    # 3. Repeat Run 002 evaluation to prove determinism
    agg1, inst1 = evaluate_checkpoint(run002_ckpt, test_manifest_path, isolated_dir, device, output_dir, "run002_determinism_check")
    
    # Check exact equality for aggregate metrics to verify determinism
    df_run002 = pd.read_csv(os.path.join(output_dir, "run002_aggregate.csv"))
    df_det = pd.read_csv(os.path.join(output_dir, "run002_determinism_check_aggregate.csv"))
    
    # Tolerance for GPU operations
    tol = 1e-4
    for col in df_run002.columns:
        diff = abs(df_run002.iloc[0][col] - df_det.iloc[0][col])
        assert diff < tol, f"Determinism failure for {col}: diff={diff}"
    
    print("\nTEST EVALUATION COMPLETED SUCCESSFULLY. DETERMINISM VERIFIED.")

if __name__ == '__main__':
    main()
