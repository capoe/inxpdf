# (J)INXPDF
Barebone tool to generate PDF slides from inkscape files.

## Setup
```bash
./configure.py
source bin/INXPDFRC
jinxpdf -h
```

## Dependencies
- python2 (legacy code ... should work with python3 though)
- numpy
- lxml
- pdftk (Ubuntu: install via snap)

## Usage
```bash
cd template
jinxpdf -f cover.svg -p cover.pdf
```

## Acknowledgements
All the credit for the scripts in ./js goes to Guillaume Savaton (https://sozi.baierouge.fr).
