import os
import sys
import torch
import csv
import json
import warnings
import time
import math
import copy
from omegaconf import OmegaConf
from torch.utils.data import DataLoader
import datetime

sys.path.append(r'C:\iks_scripts\query-bandit')
warnings.filterwarnings('ignore')

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
    if ref_energy < 1e-6: return 0.0
    optimal_scaling = torch.sum(reference * estimation) / ref_energy
    projection = optimal_scaling * reference
    noise = estimation - projection
    noise_energy = torch.sum(noise ** 2)
    if noise_energy < 1e-6: return 100.0
    return (10 * torch.log10(torch.sum(projection ** 2) / noise_energy)).item()

class DummyHandler(dict):
    def __init__(self): super().__init__()
    def __call__(self, *args, **kwargs): pass
    def get_mode(self, mode): return self
    def update(self, *args, **kwargs): pass

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
            
            sdr = compute_sdr(ref, est) if meta['is_positive'] else 0.0
            
            results.append({
                "meta": meta, "l1snr": l1snr, "sdr": sdr,
                "target_rms": target_rms, "output_rms": output_rms, "l1": l1_error
            })
            
    system.train()
    pos_l1snr = [r['l1snr'] for r in results if r['meta']['is_positive']]
    pos_sdr = [r['sdr'] for r in results if r['meta']['is_positive']]
    neg_rms = [r['output_rms'] for r in results if not r['meta']['is_positive']]
    
    mean_pos_l1snr = sum(pos_l1snr)/len(pos_l1snr) if pos_l1snr else 0.0
    mean_pos_sdr = sum(pos_sdr)/len(pos_sdr) if pos_sdr else 0.0
    mean_neg_rms = sum(neg_rms)/len(neg_rms) if neg_rms else 0.0
    max_neg_rms = max(neg_rms) if neg_rms else 0.0
    
    inst_sdr = {i: [] for i in ['tabla', 'harmonium', 'flute', 'dholak', 'dhul']}
    for r in results:
        if r['meta']['is_positive']:
            inst_sdr[r['meta']['target_instrument']].append(r['sdr'])
            
    return {
        "mean_pos_l1snr": mean_pos_l1snr,
        "mean_pos_sdr": mean_pos_sdr,
        "mean_neg_rms": mean_neg_rms,
        "max_neg_rms": max_neg_rms,
        "per_instrument_sdr": {k: (sum(v)/len(v) if v else 0.0) for k, v in inst_sdr.items()}
    }

