# LongestPath
Implementations of state-of-the-art longest path algorithms.

## Setup
You need `gcc` to compile the C code, and `python3` for the python code.
WSL is recommended for running on Windows.
```bash
# Create virtualenv
python3 -m venv venv
# Activate it (repeat this step on shell restart)
source venv/bin/activate
# Upgrade pip
pip install -U pip
# Install dependencies (e.g. for matplotlib and numpy)
pip install -r requirements.txt
```

```bash
make
# Find longest path in randomly generated graph of 30 vertices (p=0.3/30)
./lpath 30

# make and run
make && ./lpath 30
```