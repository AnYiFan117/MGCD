# MGCD

This repository contains the replication package for the MGCD.

## Installation

To install the necessary dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Usage

First, you need to put your dataset in the data/dataset/your_dataset_name folder.

Then, you need to finish config/config.py in order to complete the configuration.

To run the entire analysis pipeline, execute the `run.sh` script:

```bash
bash run.sh
```

## NOTE
To customize the dataset, you need to finish some TODOs in config/config.py and follow the format in data/dataset/put_your_dataset_here.md