def main():
    run_dir = r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002'
    os.makedirs(run_dir, exist_ok=True)
    
    # Run 002 state variables
    latest_ckpt_path = os.path.join(run_dir, 'latest.ckpt')
    baseline_ckpt_path = r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_001\checkpoint_step1400_backup.ckpt'
    baseline_val_json = os.path.join(run_dir, 'baseline_validation.json')
    
    is_resume = os.path.exists(latest_ckpt_path)
    
    import math

    if not os.path.isfile(baseline_val_json):
        raise RuntimeError(
            f"Required baseline file is missing: {baseline_val_json}"
        )
    
    with open(baseline_val_json, 'r', encoding='utf-8') as f:
        base_data = json.load(f)
    
    if 'CORRECTED RUN 002 BASELINE' not in base_data:
        raise RuntimeError(
            "baseline_validation.json does not contain "
            "'CORRECTED RUN 002 BASELINE'."
        )
    
    metrics = base_data['CORRECTED RUN 002 BASELINE']
    
    required_metrics = [
        'mean_pos_l1snr',
        'mean_pos_sdr',
        'mean_neg_rms',
    ]
    
    for key in required_metrics:
        if key not in metrics:
            raise RuntimeError(
                f"Missing required baseline metric: {key}"
            )
    
    best_val_metric = float(metrics['mean_pos_l1snr'])
    baseline_pos_sdr = float(metrics['mean_pos_sdr'])
    baseline_neg_rms = float(metrics['mean_neg_rms'])
    
    if not math.isfinite(best_val_metric):
        raise RuntimeError("Baseline mean_pos_l1snr is not finite.")
    
    if not math.isfinite(baseline_pos_sdr):
        raise RuntimeError("Baseline mean_pos_sdr is not finite.")
    
    if not math.isfinite(baseline_neg_rms) or baseline_neg_rms < 0:
        raise RuntimeError("Baseline mean_neg_rms is invalid.")
    
    negative_rms_limit = baseline_neg_rms * 2.0
            
    print(f"Initial Run 001 Baseline Best Metric (L1SNR): {best_val_metric:.4f}")
    
    # 1. Write comprehensive configuration JSON if not resuming
    if not is_resume:
        config_record = {
            "Run ID": "run_002",
            "Starting checkpoint": baseline_ckpt_path,
            "Starting global optimizer step": 1400,
            "Learning rate": 1e-5,
            "Optimizer": "Adam",
            "Physical batch size": 1,
            "Gradient accumulation steps": 4,
            "Effective batch size": 4,
            "Gradient clipping max_norm": 1.0,
            "Validation interval": "200 optimizer steps",
            "Validation samples": 100,
            "Positive validation samples": 75,
            "Negative validation samples": 25,
            "Early stopping patience": "5 validation intervals",
            "Early stopping equivalent": "1000 optimizer steps",
            "ReduceLROnPlateau mode": "min",
            "ReduceLROnPlateau factor": 0.5,
            "ReduceLROnPlateau patience": "2 validation intervals",
            "Minimum learning rate": 1e-7,
            "Maximum wall-clock runtime": "12 hours",
            "Training loss EMA alpha": 0.05,
            "Primary validation metric": "mean positive L1SNR",
            "Baseline mean positive L1SNR": best_val_metric,
            "Baseline mean positive SDR": baseline_pos_sdr,
            "Baseline mean negative RMS": baseline_neg_rms,
            "Loss function": "unchanged L1SNRLoss",
            "Validation manifest": "validation_manifest.json",
            "Training dataset": "dynamic on-the-fly dataset",
            "Dholak Sample - 26 exclusion": "enabled",
            "timestamp of launch": datetime.datetime.now().isoformat(),
            "exact Python executable": sys.executable,
            "PyTorch version": torch.__version__,
            "CUDA version": torch.version.cuda,
            "GPU name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None",
            "GPU memory": f"{torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB" if torch.cuda.is_available() else "None"
        }
        
        print("\n" + "="*60)
        print("RUN 002 CONFIGURATION SUMMARY")
        print("="*60)
        for k, v in config_record.items():
            print(f"{k}: {v}")
        print("="*60 + "\n")
        
        with open(os.path.join(run_dir, 'run_config.json'), 'w') as f:
            json.dump(config_record, f, indent=4)
        
    # 2. Build model and system
    config_path = r'C:\iks_scripts\query-bandit\config\models\bandit-query-pre.yml'
    config = OmegaConf.load(config_path)
    if 'pretrain_encoder' in config.kwargs: config.kwargs.pretrain_encoder = None
    class DummyConfig:
        def __init__(self, model): self.model = model
    root_cfg = DummyConfig(config)
    model = _build_model(root_cfg)

    loss_handler = BaseLossHandler(loss=L1SNRLoss(), modality="audio", name="l1snr")
    system = EndToEndLightningSystem(model=model, loss_handler=loss_handler, metrics=DummyHandler(), augmentation_handler=None, inference_handler=None, optimization_bundle=None)
    system.log_dict_with_prefix = lambda *args, **kwargs: None

    # 3. Datasets
    val_dataset = IKSValidationDataset(
        manifest_path=os.path.join(run_dir, 'validation_manifest.json'),
        source_dir=r'D:\ISOLATED_INSTRUMENTS_PREPARED'
    )
    val_loader = DataLoader(val_dataset, batch_size=1, shuffle=False, collate_fn=validation_collate, num_workers=0)
    
    train_dataset = IKSDynamicDataset(
        manifest_path=r'D:\IKS_Research\Instrument_Separation\datasets\source_split_manifest.csv',
        source_dir=r'D:\ISOLATED_INSTRUMENTS_PREPARED',
        query_bank_dir=r'D:\IKS_Research\Instrument_Separation\datasets\query_bank',
        split='TRAIN', num_samples=1000000
    )
    train_loader = DataLoader(train_dataset, batch_size=1, shuffle=True, collate_fn=custom_collate, num_workers=0)
    
    # 4. Optimizers & Schedulers
    optimizer = torch.optim.Adam(system.parameters(), lr=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=2, min_lr=1e-7)
    
    # 5. Tracking Variables
    global_step = 1400  # Default starting step
    ema_loss = None
    alpha = 0.05
    epochs_without_improvement = 0
    oom_count = 0
    accum_steps = 4
    val_interval = 200
    save_interval = 100
    patience_limit = 5
    max_hours = 12.0
    cumulative_runtime = 0.0
    
    train_metrics_file = os.path.join(run_dir, 'training_metrics.csv')
    val_metrics_file = os.path.join(run_dir, 'validation_metrics.csv')
    
    # 6. Load State
    if is_resume:
        print(f"Resuming Run 002 from {latest_ckpt_path}...")
        ckpt = torch.load(latest_ckpt_path, map_location='cpu')
        try: system.load_state_dict(ckpt['state_dict'], strict=True)
        except: system.load_state_dict(ckpt['state_dict'], strict=False)
        system.cuda()
        
        if 'optimizer' in ckpt: optimizer.load_state_dict(ckpt['optimizer'])
        if 'scheduler' in ckpt: scheduler.load_state_dict(ckpt['scheduler'])
        if 'global_step' in ckpt: global_step = ckpt['global_step']
        if 'best_val_metric' in ckpt: best_val_metric = ckpt['best_val_metric']
        if 'patience' in ckpt: epochs_without_improvement = ckpt['patience']
        if 'ema_loss' in ckpt: ema_loss = ckpt['ema_loss']
        if 'cumulative_runtime' in ckpt: cumulative_runtime = ckpt['cumulative_runtime']
        
        print(f"Resumed at step {global_step} with LR {optimizer.param_groups[0]['lr']:.2e}")
    else:
        print(f"Starting Run 002 fresh. Loading model weights from {baseline_ckpt_path}...")
        ckpt = torch.load(baseline_ckpt_path, map_location='cpu')
        try: system.load_state_dict(ckpt['state_dict'], strict=True)
        except: system.load_state_dict(ckpt['state_dict'], strict=False)
        system.cuda()
        
        with open(train_metrics_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['step', 'mean_raw_loss', 'ema_loss', 'step_time_sec', 'learning_rate', 'oom_count'])
            
        with open(val_metrics_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['step', 'mean_pos_l1snr', 'mean_pos_sdr', 'mean_neg_rms', 'max_neg_rms'])

    system.train()
    print("Starting training loop...")
    optimizer.zero_grad(set_to_none=True)
    accum_counter = 0
    microbatch_losses = []
    
    training_start_time = time.time()
    step_start_time = time.time()
    
    for batch_dict in train_loader:
        try:
            batch_dict["mixture"]["audio"] = batch_dict["mixture"]["audio"].cuda()
            batch_dict["queries"]["target"]["audio"] = batch_dict["queries"]["target"]["audio"].cuda()
            batch_dict["query"]["audio"] = batch_dict["query"]["audio"].cuda()
            batch_dict["sources"]["target"]["audio"] = batch_dict["sources"]["target"]["audio"].cuda()
            
            batch = BatchedInputOutput.from_dict(batch_dict)
            loss_dict = system.common_step(batch, mode=OperationMode.TRAIN, batch_idx=0)
            
            raw_loss = loss_dict['l1snr']
            if torch.isnan(raw_loss) or torch.isinf(raw_loss):
                print(f"NaN loss detected at global_step {global_step}. Skipping microbatch.")
                microbatch_losses.clear()
                accum_counter = 0
                optimizer.zero_grad(set_to_none=True)
                continue
                
            loss = raw_loss / accum_steps
            loss.backward()
            
            microbatch_losses.append(raw_loss.item())
            
            accum_counter += 1
            
            if accum_counter == accum_steps:
                torch.nn.utils.clip_grad_norm_(system.parameters(), max_norm=1.0)
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)
                accum_counter = 0
                global_step += 1
                
                step_time = time.time() - step_start_time
                step_start_time = time.time()
                current_lr = optimizer.param_groups[0]['lr']
                
                mean_raw_loss = sum(microbatch_losses) / len(microbatch_losses)
                microbatch_losses.clear()
                
                if ema_loss is None: ema_loss = mean_raw_loss
                else: ema_loss = alpha * mean_raw_loss + (1 - alpha) * ema_loss
                
                with open(train_metrics_file, 'a', newline='') as f:
                    csv.writer(f).writerow([global_step, mean_raw_loss, ema_loss, step_time, current_lr, oom_count])
                print(f"Step {global_step} | Loss: {mean_raw_loss:.4f} | EMA: {ema_loss:.4f} | LR: {current_lr:.2e} | Time: {step_time:.2f}s")
                
                # Check Time Limit
                step_elapsed_sec = time.time() - training_start_time
                elapsed_hours = (cumulative_runtime + step_elapsed_sec) / 3600.0
                if elapsed_hours >= max_hours:
                    print(f"Maximum training time of {max_hours} hours reached. Terminating early.")
                    state = {
                        'global_step': global_step, 'state_dict': system.state_dict(),
                        'optimizer': optimizer.state_dict(), 'scheduler': scheduler.state_dict(),
                        'best_val_metric': best_val_metric, 'patience': epochs_without_improvement, 'ema_loss': ema_loss,
                        'cumulative_runtime': cumulative_runtime + step_elapsed_sec
                    }
                    tmp_latest = latest_ckpt_path + ".tmp"
                    torch.save(state, tmp_latest)
                    os.replace(tmp_latest, latest_ckpt_path)
                    print(f"Final latest.ckpt saved at step {global_step}.")
                    return
                
                # Validation
                v_res = None
                if global_step % val_interval == 0:
                    print(f"Running validation at step {global_step}...")
                    v_res = evaluate_validation_set(system, val_loader)
                    
                    val_metric = v_res['mean_pos_l1snr']
                    neg_rms = v_res['mean_neg_rms']
                    
                    print(f"Validation: L1SNR={val_metric:.4f} | SDR={v_res['mean_pos_sdr']:.4f} dB | NegRMS={neg_rms:.6f} | LR={current_lr:.2e}")
                    
                    for inst, sdr in v_res['per_instrument_sdr'].items():
                        print(f"  {inst:10s} SDR: {sdr:>6.2f} dB")
                    
                    with open(val_metrics_file, 'a', newline='') as f:
                        csv.writer(f).writerow([global_step, val_metric, v_res['mean_pos_sdr'], neg_rms, v_res['max_neg_rms']])
                        
                    abnormal_neg_rms = neg_rms > negative_rms_limit
                    metric_improved = val_metric < best_val_metric
                    candidate_accepted = metric_improved and not abnormal_neg_rms
                    
                    if candidate_accepted:
                        scheduler_metric = val_metric
                    else:
                        scheduler_metric = best_val_metric
                    
                    scheduler.step(scheduler_metric)
                    
                    if candidate_accepted:
                        best_val_metric = val_metric
                        epochs_without_improvement = 0
                    
                        best_state = {
                            'global_step': global_step,
                            'state_dict': system.state_dict(),
                            'optimizer': optimizer.state_dict(),
                            'scheduler': scheduler.state_dict(),
                            'best_val_metric': best_val_metric,
                            'patience': epochs_without_improvement,
                            'ema_loss': ema_loss,
                            'validation_metrics': v_res,
                            'cumulative_runtime': cumulative_runtime + (time.time() - training_start_time),
                        }
                    
                        best_ckpt_path = os.path.join(run_dir, 'best.ckpt')
                        tmp_best = best_ckpt_path + '.tmp'
                    
                        torch.save(best_state, tmp_best)
                        os.replace(tmp_best, best_ckpt_path)
                    
                        print(
                            f"*** New best validation metric: "
                            f"{best_val_metric:.4f}. Saved best.ckpt."
                        )
                    
                    else:
                        if metric_improved and abnormal_neg_rms:
                            print(
                                "WARNING: Positive L1SNR improved but the "
                                "negative-query safety gate FAILED."
                            )
                            print(
                                f"    Previous best L1SNR: {best_val_metric:.6f}"
                            )
                            print(
                                f"    Candidate L1SNR: {val_metric:.6f}"
                            )
                            print(
                                f"    Baseline negative RMS: {baseline_neg_rms:.6f}"
                            )
                            print(
                                f"    Candidate negative RMS: {neg_rms:.6f}"
                            )
                            print(
                                f"    Safety limit: {negative_rms_limit:.6f}"
                            )
                            print(
                                "    Candidate REJECTED. "
                                "best_val_metric unchanged."
                            )
                    
                        epochs_without_improvement += 1
                    
                        print(
                            f"Validation candidate rejected/non-improving. "
                            f"Patience: "
                            f"{epochs_without_improvement}/{patience_limit}"
                        )
                    
                    if epochs_without_improvement >= patience_limit:
                        print(f"EARLY STOPPING triggered at step {global_step}.")
                        final_state = {
                            'global_step': global_step, 'state_dict': system.state_dict(),
                            'optimizer': optimizer.state_dict(), 'scheduler': scheduler.state_dict(),
                            'best_val_metric': best_val_metric, 'patience': epochs_without_improvement, 'ema_loss': ema_loss,
                            'validation_metrics': v_res,
                            'cumulative_runtime': cumulative_runtime + (time.time() - training_start_time)
                        }
                        tmp_latest = latest_ckpt_path + ".tmp"
                        torch.save(final_state, tmp_latest)
                        os.replace(tmp_latest, latest_ckpt_path)
                        print(f"Final latest.ckpt saved.")
                        return
                            
                # Periodic Checkpoint (Moved AFTER validation to ensure state is completely up-to-date)
                if global_step % save_interval == 0:
                    state = {
                        'global_step': global_step, 'state_dict': system.state_dict(),
                        'optimizer': optimizer.state_dict(), 'scheduler': scheduler.state_dict(),
                        'best_val_metric': best_val_metric, 'patience': epochs_without_improvement, 'ema_loss': ema_loss,
                        'validation_metrics': v_res if 'v_res' in locals() and v_res else None,
                        'cumulative_runtime': cumulative_runtime + (time.time() - training_start_time)
                    }
                    tmp_latest = latest_ckpt_path + ".tmp"
                    torch.save(state, tmp_latest)
                    os.replace(tmp_latest, latest_ckpt_path)
                    print(f"Saved periodic latest.ckpt at step {global_step}.")
                
        except RuntimeError as e:
            if "out of memory" in str(e):
                oom_count += 1
                print("OOM error! Clearing cache and skipping microbatch.")
                torch.cuda.empty_cache()
                optimizer.zero_grad(set_to_none=True)
                accum_counter = 0 
                microbatch_losses.clear() 
            else:
                raise e

if __name__ == "__main__":
    main()
