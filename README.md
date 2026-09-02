<kbd><img src="https://github.com/Jekannadar/CLS-CAD/raw/main/applications/cls-cad-fusion-plugin/resources/vectors/clscad.svg" width="256" height="256" style="border-radius:50%"></kbd>

---

![Generic badge](https://img.shields.io/badge/python-fusion360%20|%203.10%20|%203.11-informational.svg?style=for-the-badge)
![Supported systems](https://img.shields.io/badge/os-windows-informational.svg?style=for-the-badge)
[![GitHub license](https://img.shields.io/github/license/Jekannadar/CLS-CAD?style=for-the-badge)](https://github.com/Jekannadar/CLS-CAD/blob/main/LICENSE)
[![CodeCov](https://img.shields.io/codecov/c/github/Jekannadar/CLS-CAD?style=for-the-badge&cacheSeconds=3600)](https://codecov.io/gh/Jekannadar/CLS-CAD)

[![Latest Release](https://img.shields.io/github/v/release/Jekannadar/CLS-CAD.svg?style=for-the-badge)](https://github.com/Jekannadar/CLS-CAD/releases/latest/download/cls-cad-fusion-plugin.msi)
[![Youtube Overview](https://img.shields.io/badge/YouTube-Overview-informational?style=for-the-badge)](https://youtu.be/gNqHxLpqiFw)
[![Dataset](https://img.shields.io/badge/dataset-zenodo.10051244-blue?style=for-the-badge)](https://doi.org/10.5281/zenodo.10051244)

<!---[![Issues](https://img.shields.io/github/issues/Jekannadar/CLS-CAD)](https://github.com/Jekannadar/CLS-CAD/issues)-->

---

An add-in and matching backend that allows adding types to Joint Origins and Parts in Fusion 360, and allows requesting and assembling results by means of combinatory logic.

When exploring a design space this is roughly two orders of magnitude faster than manual design, and a lot less tiring.

<details>
<summary><b>Your assembly creation could look like this!</b></summary>

![](docs/images/demo.gif)

</details>

To get started with the add-in, follow the instructions in the [getting started section](#getting-started).

There is an overview video available at: https://youtu.be/gNqHxLpqiFw <br>
(_Slightly outdated, newest features and performance improvements missing_)

# Installation

To install the add-in in Fusion 360, download the [latest installer](https://github.com/Jekannadar/CLS-CAD/releases/download/latest/cls-cad-fusion-plugin.msi) and execute it.
To use the plugin, you need a running backend.
This requires [docker](https://docs.docker.com/desktop/install/windows-install/) to be installed.
<br>
After installing and starting docker, in a terminal, run:

- `docker run -d -p 8000:80 --name cls-cad-backend --pull=always ghcr.io/Jekannadar/cls-cad-backend:latest`

For subsequent usage, simply start the `cls-cad-backend` container from the containers tab in the docker desktop application.

# Getting Started

## Install Add-In

Install the add-in using the [latest installer](https://github.com/Jekannadar/CLS-CAD/releases/download/latest/cls-cad-fusion-plugin.msi).
<br>
Please make sure to have started Fusion 360 at least once before installation. The add-in is available as of the next time launching Fusion 360.

<details>
<summary>GIF</summary>

![](docs/images/install-addin.gif)

</details>

## Install Docker and Run Backend

Run the backend (using docker, as detailed in the [Installation](#installation) section)
<br>
On subsequent runs after rebooting the PC, the created container shown at the end of the GIF can just be started again.

<details>
<summary>GIF</summary>

![](docs/images/install-docker.gif)

</details>

## Download and Extract Dataset

Download the [modular components for synthesizing robotic arms](https://doi.org/10.5281/zenodo.10051244) dataset.

<details>
<summary>GIF</summary>

![](docs/images/obtain-dataset.gif)

</details>

## Upload Dataset to Fusion

Launch Fusion 360 and create a new empty project. Open that project and upload the dataset.

<details>
<summary>GIF</summary>

![](docs/images/upload-dataset.gif)

</details>

## Prepare Project for Synthesis

Switch to the CLS-CAD tab in Fusion 360, and press the `Upload Taxonomy` button. Select the .taxonomy in the [modular components for synthesizing robotic arms](https://doi.org/10.5281/zenodo.10051244).
<br>
Press the `Crawl Project` button in the CLS-CAD tab and wait for the process to complete.

<details>
<summary>GIF</summary>

![](docs/images/crawl-project.gif)

</details>

## Request Synthesis

At the far right of the CLS-CAD tab, press the `Request Synthesis` button.
<br>
Select the part type `Base` in the upper taxonomy, optionally add constraints, and hit Ok.

<details>
<summary>GIF</summary>

![](docs/images/request-synthesis.gif)

</details>

## Explore Results

Press the `Assemble Results` button to explore and assemble any results

<details>
<summary>GIF</summary>

![](docs/images/assemble-result.gif)

</details>

# Basic Usage

- Create taxonomies for a project by using the graphical taxonomy editors.
- Place Joint Origins.
- Type the placed Joint Origins.
- Type the parts.
- Submit the parts to the backend.
- Request synthesis.
- Explore and assemble the results.

For a short video illustrating the process, see: https://youtu.be/gNqHxLpqiFw
