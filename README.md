# RetroPieStats

## Purpose

RetroPieStats collects statistics about gameplay on RetroPie devices and stores them in AWS DynamoDB via AWS IoT Core. It enables tracking and analysis of game sessions for retro gaming enthusiasts.

## Tech Stack

- **AWS CDK (Python):** Infrastructure as code for AWS resources
- **AWS IoT Core:** Secure message ingestion from devices
- **AWS DynamoDB:** Storage for game statistics
- **Python:** Raspberry Pi client and CDK scripts
- **GitHub Copilot:** Code generation.

## Setup

1. **Clone the repository**

2. **Create and activate a Python virtual environment**
   ```sh
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Deploy AWS resources**
   ```sh
   cdk deploy
   ```

## Raspberry Pi Files

Place the files from the `raspberry_pie` directory onto your Raspberry Pi.  
These files handle collecting and publishing game statistics to AWS IoT Core.

The `runcommand-onend.sh` and `runcommand-onstart.sh` files go in `opt/retropie/configs/all`.

## Notes

- No RetroPie setup instructions are provided.
- Store your IoT certificate ARN in `certificate_arn.txt` (not committed to git).