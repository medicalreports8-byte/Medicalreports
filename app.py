# ============================================================
# 🩺 Medical Report Analyzer — Single File Version
# Run:  pip install streamlit anthropic PyMuPDF Pillow pytesseract
#       streamlit run app.py
# ============================================================

import streamlit as st
import anthropic
import base64
import json
import fitz          # PyMuPDF
from PIL import Image
import pytesseract
import io

# ── Page config ─────────────────────────────────────────────
st.set_page_config(page_title="Medical Report Analyzer", page_icon="🩺", layout="wide")

# ── Styles ───────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f172a; color: #e2e8f0; }
[data-testid="stHeader"]           { background: transparent; }
.main-header {
  background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
  padding: 2rem; border-radius: 14px; margin-bottom: 2rem; border: 1px solid #1e293b;
}
.result-card {
  background: #1e293b; border-radius: 14px; padding: 1.5rem;
  border: 1px solid #334155; margin-bottom: 1rem;
}
.risk-high   { background:#ef444422; border:1px solid #ef444466; border-radius:10px; padding:12px 16px; margin-bottom:8px; }
.risk-medium { background:#f59e0b22; border:1px solid #f59e0b66; border-radius:10px; padding:12px 16px; margin-bottom:8px; }
.risk-low    { background:#22c55e22; border:1px solid #22c55e66; border-radius:10px; padding:12px 16px; margin-bottom:8px; }
.disclaimer  {
  background:#fbbf2411; border:1px solid #fbbf2444;
  border-radius:10px; padding:12px 16px; color:#fbbf24; font-size:13px;
}
.stButton > button {
  background: linear-gradient(135deg, #0ea5e9, #2563eb) !important;
  color: white !important; border: none !important; border-radius: 10px !important;
  font-weight: 700 !important; width: 100% !important;
}
.stTextArea textarea, .stTextInput input {
  background: #0f172a !important; color: #e2e8f0 !important;
  border: 1px solid #334155 !important; border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── System prompt ────────────────────────────────────────────
SYSTEM_PROMPT = """You are a highly experienced clinical AI assistant trained on medical literature.
Analyze the provided medical report and return ONLY a valid JSON object with exactly these keys:
{
  "summary": "A clear 3-5 sentence plain-language summary of the report findings.",
  "disease_risk": [
    {"condition": "Condition Name", "risk": "High|Moderate|Low", "reason": "Brief explanation"}
  ],
  "abnormalities": [
    {"parameter": "Parameter name", "value": "Reported value", "normal_range": "Normal range", "interpretation": "What it means"}
  ],
  "predicted_conditions": [
    {"condition": "Condition", "confidence": "High|Moderate|Low", "basis": "Why this is predicted"}
  ],
  "recommendations": ["Actionable recommendation 1", "Actionable recommendation 2"],
  "overall_health_score": 75,
  "urgency": "Routine|Soon|Urgent"
}
Return ONLY valid JSON. No markdown fences, no preamble."""

# ── API Key ──────────────────────────────────────────────────
ANTHROPIC_API_KEY = "sk-ant-your-key-here"   # ← paste your key here

# ── Helpers ──────────────────────────────────────────────────
def encode_b64(data):
    return base64.standard_b64encode(data).decode("utf-8")

def analyze_report(text=None, file_bytes=None, file_type=None):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    if file_bytes and file_type:
        if file_type == "application/pdf":
            content = [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": encode_b64(file_bytes)}},
                {"type": "text", "text": "Analyze this medical report and return the structured JSON."}
            ]
        else:
            content = [
                {"type": "image", "source": {"type": "base64", "media_type": file_type, "data": encode_b64(file_bytes)}},
                {"type": "text", "text": "Analyze this medical report image and return the structured JSON."}
            ]
    else:
        content = f"Analyze this medical report:\n\n{text}"

    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}]
    )
    raw = msg.content[0].text.strip().replace("```json", "").replace("```", "")
    return json.loads(raw)

def risk_badge(risk):
    r = risk.lower()
    color = "#ef4444" if r == "high" else "#f59e0b" if r == "moderate" else "#22c55e"
    return f'<span style="background:{color}33;color:{color};border-radius:6px;padding:2px 12px;font-size:12px;font-weight:700">{risk}</span>'

def score_svg(score):
    color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"
    r, cx, cy = 54, 64, 64
    circ = 2 * 3.14159 * r
    dash = (min(max(score, 0), 100) / 100) * circ
    return f"""<svg width="128" height="128" viewBox="0 0 128 128">
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#1e293b" stroke-width="10"/>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="10"
        stroke-dasharray="{dash:.1f} {circ:.1f}" stroke-linecap="round"
        transform="rotate(-90 {cx} {cy})"/>
      <text x="{cx}" y="{cy+8}" text-anchor="middle" fill="{color}" font-size="24" font-weight="bold">{score}</text>
    </svg><p style="color:#94a3b8;font-size:12px;margin-top:-8px;text-align:center">Health Score</p>"""

# ── UI ───────────────────────────────────────────────────────
st.markdown("""<div class="main-header">
  <h1 style="color:#38bdf8;margin:0;font-size:2rem">🩺 Medical Report Analyzer</h1>
  <p style="color:#64748b;margin-top:6px">AI-powered clinical analysis • Powered by Claude Sonnet 4</p>
</div>""", unsafe_allow_html=True)

# Input area
col1, col2 = st.columns(2)
with col1:
    st.markdown("**📁 Upload Report** (PDF / Image / Text)")
    uploaded = st.file_uploader("", type=["pdf", "png", "jpg", "jpeg", "txt"], label_visibility="collapsed")
with col2:
    st.markdown("**✏️ Or Paste Report Text**")
    report_text = st.text_area("", height=150, placeholder="Paste lab report, blood work, radiology report...", label_visibility="collapsed")

if st.button("🧠 Analyze Medical Report"):
    with st.spinner("🔬 Analyzing report with AI..."):
        try:
            result = None
            if uploaded:
                fbytes = uploaded.read()
                if uploaded.type == "text/plain":
                    result = analyze_report(text=fbytes.decode("utf-8"))
                else:
                    result = analyze_report(file_bytes=fbytes, file_type=uploaded.type)
            elif report_text.strip():
                result = analyze_report(text=report_text)
            else:
                st.error("⚠️ Please upload a file or paste report text.")
            if result:
                st.session_state["result"] = result
        except Exception as e:
            st.error(f"Analysis failed: {e}")

# ── Results ──────────────────────────────────────────────────
if "result" in st.session_state:
    result = st.session_state["result"]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(score_svg(result.get("overall_health_score", 0)), unsafe_allow_html=True)
    with c2:
        st.metric("Urgency", result.get("urgency", "N/A"))
    with c3:
        st.metric("Conditions Detected", len(result.get("predicted_conditions", [])))

    tabs = st.tabs(["📋 Summary", "⚠️ Disease Risk", "🔍 Abnormalities", "🧬 Predictions", "💊 Recommendations"])

    with tabs[0]:
        st.markdown(f'<div class="result-card"><p style="line-height:1.8;font-size:15px">{result.get("summary", "")}</p></div>', unsafe_allow_html=True)

    with tabs[1]:
        for d in result.get("disease_risk", []):
            r = d["risk"].lower()
            cls = "risk-high" if r == "high" else "risk-medium" if r == "moderate" else "risk-low"
            st.markdown(f'<div class="{cls}"><strong>{d["condition"]}</strong> {risk_badge(d["risk"])}<br><small style="color:#94a3b8">{d["reason"]}</small></div>', unsafe_allow_html=True)

    with tabs[2]:
        if not result.get("abnormalities"):
            st.success("✅ No significant abnormalities detected.")
        for a in result.get("abnormalities", []):
            st.markdown(f'<div class="result-card"><strong>{a["parameter"]}</strong> <span style="background:#ef444422;color:#ef4444;border-radius:6px;padding:2px 10px;font-size:12px">{a["value"]}</span><br><small style="color:#64748b">Normal: {a["normal_range"]}</small><br><span style="color:#94a3b8;font-size:13px">{a["interpretation"]}</span></div>', unsafe_allow_html=True)

    with tabs[3]:
        for c in result.get("predicted_conditions", []):
            conf = c["confidence"].lower()
            cls = "risk-high" if conf == "high" else "risk-medium" if conf == "moderate" else "risk-low"
            st.markdown(f'<div class="{cls}"><strong>{c["condition"]}</strong> {risk_badge(c["confidence"])}<br><small style="color:#94a3b8">{c["basis"]}</small></div>', unsafe_allow_html=True)

    with tabs[4]:
        for rec in result.get("recommendations", []):
            st.markdown(f'<div class="result-card">→ {rec}</div>', unsafe_allow_html=True)

    st.markdown('<div class="disclaimer">⚠️ <strong>Disclaimer:</strong> This AI analysis is for informational purposes only. Always consult a qualified healthcare professional.</div>', unsafe_allow_html=True)
