# (J)INXPDF
Barebone tool to generate PDF slides from inkscape files.

## Installation
```bash
git clone https://github.com/capoe/inxpdf.git
cd inxpdf
conda create --prefix ./venv python=3.7
conda activate ./venv
pip install .
export INXPDF_ROOT=$(pwd)
```

## Usage
```bash
cd template
jinxpdf -f cover.svg -p cover.pdf
```

## Acknowledgements
All the credit for the scripts in ./js goes to Guillaume Savaton (https://sozi.baierouge.fr).
