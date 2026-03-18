import platform
from pathlib import Path

# Detect OS and set data root
os_name = platform.system()

if os_name == "Windows":
    DATA_ROOT = Path("Z:/")
elif os_name == "Darwin":  # macOS
    DATA_ROOT = Path("/Volumes/classdata/")
elif os_name == "Linux":
    DATA_ROOT = Path("/mnt/classdata/")
else:
    raise RuntimeError(f"Unsupported OS: {os_name}")


if __name__ == '__main__':
    print(DATA_ROOT)