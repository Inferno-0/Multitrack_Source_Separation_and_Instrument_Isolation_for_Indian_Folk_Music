import os
import pandas as pd
import glob
import numpy as np
import json

prepared_dir = r'D:\ISOLATED_INSTRUMENTS_PREPARED'
output_dir = r'D:\IKS_Research\Instrument_Separation\datasets'
os.makedirs(output_dir, exist_ok=True)

classes = ['vocals', 'tabla', 'harmonium', 'flute', 'dholak', 'dhul']
all_records = []

np.random.seed(42)

for c in classes:
    meta_files = glob.glob(os.path.join(prepared_dir, c, '*metadata.csv'))
    if not meta_files:
        meta_files = glob.glob(os.path.join(prepared_dir, c, 'metadata.csv'))
    df = pd.read_csv(meta_files[0])
    
    unique_sources = df['original_filename'].unique()
    np.random.shuffle(unique_sources)
    
    n_sources = len(unique_sources)
    
    if n_sources < 10:
        val_count = max(1, int(n_sources * 0.15))
        test_count = max(1, int(n_sources * 0.15))
    else:
        val_count = int(n_sources * 0.15)
        test_count = int(n_sources * 0.15)
        
    train_end = n_sources - val_count - test_count
    val_end = train_end + val_count
    
    for i, src in enumerate(unique_sources):
        if i < train_end:
            split = 'TRAIN'
        elif i < val_end:
            split = 'VALIDATION'
        else:
            split = 'TEST'
            
        is_mixture = True
        is_query = True if c != 'vocals' else False
        
        # Exception for Dholak sample 26
        if '26' in str(src) and c == 'dholak':
            split = 'EXCLUDED'
            is_mixture = False
            is_query = False
            
        subset = df[df['original_filename'] == src]
        for _, row in subset.iterrows():
            rec = {
                'instrument': c,
                'prepared_filename': row['standardized_filename'],
                'original_filename': src,
                'original_source_path': row.get('original_path', ''),
                'split': split,
                'eligible_as_mixture_source': is_mixture,
                'eligible_as_query_source': is_query,
                'duration_seconds': row['standardized_duration_seconds'],
                'curation_status': row.get('curation_status', 'OK'),
                'notes': row.get('notes', '')
            }
            all_records.append(rec)

out_df = pd.DataFrame(all_records)
out_df.to_csv(os.path.join(output_dir, 'source_split_manifest.csv'), index=False)
out_df.to_json(os.path.join(output_dir, 'source_split_manifest.json'), orient='records', indent=2)

report = {
    'total_files': len(all_records),
    'splits': out_df['split'].value_counts().to_dict(),
    'mixture_sources': int(out_df['eligible_as_mixture_source'].sum()),
    'query_sources': int(out_df['eligible_as_query_source'].sum()),
    'by_instrument': out_df.groupby('instrument')['split'].value_counts().unstack().fillna(0).to_dict()
}
print(json.dumps(report, indent=2))
