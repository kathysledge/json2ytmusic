### Installation

Clone this repository, e.g.

```bash
git clone git@github.com:kathysledge/json2ytmusic.git
```

Navigate to the `json2ytmusic` folder and create a virtual env:

```bash
cd json2ytmusic && python -m venv .venv
```

Active the virtual env:

```bash
source .venv/bin/activate
```

Install the requirements:

```bash
pip install -r requirements.txt
```

You're all set!

### Usage

Download and extract your Spotify archive and locate the file named `YourLibrary.json`

Copy that file into the `json2ytmusic` folder.

From your activated virtual env shell, run:

```bash
python json2ytmusic.py
```

This might take a few minutes (roughly 1 second per album searched).

When the script has completed, you will have some new files in the folder, and a new folder called `covers`.

Open the file `results.html` and you will see the results!

### License

BSD 3-Clause License
