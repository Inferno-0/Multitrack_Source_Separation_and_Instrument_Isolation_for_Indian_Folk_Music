import os
import sys
import torch
import warnings
import math
import copy
import json

sys.path.append(r'C:\iks_scripts\query-bandit')
warnings.filterwarnings('ignore')

from omegaconf import OmegaConf
from torch.utils.data import DataLoader
from train import _build_model
from core.models.ebase import EndToEndLightningSystem
from core.losses.base import BaseLossHandler
from core.losses.l1snr import L1SNRLoss
from core.types import BatchedInputOutput, OperationMode

from fixed_validation_dataset import IKSValidationDataset, validation_collate
from dynamic_dataset import IKSDynamicDataset, custom_collate

def compute_sdr(reference, estimation):
    reference = reference - torch.mean(reference)
    estimation = estimation - torch.mean(estimation)
    ref_energy = torch.sum(reference ** 2)
    if ref_energy < 1e-6:
        return 0.0
    optimal_scaling = torch.sum(reference * estimation) / ref_energy
    projection = optimal_scaling * reference
    noise = estimation - projection
    noise_energy = torch.sum(noise ** 2)
    if noise_energy < 1e-6:
        return 100.0
    sdr = 10 * torch.log10(torch.sum(projection ** 2) / noise_energy)
    return sdr.item()

def evaluate_validation_set(system, val_loader):
    system.eval()
    results = []
    
    with torch.no_grad():
        for batch_dict in val_loader:
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
            
            target_rms = torch.sqrt(torch.mean(ref ** 2)).item()
            output_rms = torch.sqrt(torch.mean(est ** 2)).item()
            l1_error = torch.mean(torch.abs(ref - est)).item()
            
            if meta['is_positive']:
                sdr = compute_sdr(ref, est)
            else:
                sdr = 0.0
                
            results.append({
                "meta": meta,
                "l1snr": l1snr,
                "sdr": sdr,
                "target_rms": target_rms,
                "output_rms": output_rms,
                "l1": l1_error
            })
            
    system.train()
    
    # Aggregate
    pos_l1snr = []
    pos_sdr = []
    neg_rms = []
    inst_sdr = {i: [] for i in ['tabla', 'harmonium', 'flute', 'dholak', 'dhul']}
    
    for r in results:
        m = r['meta']
        if m['is_positive']:
            pos_l1snr.append(r['l1snr'])
            pos_sdr.append(r['sdr'])
            inst_sdr[m['target_instrument']].append(r['sdr'])
        else:
            neg_rms.append(r['output_rms'])
            
    mean_pos_l1snr = sum(pos_l1snr)/len(pos_l1snr) if pos_l1snr else 0.0
    mean_pos_sdr = sum(pos_sdr)/len(pos_sdr) if pos_sdr else 0.0
    mean_neg_rms = sum(neg_rms)/len(neg_rms) if neg_rms else 0.0
    
    print("\n--- VALIDATION RESULTS ---")
    print(f"Mean Positive L1SNR: {mean_pos_l1snr:.4f}")
    print(f"Mean Positive SDR:   {mean_pos_sdr:.4f} dB")
    print(f"Mean Negative RMS:   {mean_neg_rms:.6f}")
    
    for inst, sdrs in inst_sdr.items():
        if sdrs:
            print(f"  {inst:10s} Mean SDR: {sum(sdrs)/len(sdrs):>6.2f} dB")
            
    return {
        "mean_pos_l1snr": mean_pos_l1snr,
        "mean_pos_sdr": mean_pos_sdr,
        "mean_neg_rms": mean_neg_rms,
        "per_instrument_sdr": {k: (sum(v)/len(v) if v else 0.0) for k, v in inst_sdr.items()}
    }

class DummyHandler(dict):
    def __init__(self):
        super().__init__()
    def __call__(self, *args, **kwargs):
        pass
    def get_mode(self, mode):
        return self
    def update(self, *args, **kwargs):
        pass

