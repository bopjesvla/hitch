# Hitchmap

The map to hitchhiking the world. Read more [here](https://hitchwiki.org/en/Hitchwiki:Maps).


## Description

- `flask run` runs the server
- `flask --app hitch generate [script]` generates pages or the dump, for example:
  - `flask --app hitch generate show` builds the main HTML page (`index.html`). This is where the magic happens.
  - `flask --app hitch generate dump` runs the monthly dump
  - `flask --app hitch generate-all` generates all files
- `cron.sh` is the crontab running above files
- `hitchmap.conf` is the NGINX configuration

## License

The software provided in this repository is licensed under AGPL 3.0. The Hitchmap database is licensed under the ODBL, the license used by OpenStreetMap.

## Installation (on Linux)

### Setting up the python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Fetching the database
```
curl https://hitchmap.com/dump.sqlite > db/points.sqlite
```

### Installing pre-commit to automatically run the linter
```
pre-commit install
```

## Getting started
### Running

```
flask --app hitch generate-all
flask run
```

### Linting

We use Ruff for linting [https://docs.astral.sh/ruff/](https://docs.astral.sh/ruff/).

The settings can be found in `ruff.toml`.

To configure automatic linting for VS Code check out the extension [https://github.com/astral-sh/ruff-vscode](https://github.com/astral-sh/ruff-vscode).

## Contributing
Join the conversation about a map for hitchhiking in our [Signal Chat](https://signal.group/#CjQKIDyYgIxcOUCEPYu8-JawC_tv1bcgkAhvbISRZkN45MMVEhCtydy3DOOCKEAE_tsR6g9s).

File an [issue](https://github.com/bopjesvla/hitch/issues) if you have a feature request or found a bug.

Perform a [pull request](https://github.com/bopjesvla/hitch/pulls) from your [fork](https://github.com/bopjesvla/hitch/fork) of the repository if you solved an issue. (It's best to file an issue first so we can discuss it and reference it in the PR.)

## Data
If you find the data collected and provided by hitchmap.com helpful, feel free to cite it using:
```
@misc{hitchhiking,
author = {Bob de Ruiter, Till Wenke},
title = {Dataset of Hitchhiking Trips},
year = {2024},
url = {https://hitchmap.com},
}
```

