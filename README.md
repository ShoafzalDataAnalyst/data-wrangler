# 🧹 AI-Assisted Data Wrangler & Visualizer

> Coursework for **Data Wrangling and Visualization (5COSC038C)**

A Streamlit app that lets users upload a dataset and interactively clean, transform, and visualize it — ending with an exported cleaned dataset and a transformation report.

---

## 🚀 Live App

👉 **[Click here to open the app](#)** *(replace with your Streamlit Cloud URL)*

---

## 📁 Project Structure

```
data_wrangler/
├── app.py                  # Main entry point
├── requirements.txt
├── README.md
├── AI_USAGE.md
├── pages/
│   ├── page_a_upload.py    # Upload & Overview
│   ├── page_b_cleaning.py  # Cleaning Studio
│   ├── page_c_viz.py       # Visualization Builder
│   └── page_d_export.py    # Export & Report
├── utils/
│   └── helpers.py          # Shared utilities
└── sample_data/
    ├── dataset1.csv
    └── dataset2.xlsx
```

---

## ⚙️ How to Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/data-wrangler.git
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

---

## 🤖 AI Assistant

The app includes an optional Claude-powered AI assistant (toggle it in the sidebar).  
To enable it, set your Anthropic API key as an environment variable:
```bash
export ANTHROPIC_API_KEY=your_key_here
```
Or add it to Streamlit Cloud secrets.

---

## 📦 Sample Datasets

Two sample datasets are included in `sample_data/` for demonstration:
- `dataset1.csv` — *description*
- `dataset2.xlsx` — *description*

---

## 👥 Team

- Student 1 name
- Student 2 name
