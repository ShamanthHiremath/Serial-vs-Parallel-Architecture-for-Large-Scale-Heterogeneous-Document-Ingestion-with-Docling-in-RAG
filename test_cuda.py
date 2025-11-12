import sys, traceback
try:
    import torch
except Exception as e:
    print("Failed to import torch:", repr(e))
    traceback.print_exc()
    raise SystemExit(1)

print("python:", sys.executable)
print("torch version:", getattr(torch, "__version__", None))
print("cuda available:", torch.cuda.is_available())
print("cuda device count:", torch.cuda.device_count())
if torch.cuda.is_available() and torch.cuda.device_count() > 0:
    print("current device:", torch.cuda.current_device())
    print("device name:", torch.cuda.get_device_name(0))