import os
import sys
import torch
import torchaudio
import io
import warnings
import math

sys.path.append(r'C:\iks_scripts\query-bandit')
warnings.filterwarnings('ignore')

from omegaconf import OmegaConf
from train import _build_model
from core.models.ebase import EndToEndLightningSystem
from torch_audiomentations.utils.object_dict import ObjectDict
from core.types import BatchedInputOutput

def load_system(ckpt_path):
    config_path = r'C:\iks_scripts\query-bandit\config\models\bandit-query-pre.yml'
    config = OmegaConf.load(config_path)

    if 'pretrain_encoder' in config.kwargs:
        config.kwargs.pretrain_encoder = None

    class DummyConfig:
        def __init__(self, model):
            self.model = model

    root_cfg = DummyConfig(config)
    model = _build_model(root_cfg)

    state_dict = torch.load(ckpt_path, map_location='cpu')['state_dict']

    system = EndToEndLightningSystem(
        model=model, 
        loss_handler=None, 
        metrics=None, 
        augmentation_handler=None, 
        inference_handler=None, 
        optimization_bundle=None
    )

    try:
        system.load_state_dict(state_dict, strict=True)
    except Exception:
        system.load_state_dict(state_dict, strict=False)

    system.cuda()
    system.eval()
    return system

def load_audio(path, expected_samples, sample_rate=44100):
    with open(path, 'rb') as f:
        waveform, sr = torchaudio.load(io.BytesIO(f.read()), format="wav")
    if sr != sample_rate:
        raise ValueError(f"Expected sr {sample_rate}, got {sr}")
        
    if waveform.shape[0] == 1:
        waveform = waveform.repeat(2, 1)
    elif waveform.shape[0] > 2:
        waveform = waveform[:2, :]
        
    length = waveform.shape[1]
    if length < expected_samples:
        pad = expected_samples - length
        waveform = torch.nn.functional.pad(waveform, (0, pad))
    elif length > expected_samples:
        waveform = waveform[:, :expected_samples]
        
    return waveform

def compute_sdr(reference, estimation):
    reference = reference - torch.mean(reference)
    estimation = estimation - torch.mean(estimation)
    
    ref_energy = torch.sum(reference ** 2)
    
    if ref_energy < 1e-6:
        return 0.0 # Silence target
        
    optimal_scaling = torch.sum(reference * estimation) / ref_energy
    projection = optimal_scaling * reference
    noise = estimation - projection
    
    noise_energy = torch.sum(noise ** 2)
    if noise_energy < 1e-6:
        return 100.0 # Perfect
        
    sdr = 10 * torch.log10(torch.sum(projection ** 2) / noise_energy)
    return sdr.item()

@torch.no_grad()
def main():
    print("Evaluating Cascade...")
    ckpt_path = r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_001\latest.ckpt'
    if not os.path.exists(ckpt_path):
        print(f"Checkpoint not found: {ckpt_path}")
        return
        
    system = load_system(ckpt_path)
    
    chunk_size = int(6.0 * 44100)
    query_size = int(10.0 * 44100)
    
    pilot_dir = r'D:\IKS_Research\Instrument_Separation\mixtures\pilot'
    
    test_cases = [
        {"id": "000", "target": "Tabla"},
        {"id": "001", "target": "Harmonium"},
        {"id": "017", "target": "Dholak"}
    ]
    
    results = []
    
    for tc in test_cases:
        p_path = os.path.join(pilot_dir, f"pilot_{tc['id']}")
        
        mix_audio = load_audio(os.path.join(p_path, "htdemucs_accompaniment_pred.wav"), chunk_size).unsqueeze(0).cuda()
        q_audio = load_audio(os.path.join(p_path, "query.wav"), query_size).unsqueeze(0).cuda()
        inst_name = tc["target"].lower()
        target_audio = load_audio(os.path.join(p_path, "stems", f"{inst_name}.wav"), chunk_size).unsqueeze(0).cuda()
        
        batch_dict = {
            "mixture": {"audio": mix_audio},
            "queries": {"target": {"audio": q_audio}},
            "query": {"audio": q_audio},
            "sources": {"target": {"audio": target_audio}},
            "estimates": {}
        }
        
        out = system(BatchedInputOutput.from_dict(batch_dict))
        est = out.estimates.target.audio
        
        rms = torch.sqrt(torch.mean(est ** 2)).item()
        target_rms = torch.sqrt(torch.mean(target_audio ** 2)).item()
        
        sdr = compute_sdr(target_audio[0], est[0])
        l1_error = torch.mean(torch.abs(target_audio[0] - est[0])).item()
        
        results.append({
            "pilot": tc["id"],
            "target": tc["target"],
            "rms": rms,
            "target_rms": target_rms,
            "sdr": sdr,
            "l1": l1_error
        })
        
    print("\n--- STANDARD TESTS ---")
    for r in results:
        print(f"Pilot {r['pilot']} ({r['target']:10s}): SDR={r['sdr']:>6.2f} dB, L1={r['l1']:.4f}, RMS={r['rms']:.4f} (Target={r['target_rms']:.4f})")
        
    print("\n--- NEGATIVE QUERY TEST ---")
    # pilot_000 (Tabla target, Vocals+Tabla+Harmonium+Dholak+Dhul) + Flute Query (from 016)
    p_path = os.path.join(pilot_dir, "pilot_000")
    mix_audio = load_audio(os.path.join(p_path, "htdemucs_accompaniment_pred.wav"), chunk_size).unsqueeze(0).cuda()
    q_audio = load_audio(os.path.join(pilot_dir, "pilot_016", "query.wav"), query_size).unsqueeze(0).cuda() # Flute query
    
    batch_dict = {
            "mixture": {"audio": mix_audio},
            "queries": {"target": {"audio": q_audio}},
            "query": {"audio": q_audio},
            "sources": {"target": {"audio": torch.zeros_like(mix_audio)}}, # Silence
            "estimates": {}
    }
    out = system(BatchedInputOutput.from_dict(batch_dict))
    est = out.estimates.target.audio
    rms = torch.sqrt(torch.mean(est ** 2)).item()
    print(f"Negative Query (Flute on Pilot 000) Output RMS: {rms:.6f}")
    
    print("\n--- SENSITIVITY TEST ---")
    # pilot_000 + Harmonium Query (from 001)
    q_audio_harm = load_audio(os.path.join(pilot_dir, "pilot_001", "query.wav"), query_size).unsqueeze(0).cuda()
    batch_dict["queries"]["target"]["audio"] = q_audio_harm
    batch_dict["query"]["audio"] = q_audio_harm
    
    out_harm = system(BatchedInputOutput.from_dict(batch_dict))
    est_harm = out_harm.estimates.target.audio
    
    diff = torch.abs(est - est_harm)
    mean_diff = torch.mean(diff).item()
    print(f"Mean Abs Difference (Flute vs Harmonium query on Pilot 000): {mean_diff:.6f}")
    
if __name__ == "__main__":
    main()
