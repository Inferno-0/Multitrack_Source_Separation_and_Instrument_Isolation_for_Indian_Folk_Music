import csv
import json
import collections

manifest = r'D:\IKS_Research\Instrument_Separation\datasets\source_split_manifest.csv'
qbank = r'D:\IKS_Research\Instrument_Separation\datasets\query_bank\metadata.json'

splits = collections.defaultdict(lambda: collections.defaultdict(int))
source_splits = {}

with open(manifest, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        s = row['split']
        i = row['instrument']
        name = row['prepared_filename']
        splits[s][i] += 1
        source_splits[name] = s

print('Source Manifest Split Counts:')
for s, insts in splits.items():
    print(f"  {s}:")
    for i, c in insts.items():
        print(f"    {i}: {c}")

with open(qbank, 'r', encoding='utf-8') as f:
    qb = json.load(f)

print('\nQuery Bank Metadata (Target -> Source Files):')
leak_count = 0
for target, items in qb.items():
    files = [x['source_file'] for x in items]
    print(f"  {target}: {len(files)} files")
    for fl in files:
        if source_splits.get(fl, 'UNKNOWN') != 'TRAIN':
            print(f"    WARNING: Query {fl} is not from TRAIN split! (Found in {source_splits.get(fl, 'UNKNOWN')})")
            leak_count += 1

print(f'\nTotal Query Leaks: {leak_count}')
