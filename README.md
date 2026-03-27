# ToBeControl (AI-Powered Backend & Telegram Bot) 🤖💊

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org)
[![Library: python-telegram-bot](https://img.shields.io/badge/library-python--telegram--bot-blue.svg)](https://python-telegram-bot.org/)
[![Database: MongoDB](https://img.shields.io/badge/database-MongoDB-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Inference: Groq](https://img.shields.io/badge/AI-Groq%20LPU-orange.svg)](https://groq.com/)

**ToBeControl** is the intelligent core of the ToBeControl ecosystem. This backend combines a Telegram Bot interface with **Groq Cloud API** to provide lightning-fast AI reasoning, patient intent classification, and automated medication reminders for Tuberculosis (TBC) patients.

## 🌟 Key Functions
* **AI-Powered Responses:** Uses **Groq (LLama/Mixtral models)** for instant, human-like medical guidance and FAQ handling.
* **Smart Classification:** Automatically classifies patient messages (e.g., reports of side effects vs. intake confirmations) using LLM logic.
* **Automated Reminders:** Scheduled notifications to ensure strict TBC medication adherence.
* **Patient Data Management:** Securely stores treatment logs and profiles in **MongoDB**.
* **Seamless Integration:** Synchronizes all AI-processed data with the [ToBeControlWeb](https://github.com/Zizyxx/ToBeControlWeb) frontend.

## 🛠️ Tech Stack
* **Language:** Python 3.9+
* **Framework:** [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
* **AI Engine:** [Groq Cloud API](https://console.groq.com/) (LPU™ Inference)
* **Database:** [MongoDB](https://www.mongodb.com/) (NoSQL)
* **Environment:** `python-dotenv` for secure API key management.

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Zizyxx/ToBeControl.git](https://github.com/Zizyxx/ToBeControl.git)
   cd ToBeControl
