# DynpackTests

# Requirements:

Python installed, preferably version 3.13

# Installation (run everything in the main project folder):

```bash
C:\...\Python313\python -m venv .venv
.venv\Scripts\activate
python.exe -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

# Running all tests:

```bash
.venv\Scripts\python.exe -m pytest
```

# Run the selected test (with the smoke marker):

```bash
.venv\Scripts\python.exe -m pytest -m smoke
```

# Prepare a csv file with the data in the tools folder.

File name: .env

Data:

BASE_URL=
TRELLO_API_KEY=
TRELLO_API_TOKEN=
EMAIL=
PASSWORD=
