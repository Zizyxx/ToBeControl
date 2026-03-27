# ToBeControl (Core Backend & Telegram Bot) 🤖💊

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org)
[![Library: python-telegram-bot](https://img.shields.io/badge/library-python--telegram--bot-blue.svg)](https://python-telegram-bot.org/)
[![Database: MongoDB](https://img.shields.io/badge/database-MongoDB-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**ToBeControl** is the central logic engine and Telegram Bot integration for the ToBeControl ecosystem. It leverages a non-relational database to manage Tuberculosis (TBC) patient data, providing automated medication reminders and a seamless synchronization bridge to the [ToBeControlWeb](https://github.com/Zizyxx/ToBeControlWeb) frontend.

## 🌟 Key Functions
* **Automated Reminders:** Uses scheduled tasks to send Telegram notifications for medication schedules.
* **Patient Data Management:** Efficiently stores patient profiles, treatment history, and adherence logs in MongoDB.
* **Interactive Bot Interface:** Built with `python-telegram-bot` for a smooth, command-based user experience.
* **Status Tracking:** Allows patients to update their intake status, which is then reflected on the web dashboard.
* **Scalable Architecture:** NoSQL structure allows for flexible data schema as the project grows.

## 🛠️ Tech Stack
* **Language:** Python 3.9+
* **Framework:** [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) (v20+ recommended)
* **Database:** [MongoDB](https://www.mongodb.com/) (NoSQL)
* **Driver:** `pymongo` or `motor` (for asynchronous DB operations)
* **Integration:** Direct MongoDB connection shared with the Web Interface.

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Zizyxx/ToBeControl.git](https://github.com/Zizyxx/ToBeControl.git)
   cd ToBeControl
