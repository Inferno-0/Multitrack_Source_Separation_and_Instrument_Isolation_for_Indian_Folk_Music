import torch
print('GPU Name:', torch.cuda.get_device_name(0))
print('Total VRAM:', torch.cuda.get_device_properties(0).total_memory / (1024**3), 'GB')
print('CUDA Version:', torch.version.cuda)
print('PyTorch Version:', torch.__version__)
print('CUDA Available:', torch.cuda.is_available())
