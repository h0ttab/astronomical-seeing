# 🔭 AstronomicalSeeing Telegram Bot 

An automated Python script designed to monitor meteorological conditions and notify users via Telegram when optimal conditions for astronomical observations (stargazing) are met.

![Report example](./report_example.png)

## ⚙️ Features
*   **API Integration:** Fetches and parses complex meteorological and astronomical data from Meteoblue API.
*   **Data Processing:** Filters data based on cloud cover percentage, calculates precise moon illumination using trigonometric functions, and handles timezone offsets.
*   **Dynamic Reporting:** Generates human-readable weather reports using **Jinja2** templates.
*   **Proactive Alerting:** Automatically sends observation reports directly to Telegram.
*   **Error Handling & Monitoring:** Features a global exception handler that logs errors and forwards full stack traces to Telegram, ensuring zero silent failures (SRE approach).
*   **Robust Configuration:** Uses strictly validated YAML configuration files (via the `schema` library).

## 🛠 Tech Stack
*   **Language:** Python 3.11+
*   **Libraries:** `requests`, `pyyaml`, `jinja2`, `schema`
*   **Deployment:** Docker ready

> **Note on code documentation:** The variables, functions, and architecture are in English. The docstrings within the code are written in Russian, as this project was initially developed for a local astronomy community.

## 🚀 How to Run

### Option 1: Using Docker (Recommended)
1. Clone the repository.
2. Edit `config.yml` in the root directory and add your API keys and Telegram credentials.
3. Build the Docker image:
   ```bash
   docker build -t astronomical-seeing .
   ```