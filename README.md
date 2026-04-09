# 🧹 AI-Assisted Data Wrangler & Visualizer | Streamlit

> Coursework for **Data Wrangling and Visualization (5COSC038C)**

A Streamlit app that lets users upload a dataset and interactively clean, transform, and visualize it — ending with an exported cleaned dataset and a transformation report.

---

## 🚀 Live App

👉 https://data-wrangler-6e9qvnawus4t8wfexgyt2h.streamlit.app/

---

## 📁 Project Structure

```
data_wrangler/
├── app.py                  # Main entry point
├── requirements.txt
├── README.md
├── AI_USAGE.md
├── sections/
│   ├── page_a_upload.py    # Upload & Overview
│   ├── page_b_cleaning.py  # Cleaning Studio
│   ├── page_c_viz.py       # Visualization Builder
│   ├── page_d_export.py    # Export & Report
│   └── page_e_ai.py        # AI Assistant
├── utils/
│   └── helpers.py          # Shared utilities
└── sample_data/
    ├── sales_data.csv
    └── hr_data.xlsx
```

---

## ⚙️ How to Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/ShoafzalDataAnalyst/data-wrangler.git
cd data-wrangler
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
streamlit run app.py
```

Or just open the live app in your browser:
https://data-wrangler-6e9qvnawus4t8wfexgyt2h.streamlit.app/

---

## 🤖 AI Assistant

The app includes an optional Claude-powered AI assistant (toggle it in the sidebar).  
To enable it, enter your Anthropic API key directly in the app UI, or add it to `.streamlit/secrets.toml`:

```
ANTHROPIC_API_KEY = "sk-ant-..."
```

> Note: The AI assistant requires a paid Anthropic API key (minimum $5 credits at console.anthropic.com). The app works fully without it.

---

## 📦 Sample Datasets

Two sample datasets are included in `sample_data/` for demonstration:

- `sales_data.csv` — 2030 rows, 13 columns, mixed types, intentional missing values
- `hr_data.xlsx` — 1525 rows, 12 columns, mixed types, intentional missing values