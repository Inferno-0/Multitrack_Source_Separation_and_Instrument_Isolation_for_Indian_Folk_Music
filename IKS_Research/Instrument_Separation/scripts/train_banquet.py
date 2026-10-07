import os
import sys
import time
import json
import warnings
import torch
import torchaudio
import io
import csv

sys.path.append(r'C:\iks_scripts\query-bandit')
warnings.filterwarnings('ignore')

from omegaconf import OmegaConf
from torch.utils.data import DataLoader
from train import _build_model
from core.models.ebase import EndToEndLightningSystem
from core.losses.base import BaseLossHandler
from core.losses.l1snr import L1SNRLoss
from core.types import BatchedInputOutput, OperationMode

from dynamic_dataset import IKSDynamicDataset, custom_collate

def save_checkpoint(system, optimizer, step, path):
    checkpoint = {
        'state_dict': system.state_dict(),
        'optimizer': optimizer.state_dict(),
        'step': step
    }
    torch.save(checkpoint, path)

class DummyHandler(dict):
    def __init__(self):
        super().__init__()
    def __call__(self, *args, **kwargs):
        pass
    def get_mode(self, mode):
        return self

def main():
    print("CUDA Device:", torch.cuda.get_device_name(0))
    print("Total VRAM:", torch.cuda.get_device_properties(0).total_memory / (1024**3), "GB")
    
    # 1. Dataset setup
    manifest_path = r'D:\IKS_Research\Instrument_Separation\datasets\source_split_manifest.csv'
    source_dir = r'D:\ISOLATED_INSTRUMENTS_PREPARED'
    query_bank_dir = r'D:\IKS_Research\Instrument_Separation\datasets\query_bank'
    output_dir = r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_001'
    
    os.makedirs(output_dir, exist_ok=True)
    
    train_dataset = IKSDynamicDataset(
        manifest_path=manifest_path,
        source_dir=source_dir,
        query_bank_dir=query_bank_dir,
        split='TRAIN',
        num_samples=100000 # virtual infinite
    )
    
    train_loader = DataLoader(
        train_dataset, 
        batch_size=1, 
        shuffle=True, 
        collate_fn=custom_collate, 
        num_workers=0
    )
    
    # 2. Model setup
    config_path = r'C:\iks_scripts\query-bandit\config\models\bandit-query-pre.yml'
    config = OmegaConf.load(config_path)

    if 'pretrain_encoder' in config.kwargs:
        config.kwargs.pretrain_encoder = None

    class DummyConfig:
        def __init__(self, model):
            self.model = model

    root_cfg = DummyConfig(config)
    model = _build_model(root_cfg)

    ckpt_path = r'C:\iks_scripts\query-bandit\ev-pre-aug.ckpt'
    print(f"Loading pretrained weights from {ckpt_path}")
    state_dict = torch.load(ckpt_path, map_location='cpu')['state_dict']

    loss_handler = BaseLossHandler(loss=L1SNRLoss(), modality="audio", name="l1snr")

    system = EndToEndLightningSystem(
        model=model, 
        loss_handler=loss_handler, 
        metrics=DummyHandler(), 
        augmentation_handler=None, 
        inference_handler=None, 
        optimization_bundle=None
    )
    
    def mock_log_dict(*args, **kwargs):
        pass
    system.log_dict_with_prefix = mock_log_dict

    try:
        system.load_state_dict(state_dict, strict=True)
    except Exception as e:
        system.load_state_dict(state_dict, strict=False)

    system.cuda()
    system.train()
    
    optimizer = torch.optim.Adam(system.parameters(), lr=1e-4)
    
    # Check for resume
    latest_ckpt_path = os.path.join(output_dir, 'latest.ckpt')
    start_step = 0
    if os.path.exists(latest_ckpt_path):
        print(f"Resuming from {latest_ckpt_path}...")
        ckpt = torch.load(latest_ckpt_path, map_location='cpu')
        system.load_state_dict(ckpt['state_dict'])
        optimizer.load_state_dict(ckpt['optimizer'])
        start_step = ckpt['step']
    
    # 3. Training Loop
    MAX_HOURS = 8.5
    start_time = time.time()
    
    metrics_log_path = os.path.join(output_dir, 'training_metrics.csv')
    file_exists = os.path.exists(metrics_log_path)
    metrics_file = open(metrics_log_path, 'a', newline='')
    csv_writer = csv.writer(metrics_file)
    if not file_exists:
        csv_writer.writerow(['step', 'loss', 'step_time_sec'])
        
    print(f"Starting training from step {start_step}...")
    
    step = start_step
    running_loss = 0.0
    
    for batch_idx, batch_dict in enumerate(train_loader):
        # Move to GPU
        batch_dict["mixture"]["audio"] = batch_dict["mixture"]["audio"].cuda()
        batch_dict["queries"]["target"]["audio"] = batch_dict["queries"]["target"]["audio"].cuda()
        batch_dict["query"]["audio"] = batch_dict["query"]["audio"].cuda()
        batch_dict["sources"]["target"]["audio"] = batch_dict["sources"]["target"]["audio"].cuda()
        
        batch = BatchedInputOutput.from_dict(batch_dict)
        
        step_start_time = time.time()
        
        optimizer.zero_grad()
        
        try:
            loss_dict = system.common_step(batch, mode=OperationMode.TRAIN, batch_idx=step)
            loss = loss_dict['l1snr']
            
            # If target is silence (negative query), L1SNRLoss handles it? Let's check for NaN
            if torch.isnan(loss) or torch.isinf(loss):
                print(f"Step {step}: NaN loss encountered. Skipping batch.")
                continue
                
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(system.parameters(), max_norm=1.0)
            
            optimizer.step()
            
        except RuntimeError as e:
            if "out of memory" in str(e):
                print(f"OOM at step {step}. Emptying cache and skipping batch.")
                torch.cuda.empty_cache()
                continue
            else:
                raise e
        
        step_time = time.time() - step_start_time
        running_loss += loss.item()
        
        if (step + 1) % 10 == 0:
            avg_loss = running_loss / 10
            print(f"Step {step + 1} | Loss: {avg_loss:.4f} | Time/step: {step_time:.2f}s")
            csv_writer.writerow([step + 1, avg_loss, step_time])
            metrics_file.flush()
            running_loss = 0.0
            
        if (step + 1) % 100 == 0:
            save_checkpoint(system, optimizer, step + 1, latest_ckpt_path)
            
        step += 1
        
        elapsed_hours = (time.time() - start_time) / 3600.0
        if elapsed_hours >= MAX_HOURS:
            print(f"Reached time limit of {MAX_HOURS} hours. Stopping.")
            break
            
    # Save final
    save_checkpoint(system, optimizer, step, os.path.join(output_dir, 'final.ckpt'))
    metrics_file.close()
    print("Training finished.")

if __name__ == "__main__":
    main()
