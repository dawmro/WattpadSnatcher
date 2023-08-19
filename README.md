# WattpadSnatcher
Scrape novels from wattpad.com and save them locally. Used to prepare input data for teller_of_tales.

## Setup:
1. Create new virtual env:
``` sh
python -m venv env
```
2. Activate your virtual env:
``` sh
env/Scripts/activate
```
3. Install packages from included requirements.txt:
``` sh
pip install -r .\requirements.txt
```

## Usage:
1. Put links to novels into novel_links.txt, one link per line, no empty lines.

2. Run scrapper:
``` sh
python .\wattpad_snacher.py
```
