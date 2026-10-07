import pandas as pd
import json
import random
import os

random.seed(42)

manifest_path = r'D:\IKS_Research\Instrument_Separation\datasets\source_split_manifest.csv'
df = pd.read_csv(manifest_path)

def get_abs_path(row):
    # Added audio/ subdirectory
    return os.path.join(r'D:\ISOLATED_INSTRUMENTS_PREPARED', row['instrument'], 'audio', row['prepared_filename'])

test_df = df[(df['split'] == 'TEST') & (df['instrument'] != 'other')].copy()

instruments = ['vocals', 'tabla', 'harmonium', 'flute', 'dholak', 'dhul']
pool = {inst: test_df[test_df['instrument'] == inst] for inst in instruments}
pool['dholak'] = pool['dholak'][~pool['dholak']['original_filename'].str.contains('26', na=False)]

queries_pool = {inst: test_df[test_df['instrument'] == inst].copy() for inst in ['tabla', 'harmonium', 'flute', 'dholak', 'dhul']}
queries_pool['dholak'] = queries_pool['dholak'][~queries_pool['dholak']['original_filename'].str.contains('26', na=False)]

pilot_matrix = []
combinations = []
insts_no_voc = ['tabla', 'harmonium', 'flute', 'dholak', 'dhul']

for num_insts in range(1, 6):
    for _ in range(6):
        chosen = random.sample(insts_no_voc, num_insts)
        combinations.append(['vocals'] + chosen)

random.shuffle(combinations)

negative_count = 5
neg_idx = random.sample(range(30), negative_count)

for i, mix_insts in enumerate(combinations):
    example = {
        'id': f'pilot_{i:03d}',
        'mixture_composition': mix_insts,
        'sources': {}
    }
    
    for inst in mix_insts:
        row = pool[inst].sample(1).iloc[0]
        example['sources'][inst] = {
            'path': get_abs_path(row),
            'original_filename': row['original_filename']
        }
        
    is_negative = i in neg_idx
    if is_negative:
        absent = [inst for inst in insts_no_voc if inst not in mix_insts]
        if not absent:
            query_inst = random.choice(insts_no_voc)
            example['target_present'] = True
        else:
            query_inst = random.choice(absent)
            example['target_present'] = False
    else:
        query_inst = random.choice([inst for inst in mix_insts if inst != 'vocals'])
        example['target_present'] = True
        
    example['query_instrument'] = query_inst
    
    mix_origs = [example['sources'][inst]['original_filename'] for inst in example['sources']]
    valid_queries = queries_pool[query_inst][~queries_pool[query_inst]['original_filename'].isin(mix_origs)]
    
    if len(valid_queries) == 0:
        valid_queries = queries_pool[query_inst]
        
    q_row = valid_queries.sample(1).iloc[0]
    example['query_file'] = {
        'path': get_abs_path(q_row),
        'original_filename': q_row['original_filename']
    }
    
    if example['target_present']:
        example['target_path'] = example['sources'][query_inst]['path']
    else:
        example['target_path'] = None
        
    pilot_matrix.append(example)

with open(r'D:\IKS_Research\Instrument_Separation\mixtures\pilot_matrix.json', 'w') as f:
    json.dump(pilot_matrix, f, indent=4)
