# Trackbio

A command-line tool designed for biologists to predict future animal locations based on historical geolocalization data and environmental variables from the Copernicus Marine Service.

## Overview

This tool takes a local CSV file containing timestamped latitude and longitude data for an animal (or multiple animals). It then connects to the Copernicus Marine Service API to download relevant environmental data (like sea surface temperature, currents, chlorophyll levels, etc.) corresponding to the time and locations in your input file. Finally, it uses this combined dataset to train a predictive model and forecast potential future locations of the animal(s).

## Features

* Loads animal track data from a local CSV file.
* Automatically fetches relevant environmental data from Copernicus Marine Service API.
* Integrates animal location data with environmental variables.
* Trains a model to predict future movement patterns.
* Outputs predicted future locations.

## Prerequisites

* **Python:** Version 3.8 or higher recommended. Tested in 3.12.9.
* **Pip** or **Conda:** Python package installer.
* **Copernicus Marine Service Account:** You need valid credentials (username and password) to access the API. You can register here: https://data.marine.copernicus.eu/register. 
* **Input Data:** A CSV file with animal geolocalization data (details below).

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/pablopertusa/trackbio.git
    cd trackbio
    ```

2.  **Set up a virtual environment (Recommended):**
    ```bash
    # For Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Env Configuration

You need to place your Copernicus Marine credentials in a .env file at the root of the project for the application to work correctly.

```bash
USERNAME_COPERNICUS=your_user
PASSWORD_COPERNICUS=your_password
```

## Configuration File (`config.json`)

This file defines the configuration parameters for the app. It allows you to specify where your input data is located and where to store outputs such as environmental data and prediction maps.

## Structure of the File

Below is an example of a typical `config.json` file:

```json
{
    "copernicus_datasets": [
        "cmems_mod_glo_phy_my_0.083deg_P1D-m",
        "cmems_mod_glo_bgc_my_0.25deg_P1D-m"
    ],
    "animal_data": "data/datos_foca.csv",
    "data_folder": "data/",
    "distribution_image_folder": "images/",
    "grid_size": 1,
    "training_verbosity": true
}
```

## Parameters Description

| Key                          | Description |
|------------------------------|-------------|
| `copernicus_datasets`        | *(Do not modify unless you know what you are doing)* — List of dataset IDs from the [Copernicus Marine Service](https://marine.copernicus.eu/) that will be used for downloading environmental data. |
| `animal_data`                | Path to the `.csv` file that contains the animal tracking data. This file should include columns named `latitude`, `longitude`, and `date` with format `Y-%m-dTH:%M:%S`. |
| `data_folder`                | Path to the folder where downloaded environmental data will be stored. |
| `distribution_image_folder` | Path to the folder where the output distribution maps will be saved. |
| `grid_size`                  | *(Advanced)* Grid resolution for model computations. Default is `1`. |
| `training_verbosity`         | *(Advanced)* Whether to show detailed training logs during model fitting. Set to `true` or `false`. |

## Instructions

Before running the tool, make sure this file is named `config.json` and located in the root of the project.

Modify only the following fields according to your data and preferences:

- `animal_data`  
- `data_folder`  
- `distribution_image_folder`  

**Do not modify the remaining fields unless you understand their purpose.**

## Notes

* All paths should be relative to the root of the project.
* Make sure the specified folders exist or the program will try to create them automatically.
* The config.json that already exists is an example of how it should look like.