# Digital IC Functionality Duplication Using Neural Networks

> Reproduce / approximate the functional behavior of small digital sequential circuits (VHDL / schematic designs) using neural networks trained on input–output traces.

---

## Table of contents

- [Overview](#overview)  
- [Quickstart](#quickstart)  
- [Dependencies](#dependencies)  
- [Dataset / Data preparation](#dataset--data-preparation)  
- [Project structure](#project-structure)  
- [How to run (examples)](#how-to-run-examples)  
- [Training tips & wandb](#training-tips--wandb)  
- [Evaluation & expected outputs](#evaluation--expected-outputs)  
- [Contributing](#contributing)  
- [License](#license)  
- [Contact / Acknowledgements](#contact--acknowledgements)

---

## Overview

Digital circuits (counters, shift registers, LFSRs, etc.) can be represented as input → state → output mappings. This project collects traces from VHDL/Quartus/ModelSim simulations and uses them to train neural-network models that approximate the circuit's functional behaviour. The goal is *functionality duplication*: given the same inputs (and initial states), the trained NN should produce the same outputs as the original digital design.

---

## Quickstart

1. Clone the repo:
```bash
git clone https://github.com/Anjanamb/Digital-IC-Functionality-Duplication-Using-NN.git
cd Digital-IC-Functionality-Duplication-Using-NN
```

2. Create a Python virtual environment and activate it:
```bash
python -m venv venv
# on Linux/macOS
source venv/bin/activate
# on Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

3. Install dependencies (or create a `requirements.txt` from these lines):
```bash
pip install numpy mysql-connector-python tensorflow Flask wandb keras-tuner
```

---

## Dataset / Data preparation

This project uses datasets generated from VHDL designs and ModelSim/Quartus simulations. The dataset-preparation repository referenced in this project contains the scripts and designs used to produce the training traces (VHDL testbenches, schematic files, and dataset `.txt` traces). Please refer to that repository for the exact dataset-generation pipeline and file formats.

Typical dataset items:
- VHDL testbenches (`.vhd`) used to create stimuli.  
- Schematic design files (`.bdf`) for the circuit layout.  
- Plain text dataset files (`.txt`) containing aligned input / output / state traces suitable for feeding into training pipelines.

**Where to put the data locally**  
Create a directory `data/` at repo root and place the generated `.txt` traces there (or update the training script `--data` argument to point to your dataset folder).

---

## Project structure (top-level)

```
Digital-IC-Functionality-Duplication-Using-NN/
├─ Logic_Function/          # Logic designs / helper scripts (VHDL, schematics, generators)
├─ NN for testing/          # Neural-network training / testing scripts and model code
├─ .gitignore
└─ README.md                # <- you are replacing/updating this file
```

> Note: It is recommended to rename `NN for testing` → `nn_for_testing` (no spaces) to make CLI paths and imports easier.

---

## How to run (examples)

**Train (example)**
```bash
# Example - adapt filenames to match this repo's scripts
python "NN for testing/train.py"   --data ../data/my_trace.txt   --model-dir models/   --epochs 50   --batch-size 64
```

**Evaluate**
```bash
python "NN for testing/evaluate.py"   --model models/last   --data ../data/validation_trace.txt
```

If you rename the folder (recommended):
```bash
python nn_for_testing/train.py --data data/my_trace.txt
```

---

## Training tips & wandb

This repository lists `wandb` as an optional dependency for experiment tracking; to use it:

1. Install & login:
```bash
pip install wandb
wandb login
```

2. In your training script, initialize:
```python
import wandb
wandb.init(project="digital-ic-duplication", config=your_config_dict)
```

---

## Evaluation & expected outputs

- Expected model outputs: the NN should produce digital-output sequences matching the ground-truth trace, within an acceptable error (binary classification per output bit or regression + thresholding depending on setup).
- Evaluation scripts should compute per-bit accuracy, sequence-level accuracy, and optionally confusion matrices and timing/skew analyses.

---

## Suggested improvements

1. Add `requirements.txt` with pinned versions.  
2. Rename `NN for testing` to `nn_for_testing` to avoid spaces.  
3. Add explicit entrypoints (e.g., `train.py`, `evaluate.py`) and show example CLI flags.  
4. Add a `data/README.md` explaining the expected trace/text format and a small sample `.txt`.  
5. Add unit / smoke tests for reproducibility. 
6. Document model architecture choices.  
7. Add a usage example notebook.

---

## Contributing

1. Open an issue to discuss major changes.  
2. Create a branch, add tests & docs for your feature, and submit a PR.  
3. Keep commits small and clear; update README examples if you change CLIs.

---

## License

MIT License – feel free to use, modify, and share. Please credit the repository if used in research or academic work.

---

## Contact / Acknowledgements

Author: **Anjana Bandara** (GitHub: [Anjanamb](https://github.com/Anjanamb))  
Contributors: [Ayesh-Rajakaruna](https://github.com/Ayesh-Rajakaruna), [sahannt98](https://github.com/sahannt98)
