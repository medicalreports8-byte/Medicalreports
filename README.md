# 🩺 MediScan AI — Medical Report Analyzer

AI-powered medical report analyzer built with Streamlit + Google Gemini API.

---

## ✅ Features (Level 1 + Level 2)

### Level 1
- 📄 Multi Report Upload (PDF + Image)
- 🟢🟡🔴 Severity Indicator for each value
- 🔤 Simple Language Toggle
- 📥 Download Summary as PDF

### Level 2
- 💬 Ask Questions on Report (AI Chatbot)
- 🥗 Diet & Lifestyle Suggestions
- 📊 Normal Range Comparison Chart
- 📋 Report History Tracker (compare multiple reports)

---

## 🛠️ Setup — VS Code (Recommended)

### Step 1: Install Python
Download from https://python.org (Python 3.10+)

### Step 2: Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### Step 3: Install Libraries
```bash
pip install -r requirements.txt
```

### Step 4: Get Gemini API Key
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

### Step 5: Run the App
```bash
streamlit run app.py
```

### Step 6: Open Browser
App opens at: http://localhost:8501

---

## 📁 Project Structure

```
ai_medical_analyzer/
├── app.py              ← Main application (all code here)
├── requirements.txt    ← All libraries
└── README.md           ← This file
```

---

## 💡 VS Code vs Google Colab

| | VS Code | Google Colab |
|--|---------|-------------|
| Streamlit UI | ✅ Works perfectly | ❌ Needs tunnel |
| File uploads | ✅ Easy | ⚠️ Complicated |
| Speed | ✅ Fast | ✅ Fast |
| Recommended | ✅ YES | Not recommended |

**Always use VS Code for Streamlit projects!**

---

## ⚠️ Disclaimer
This tool is for educational purposes only.
Always consult a qualified doctor for medical advice.
