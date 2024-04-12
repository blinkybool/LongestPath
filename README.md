# LongestPath
Implementations of state-of-the-art longest path algorithms.

## Setup
You need `gcc` to compile the C code, and `python3` for the python code.
WSL is recommended for running on Windows.
```bash
# Create virtualenv
python3 -m venv venv
# Activate it (repeat this step on shell restart)
source ./venv/bin/activate
# Upgrade pip
pip install -U pip
# Install dependencies (e.g. for matplotlib and numpy)
pip install -r requirements.txt
```
In order for KaLP to run you need to install KaLP manually and expose the executable path to python.
For installing KaLP checkout: https://karlsruhelongestpaths.github.io/.
To give python access to the KaLP executable you need to set the `KALP_PATH` environment variable using `.env` files.
In order for the notebooks to work you also need a duplicate of this `.env` file to be included in `./notebooks`.
```bash
touch .env
echo "KALP_PATH=[you kalp path]" > .env
cp .env notebooks/.env
```