def main():
    print("--- PRE-FLIGHT CHECK FOR RUN 002 ---")
    
    ckpt_path = r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_001\checkpoint_step1400_backup.ckpt'
    if not os.path.exists(ckpt_path):
        # The user actually preserved 'latest.ckpt' in run_001. We need to check if the backup exists.
        old_latest = r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_001\latest.ckpt'
        if os.path.exists(old_latest):
            import shutil
            shutil.copy2(old_latest, ckpt_path)
            print("Copied latest.ckpt to checkpoint_step1400_backup.ckpt")
        else:
            print("ERROR: Base checkpoint not found!")
            return

    # Load Model
    config_path = r'C:\iks_scripts\query-bandit\config\models\bandit-query-pre.yml'
    config = OmegaConf.load(config_path)
    if 'pretrain_encoder' in config.kwargs:
        config.kwargs.pretrain_encoder = None
    class DummyConfig:
        def __init__(self, model):
            self.model = model
    root_cfg = DummyConfig(config)
    model = _build_model(root_cfg)

    loss_handler = BaseLossHandler(loss=L1SNRLoss(), modality="audio", name="l1snr")
    system = EndToEndLightningSystem(
        model=model, 
        loss_handler=loss_handler, 
        metrics=DummyHandler(), 
        augmentation_handler=None, 
        inference_handler=None, 
        optimization_bundle=None
    )
    system.log_dict_with_prefix = lambda *args, **kwargs: None

    print(f"Loading checkpoint {ckpt_path}...")
    ckpt = torch.load(ckpt_path, map_location='cpu')
    try:
        system.load_state_dict(ckpt['state_dict'], strict=True)
    except Exception as e:
        system.load_state_dict(ckpt['state_dict'], strict=False)
    system.cuda()
    
    # Create DataLoaders
    val_dataset = IKSValidationDataset(
        manifest_path=r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\validation_manifest.json',
        source_dir=r'D:\ISOLATED_INSTRUMENTS_PREPARED'
    )
    val_loader = DataLoader(val_dataset, batch_size=1, shuffle=False, collate_fn=validation_collate, num_workers=0)
    
    train_dataset = IKSDynamicDataset(
        manifest_path=r'D:\IKS_Research\Instrument_Separation\datasets\source_split_manifest.csv',
        source_dir=r'D:\ISOLATED_INSTRUMENTS_PREPARED',
        query_bank_dir=r'D:\IKS_Research\Instrument_Separation\datasets\query_bank',
        split='TRAIN',
        num_samples=100
    )
    train_loader = DataLoader(train_dataset, batch_size=1, shuffle=True, collate_fn=custom_collate, num_workers=0)
    
    print("Evaluating Baseline Step 1400 on Fixed Validation Set...")
    baseline_metrics = evaluate_validation_set(system, val_loader)
    
    # Save baseline metrics
    with open(r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\baseline_validation.json', 'w') as f:
        json.dump(baseline_metrics, f, indent=4)
        
    print("\nTesting Training Microbatches with Gradient Accumulation (4)...")
    
    optimizer = torch.optim.Adam(system.parameters(), lr=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=2, min_lr=1e-7)
    
    system.train()
    optimizer.zero_grad(set_to_none=True)
    accum_steps = 4
    
    train_iter = iter(train_loader)
    for i in range(accum_steps):
        batch_dict = next(train_iter)
        batch_dict["mixture"]["audio"] = batch_dict["mixture"]["audio"].cuda()
        batch_dict["queries"]["target"]["audio"] = batch_dict["queries"]["target"]["audio"].cuda()
        batch_dict["query"]["audio"] = batch_dict["query"]["audio"].cuda()
        batch_dict["sources"]["target"]["audio"] = batch_dict["sources"]["target"]["audio"].cuda()
        
        batch = BatchedInputOutput.from_dict(batch_dict)
        loss_dict = system.common_step(batch, mode=OperationMode.TRAIN, batch_idx=0)
        
        loss = loss_dict['l1snr'] / accum_steps
        loss.backward()
        print(f"  Microbatch {i+1} backward passed. Loss (scaled): {loss.item():.4f}")
        
    torch.nn.utils.clip_grad_norm_(system.parameters(), max_norm=1.0)
    optimizer.step()
    print("  Optimizer step successful!")
    
    # Check scheduler step
    scheduler.step(baseline_metrics['mean_pos_l1snr'])
    print(f"  Scheduler stepped with metric {baseline_metrics['mean_pos_l1snr']:.4f}")
    
    print("Pre-flight checks passed.")
    
if __name__ == "__main__":
    main()
