import os
import json
import hashlib
import sys
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

def get_hash(path):
    h = hashlib.sha256()
    if os.path.exists(path):
        with open(path, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    return None

def main():
    failures = []
    
    # 1. Verify exact model
    best_ckpt = r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\best.ckpt'
    if not os.path.exists(best_ckpt): failures.append("best.ckpt missing")
    best_hash = get_hash(best_ckpt)
    expected_hash = "7f2415e71a7ec26247f3d9cbb620940a65f54bcdb310e4f1c74f0918673c3167"
    if best_hash != expected_hash: failures.append("best.ckpt hash modified")
    
    # 2. Verify independent TEST dataset
    test_manifest_path = r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\test_evaluation\test_manifest.json'
    inv_path = r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\test_inventory.csv'
    
    inv_df = pd.read_csv(inv_path)
    if not (inv_df['split'] == 'TEST').all(): failures.append("Not all TEST files are TEST split")
    test_files_allowed = set(inv_df['prepared_filename'])
    
    with open(test_manifest_path, 'r', encoding='utf-8') as f:
        test_samples = json.load(f)
        
    for s in test_samples:
        if s['query']['file'] not in test_files_allowed: failures.append("TEST query uses non-TEST file")
        for mix in s['mixture_sources']:
            if mix['file'] not in test_files_allowed: failures.append("TEST mix uses non-TEST file")
            
    # Check overlap and lengths
    for s in test_samples:
        if s['is_positive']:
            for mix in s['mixture_sources']:
                if mix['instrument'] == s['target_instrument']:
                    if mix['file'] == s['query']['file']:
                        # positive same file: ensure >= 16s
                        row = inv_df[inv_df['prepared_filename'] == mix['file']].iloc[0]
                        if row['duration'] < 15.9:
                            failures.append("Positive same-file has <16s duration, overlap possible")
    
    # 3. Determinism check
    # We already verified it exactly in previous step, but let's re-verify
    res_run002 = pd.read_csv(r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\test_evaluation\run002_aggregate.csv')
    res_det = pd.read_csv(r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\test_evaluation\run002_determinism_check_aggregate.csv')
    
    tol = 1e-4
    for col in res_run002.columns:
        diff = abs(res_run002.iloc[0][col] - res_det.iloc[0][col])
        if diff > tol: failures.append(f"Determinism failed for {col}")
        
    # Check hashes of files
    hashes = {
        "final training executable (train_banquet_v2.py)": get_hash(r'D:\IKS_Research\Instrument_Separation\scripts\train_banquet_v2.py'),
        "final evaluation executable (evaluate_run002_test.py)": get_hash(r'D:\IKS_Research\Instrument_Separation\scripts\evaluate_run002_test.py'),
        "fixed validation manifest": get_hash(r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\validation_manifest.json'),
        "TEST manifest": get_hash(test_manifest_path),
        "Run 001 baseline checkpoint": get_hash(r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_001\checkpoint_step1400_backup.ckpt'),
        "Run 002 best checkpoint": best_hash,
        "Run 002 TEST baseline metrics": get_hash(r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\test_evaluation\baseline_aggregate.csv'),
        "Run 002 TEST run002 metrics": get_hash(r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\test_evaluation\run002_aggregate.csv')
    }
    
    print("HASHES:")
    for k, v in hashes.items():
        print(f"{k}: {v}")
        
    if not failures:
        print("\nFINAL STATUS: PASS")
        print("RESEARCH RESULTS LOCKED: YES")
        print("TRAINING MODIFICATION REQUIRED: NO")
        print("FURTHER TRAINING AUTHORIZED: NO")
        print("TEST RESULTS SCIENTIFICALLY REPORTABLE: YES")
    else:
        print("\nFINAL STATUS: FAIL")
        for f in failures:
            print(f"- {f}")

if __name__ == "__main__":
    main()
