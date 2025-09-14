# RetroPieStats

## Disclaimer

**This project is entirely AI-generated.** The purpose is to demonstrate both technical knowledge of the AWS tech stack (CDK, IoT Core, DynamoDB, Lambda) and proficiency in leveraging generative AI tools for software development. All code, infrastructure, and documentation were created using AI assistance.

## Purpose

RetroPieStats collects statistics about gameplay on RetroPie devices and stores them in AWS DynamoDB via AWS IoT Core. It enables tracking and analysis of game sessions for retro gaming enthusiasts.

## Tech Stack

- **AWS CDK (Python):** Infrastructure as code for AWS resources
- **AWS Iot Python SDK (aws-iot-device-sdk-python-v2):** Installed on Raspberry Pi for communication with Iot
- **AWS IoT Core:** Secure message ingestion from devices
- **AWS DynamoDB:** Storage for game statistics
- **Python:** Raspberry Pi client and CDK scripts
- **GitHub Copilot/Amazon Q:** Code generation.

## Recommended Development Environment

- **VS Code** (Visual Studio Code)

### Recommended Extensions

- Black Formatter
- isort
- Pylance
- Pylint
- Python
- Python Debugger
- GitHub Copilot/Amazon Q

## Setup

1. **Clone the repository**

2. **Create and activate a Python virtual environment**
   ```sh
   python -m venv .venv
   source .venv/Scripts/activate
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Create an AWS IoT certificate**
   - In the AWS Console, go to IoT Core → Security → Certificates.
   - Create a new certificate and download the certificate and private key.
   - Copy the certificate ARN and save it in a file named `certificate_arn.txt` in the project root.

5. **Deploy AWS resources**
   ```sh
   cdk deploy
   ```

## Raspberry Pi Files

Place the files from the `raspberry_pie` directory onto your Raspberry Pi.  
These files handle collecting and publishing game statistics to AWS IoT Core.

The `runcommand-onend.sh` and `runcommand-onstart.sh` files go in `opt/retropie/configs/all`.

Your certificate must also be deployed to the device. Refer to `publish_game_data.py`. Either use the hardcoded locations or update the paths in the script.

```bash
scp publish_game_data.py pi@10.0.0.44:~/sdk-workspace/aws-iot-device-sdk-python-v2/samples/publish_game_data.py
```
