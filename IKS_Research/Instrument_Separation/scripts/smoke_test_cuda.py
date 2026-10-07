import torch
import time
import os
import sys
import warnings
from omegaconf import OmegaConf

sys.path.append(r'C:\iks_scripts\query-bandit')
warnings.filterwarnings('ignore')

from train import _build_model
from core.models.ebase import EndToEndLightningSystem
from core.losses.base import BaseLossHandler
from core.losses.l1snr import L1SNRLoss
from torch_audiomentations.utils.object_dict import ObjectDict

print("CUDA Device:", torch.cuda.get_device_name(0))
print("PyTorch Version:", torch.__version__)

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
state_dict = torch.load(ckpt_path, map_location='cpu')['state_dict']

class DummyHandler(dict):
    def __init__(self):
        super().__init__()
    def __call__(self, *args, **kwargs):
        pass
    def get_mode(self, mode):
        return self

loss_handler = BaseLossHandler(loss=L1SNRLoss(), modality="audio", name="l1snr")

system = EndToEndLightningSystem(
    model=model, 
    loss_handler=loss_handler, 
    metrics=DummyHandler(), 
    augmentation_handler=None, 
    inference_handler=None, 
    optimization_bundle=None
)

try:
    system.load_state_dict(state_dict, strict=True)
except Exception as e:
    print(f"Strict load failed: {e}. Trying strict=False")
    system.load_state_dict(state_dict, strict=False)

def mock_log_dict(*args, **kwargs):
    pass
system.log_dict_with_prefix = mock_log_dict

system.cuda()
system.train()
print("System instantiated and loaded to CUDA.")

sys.path.append(r'D:\IKS_Research\Instrument_Separation\scripts')
from iks_banquet_dataset import IKSSourceSeparationDataset

dataset = IKSSourceSeparationDataset(
    manifest_path=r'D:\IKS_Research\Instrument_Separation\datasets\source_split_manifest.csv',
    split='TEST',
    mixture_metadata_path=r'D:\IKS_Research\Instrument_Separation\mixtures\pilot\pilot_dataset_metadata.json'
)

# Custom collate fn
def custom_collate(batch):
    item = batch[0]
    mix_audio = item["mixture"]["audio"].unsqueeze(0).cuda()
    query_audio = item["query"]["audio"].unsqueeze(0).cuda()
    target_audio = item["sources"]["target"]["audio"].unsqueeze(0).cuda()
    
    return ObjectDict({
        "mixture": ObjectDict({"audio": mix_audio}),
        "queries": ObjectDict({"target": ObjectDict({"audio": query_audio})}),
        "query": ObjectDict({"audio": query_audio}),
        "sources": ObjectDict({"target": ObjectDict({"audio": target_audio})}),
        "estimates": ObjectDict({})
    })

dataloader = torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=True, drop_last=False, collate_fn=custom_collate)
batch = next(iter(dataloader))

print("Starting batch_size=1 smoke test...")

torch.cuda.reset_peak_memory_stats()
torch.cuda.empty_cache()

opt = torch.optim.Adam(system.parameters(), lr=1e-4)
opt.zero_grad()

t0 = time.time()
loss_dict = system.training_step(batch, 0)
t1 = time.time()
print(f"Forward pass time: {t1 - t0:.3f}s")
print(f"Loss dict: {loss_dict}")

t2 = time.time()
if isinstance(loss_dict, tuple):
    loss = loss_dict[0]
elif isinstance(loss_dict, dict):
    loss = loss_dict.get('loss', loss_dict.get('l1snr', loss_dict.get('l1snr/target')))
else:
    loss = loss_dict

loss.backward()
t3 = time.time()
print(f"Backward pass time: {t3 - t2:.3f}s")

grad_finite = True
for p in system.parameters():
    if p.grad is not None:
        if not torch.isfinite(p.grad).all():
            grad_finite = False
            break
print(f"Gradient finiteness: {grad_finite}")

t4 = time.time()
opt.step()
t5 = time.time()
print(f"Optimizer step time: {t5 - t4:.3f}s")
print(f"Total step time: {t5 - t0:.3f}s")

print(f"Peak Allocated VRAM: {torch.cuda.max_memory_allocated() / (1024**2):.2f} MB")
print(f"Peak Reserved VRAM: {torch.cuda.max_memory_reserved() / (1024**2):.2f} MB")
print("Smoke test completed for batch_size=1.")
