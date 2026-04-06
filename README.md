# KenditAI: Intelligent Data Retrieval Assistant

### 🚀 Overview
**KenditAI** is an AI-powered assistant designed to optimize structured information retrieval using **RAG (Retrieval-Augmented Generation)**. This project bridges the gap between natural language and local databases, allowing users to interact with **SQL Server** data in a more intuitive and efficient way.

### 📋 Prerequisites
Before running **KenditAI**, ensure you have the following installed:
* **Python 3.14.3** (Optimized for the latest release)
* **Microsoft SQL Server (SSMS):** To host the local database.
* **Ollama:** Required to run the local LLM.
* **Google Cloud Project:** With OAuth 2.0 credentials enabled for Google Auth.

### 🛠️ Key Features
* **Natural Language Querying:** Translates user intent into data-driven insights.
* **RAG Implementation:** Leverages retrieval techniques to provide context-aware responses grounded in real database records.
* **Secure Database Integration:** Robust connection to **SQL Server** using **parameter markers** to prevent SQL injection.
* **Voice Recognition:** Integrated speech-to-text for hands-free querying.
* **Google OAuth 2.0:** Secure user authentication for personalized chat history.

### 💻 Tech Stack
* **Language:** Python 3.14.3
* **UI Framework:** CustomTkinter
* **Database:** Microsoft SQL Server (SSMS)
* **AI Models:** Ollama (phi3)
* **Key Libraries:** pyodbc, ollama, speech_recognition, google-api-python-client

### ⚙️ Installation & Setup

1. **Ollama Setup (Local AI):**
   - Download and install Ollama from ollama.com
   - Open your terminal and run: ollama run phi3
   (This will download the required model for KenditAI).

2. **Clone the repository:**
   git clone https://github.com/tu-usuario/KenditAI.git
   cd KenditAI

3. **Create and activate a virtual environment:**
   python -m venv venv
   .\venv\Scripts\activate

4. **Install dependencies:**
   pip install -r requirements.txt

---

## 👤 Author
**Kendall Jesus Alpizar Rodriguez**
* **LinkedIn:** [My Profile](https://www.linkedin.com/in/kendall-alp%C3%ADzar-rodr%C3%ADguez-422480234/)
* **Email:** Ken.alp.01.kar@gmail.com
* **Location:** San José, Costa Rica 🇨🇷

---

> [!IMPORTANT]
> **Privacy & Security Note:** For security reasons, this repository **does not include database files (.mdf/.bak) or access credentials**. It focuses on the source code and architectural design.