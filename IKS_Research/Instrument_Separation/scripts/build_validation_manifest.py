import os
import csv
import json
import random

def build_validation_manifest():
    manifest_path = r'D:\IKS_Research\Instrument_Separation\datasets\source_split_manifest.csv'
    output_dir = r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002'
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 'validation_manifest.json')
    
    # deterministic seed
    random.seed(42)
    
    val_sources = {}
    with open(manifest_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['split'] == 'VALIDATION':
                inst = row['instrument']
                if inst not in val_sources:
                    val_sources[inst] = []
                val_sources[inst].append(row['prepared_filename'])
                
    instruments = ['tabla', 'harmonium', 'flute', 'dholak', 'dhul']
    vocals = 'vocals'
    
    val_samples = []
    sample_id = 0
    
    # 20 samples per instrument: 15 positive, 5 negative
    for target_inst in instruments:
        for i in range(20):
            is_positive = i < 15
            
            # Select 1 to 4 other instruments
            num_others = random.randint(1, 4)
            pool = [x for x in instruments if x != target_inst]
            num_others = min(num_others, len(pool))
            selected_insts = random.sample(pool, num_others)
            
            if is_positive:
                selected_insts.append(target_inst)
                
            selected_insts.append(vocals)
            
            mixture_sources = []
            target_source_file = None
            
            for inst in selected_insts:
                if len(val_sources[inst]) == 0:
                    continue
                src_file = random.choice(val_sources[inst])
                gain = 10 ** (random.uniform(-3, 3) / 20.0)
                mixture_sources.append({
                    "instrument": inst,
                    "file": src_file,
                    "gain": gain
                })
                if inst == target_inst:
                    target_source_file = src_file
            
            # Query source
            # Must be from VALIDATION, preferably different from target_source_file
            if len(val_sources[target_inst]) > 1:
                q_candidates = [x for x in val_sources[target_inst] if x != target_source_file]
                if not q_candidates:
                    q_candidates = val_sources[target_inst]
                query_file = random.choice(q_candidates)
            else:
                query_file = val_sources[target_inst][0]
                
            val_samples.append({
                "id": f"val_{sample_id:03d}",
                "target_instrument": target_inst,
                "is_positive": is_positive,
                "mixture_sources": mixture_sources,
                "query": {
                    "instrument": target_inst,
                    "file": query_file
                }
            })
            sample_id += 1
            
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(val_samples, f, indent=4)
        
    print(f"Generated {len(val_samples)} validation samples at {out_path}")
    
if __name__ == "__main__":
    build_validation_manifest()
