<!-- PROJECT SHIELDS -->
<!--
*** Markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Issues][issues-shield]][issues-url]
[![Unlicense License][license-shield]][license-url]

<!-- ABOUT THE PROJECT -->
<div align="center">
  <h3 align="center">Hitchmap</h3>
  <p align="center">
    The map to hitchhiking the world.
    <br />
    <br />
    <a href="https://github.com/Hitchwiki/hitchmap/issues/new?labels=bug&template=bug_report.md">Report Bug</a>
    &middot;
    <a href="https://github.com/Hitchwiki/hitchmap/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

## About The Project

Read more [here](https://hitchwiki.org/en/Hitchwiki:Maps).

Join the conversation about a map for hitchhiking in our [Signal Chat](https://signal.group/#CjQKIDyYgIxcOUCEPYu8-JawC_tv1bcgkAhvbISRZkN45MMVEhCtydy3DOOCKEAE_tsR6g9s).

### Fork and Divergence

This repository, [`Hitchwiki/hitchmap`](https://github.com/Hitchwiki/hitchmap), is a fork of [`bobjesvla/hitch`](https://github.com/bobjesvla/hitch). While both projects share a common origin, they have since taken different development paths. At this stage, it remains uncertain which repository will emerge as the mainline project. However, we remain open to collaboration and potential reconciliation of efforts.

For contributors and users, we recommend reviewing both repositories to determine which best fits your needs.


## Getting Started

Set up Python virtual environment, install requirements and download the latest database dump:

Works with Python 3.12.6

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
curl https://hitchmap.com/dump.sqlite > db/points.sqlite
```

Initialize and run the Flask server:

```bash
flask --app hitch init
flask --app hitch generate-all
flask run
```

In order to run the project continuously, use `cron.sh` to set up corresponding cronjobs to update the views and `hitchmap.conf` as a basic NGINX configuration.

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

## License

The software provided in this repository is licensed under AGPL 3.0. The Hitchmap database is licensed under the ODBL, the license used by OpenStreetMap.

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/Hitchwiki/hitchmap.svg?style=for-the-badge
[contributors-url]: https://github.com/Hitchwiki/hitchmap/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Hitchwiki/hitchmap.svg?style=for-the-badge
[forks-url]: https://github.com/Hitchwiki/hitchmap/network/members
[stars-shield]: https://img.shields.io/github/stars/Hitchwiki/hitchmap.svg?style=for-the-badge
[stars-url]: https://github.com/Hitchwiki/hitchmap/stargazers
[issues-shield]: https://img.shields.io/github/issues/Hitchwiki/hitchmap.svg?style=for-the-badge
[issues-url]: https://github.com/Hitchwiki/hitchmap/issues
[license-shield]: https://img.shields.io/github/license/Hitchwiki/hitchmap.svg?style=for-the-badge
[license-url]: https://github.com/Hitchwiki/hitchmap/blob/master/LICENSE.txt
[Flask]: https://img.shields.io/badge/flask-000000?style=for-the-badge&logo=flask&logoColor=white
[Flask-url]: https://flask.palletsprojects.com/en/stable/