import os
import torch
import torchaudio

pilot_dir = r'D:\IKS_Research\Instrument_Separation\mixtures\pilot'
subdirs = [d for d in os.listdir(pilot_dir) if d.startswith('pilot_')]

print("=== HT-Demucs Cascade Verification ===")

for d in sorted(subdirs):
    ex_dir = os.path.join(pilot_dir, d)
    acc_path = os.path.join(ex_dir, 'htdemucs_accompaniment_pred.wav')
    voc_path = os.path.join(ex_dir, 'htdemucs_vocals_pred.wav')
    
    if not os.path.exists(acc_path) or not os.path.exists(voc_path):
        print(f"FAILED: Missing files in {d}")
        continue
        
    try:
        acc, sr = torchaudio.load(acc_path)
        voc, sr2 = torchaudio.load(voc_path)
        
        # checks
        assert sr == 44100
        assert sr2 == 44100
        assert torch.isfinite(acc).all()
        assert torch.isfinite(voc).all()
        assert acc.shape[1] > 0
        assert acc.shape[0] == 1 # mono
        assert acc.shape[1] == int(6.0 * 44100) # 264600 samples
        
        acc_rms = torch.sqrt(torch.mean(acc**2)).item()
        acc_peak = torch.max(torch.abs(acc)).item()
        
        print(f"[{d}] VERIFIED. SR=44100, C=1, Dur=6.0s, Acc_RMS={acc_rms:.5f}, Acc_Peak={acc_peak:.5f}")
        if acc_rms < 1e-5:
            print(f"ANOMALY: {d} accompaniment is almost silent!")
    except Exception as e:
        print(f"FAILED {d}: {e}")

print("Verification complete.")
