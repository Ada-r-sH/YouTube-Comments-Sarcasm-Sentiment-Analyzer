# 🎬 YouTube Sentiment & Sarcasm Analyzer

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16+-FF6F00)
![Groq](https://img.shields.io/badge/Groq-Llama_3-black)

An AI-powered dashboard that fetches YouTube comments in real-time using YouTube Data API V3, analyzes them for underlying sentiment and sarcasm using a custom-trained Deep Learning model, and generates an executive summary using llama-3.1-8b-instant.

**[🔴Live App](https://youtube-comments-sarcasm-sentiment-analyzer-fyz7djni98ywerb9me.streamlit.app/)**

---

## 📋 Table of Contents

- [Features](#-features)
- [Model Architecture](#-model-architecture)
- [Tech Stack](#tech-stack)
- [Local Installation](#-local-installation)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Set Up a Virtual Environment](#2-set-up-a-virtual-environment)
  - [3. Install Dependencies](#3-install-dependencies)
  - [4. Configure API Keys](#4-configure-api-keys)
  - [5. Run the App](#5-run-the-app)
- [Project Structure](#-project-structure)
- [Disclaimer](#disclaimer)

---

## ✨ Features

- **Real-Time Web Scraping:** Connects directly to the YouTube Data v3 API to pull up to 600 comments from any public video.
- **Custom NLP Classification:** Utilizes a custom-built, dual-output TensorFlow/Keras neural network (Bidirectional LSTM) to classify comments into Positive, Negative, or Neutral.
- **Sarcasm Detection:** A secondary output layer specifically trained to flag sarcastic or ironic comments that traditional sentiment analyzers misclassify, automatically weighting them as negative.
- **Executive LLM Summaries:** Integrates with the Groq API (running `llama-3.1-8b-instant`) to output a high-level, human-readable analysis of audience consensus.
- **Dynamic Weighting:** Allows users to adjust the mathematical weight of "Likes vs. Volume" to see how the silent majority (upvoters) impacts overall sentiment.

---

##  Model Architecture

The custom Deep Learning model was built and trained using TensorFlow/Keras. You can view the full training process, data pipeline, and evaluation metrics in the provided Jupyter Notebook:

`notebooks/model_training.ipynb`

### Tech Stack

| Layer | Tools |
|---|---|
| Frontend / UI | Streamlit, Bootstrap Icons |
| Backend Core | Python, Pandas, NumPy |
| Machine Learning | TensorFlow CPU, Keras |
| LLM Integration | Groq API |
| Data Ingestion | Google API Python Client |

---

## Local Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/youtube-sentiment-ai.git
cd youtube-sentiment-ai
```

### 2. Set Up a Virtual Environment

**On Ubuntu / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.streamlit` folder and a `secrets.toml` file inside it:

```bash
mkdir .streamlit
nano .streamlit/secrets.toml
```

Add your keys to the file:

```toml
YOUTUBE_API_KEY = "your_youtube_api_key"
GROQ_API_KEY = "your_groq_api_key"
```

### 5. Run the App

```bash
streamlit run app.py
```

---

## 📂 Project Structure

```
├── .streamlit/                     # Local secrets (ignored by Git)
├── notebooks/                      # Model training sandbox
│   └── model_training.ipynb
├── ai_analysis.py                  # ML inference and Groq LLM logic
├── api_youtube.py                  # YouTube Data API ingestion scripts
├── app.py                          # Main Streamlit UI/UX application
├── final_production_tokenizer.pkl  # NLP Text Tokenizer
├── youtube_production_model.keras  # Compiled Keras Model
├── requirements.txt                # Python dependencies
└── README.md
```

---

## Disclaimer

> This project requires active API keys for **YouTube Data v3** and **Groq** to function locally. Ensure your keys have sufficient quota before running.