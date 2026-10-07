import torch
ckpt = torch.load(r'C:\iks_scripts\query-bandit\ev-pre-aug.ckpt', map_location='cpu')
print("Keys:", ckpt.keys())
if 'hyper_parameters' in ckpt:
    print("Hyper parameters:", ckpt['hyper_parameters'])
