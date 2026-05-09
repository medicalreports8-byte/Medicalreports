# ============================================================
# 🩺 Medical Report Analyzer — Claude Vision Version
# Supports: Text paste, Image upload, PDF upload
# pip install streamlit anthropic pypdf pillow
# streamlit run app.py
# ============================================================

import streamlit as st
import anthropic
import json
import base64
import io

# ── Page config ─────────────────────────────────────────────
st.set_page_config(page_title="Medical Report Analyzer", page_icon="🩺", layout="wide")

# ── Styles ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

* { font-family: 'Sora', sans-serif; }

[data-testid="stAppViewContainer"] { background: #080f1e; color: #e2e8f0; }
[data-testid="stHeader"]           { background: transparent; }
[data-testid="stSidebar"]          { background: #0c1628; border-right: 1px solid #1e2d45; }

.main-header {
  background: linear-gradient(135deg, #0d2137 0%, #061020 60%, #0a1a2e 100%);
  padding: 2.2rem 2.5rem; border-radius: 18px; margin-bottom: 2rem;
  border: 1px solid #1a3050;
  box-shadow: 0 0 60px #0ea5e910;
  position: relative; overflow: hidden;
}
.main-header::before {
  content:''; position:absolute; top:-60px; right:-60px;
  width:220px; height:220px; border-radius:50%;
  background: radial-gradient(circle, #0ea5e920 0%, transparent 70%);
}
.main-header h1 { color:#38bdf8; margin:0; font-size:2rem; font-weight:700; }
.main-header p  { color:#4a6580; margin-top:6px; font-size:0.9rem; }

.upload-box {
  background: #0e1c2f; border: 2px dashed #1e3a55; border-radius: 16px;
  padding: 1.5rem; text-align: center; margin-bottom: 1rem;
  transition: border-color 0.3s;
}
.upload-box:hover { border-color: #0ea5e9; }

.tab-label { font-size: 13px; font-weight: 600; }

.result-card {
  background: #0e1c2f; border-radius: 14px; padding: 1.4rem;
  border: 1px solid #1a3050; margin-bottom: 1rem;
  transition: border-color 0.2s;
}
.result-card:hover { border-color: #0ea5e9; }

.risk-high   { background:#ef444414; border:1px solid #ef444450; border-radius:12px; padding:14px 18px; margin-bottom:10px; }
.risk-medium { background:#f59e0b14; border:1px solid #f59e0b50; border-radius:12px; padding:14px 18px; margin-bottom:10px; }
.risk-low    { background:#22c55e14; border:1px solid #22c55e50; border-radius:12px; padding:14px 18px; margin-bottom:10px; }

.disclaimer {
  background:#fbbf2408; border:1px solid #fbbf2430;
  border-radius:12px; padding:14px 18px; color:#fbbf24; font-size:13px; margin-top:1.5rem;
}

.mode-card {
  background: #0e1c2f; border: 1px solid #1a3050; border-radius: 14px;
  padding: 1.2rem; text-align: center; cursor: pointer;
  transition: all 0.2s; margin-bottom: 0.5rem;
}
.mode-card.active { border-color: #0ea5e9; background: #0ea5e910; }

.stButton > button {
  background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%) !important;
  color: white !important; border: none !important; border-radius: 12px !important;
  font-weight: 700 !important; width: 100% !important; padding: 0.7rem !important;
  font-family: 'Sora', sans-serif !important; font-size: 15px !important;
  box-shadow: 0 4px 20px #0ea5e930 !important;
  transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

.stTextArea textarea {
  background: #0b1629 !important; color: #e2e8f0 !important;
  border: 1px solid #1e3a55 !important; border-radius: 12px !important;
  font-family: 'JetBrains Mono', monospace !important; font-size: 13px !important;
}

[data-testid="stFileUploader"] {
  background: #0e1c2f !important;
  border: 2px dashed #1e3a55 !important;
  border-radius: 14px !important; padding: 1rem !important;
}

.stTabs [data-baseweb="tab-list"] {
  background: #0c1628; border-radius: 12px; padding: 4px; gap: 4px;
}
.stTabs [data-baseweb="tab"] {
  background: transparent; border-radius: 10px; color: #64748b;
  font-weight: 600; font-size: 13px;
}
.stTabs [aria-selected="true"] {
  background: #0ea5e920 !important; color: #38bdf8 !important;
}

.metric-box {
  background: #0e1c2f; border: 1px solid #1a3050; border-radius: 14px;
  padding: 1.2rem; text-align: center;
}
.metric-label { color: #4a6580; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.metric-value { color: #38bdf8; font-size: 1.8rem; font-weight: 700; margin: 4px 0; }

.source-badge {
  display:inline-block; font-size:11px; font-weight:600; padding:2px 10px;
  border-radius:20px; margin-bottom:12px;
}
.source-text   { background:#6366f120; color:#818cf8; border:1px solid #6366f140; }
.source-image  { background:#ec489920; color:#f472b6; border:1px solid #ec489940; }
.source-pdf    { background:#f59e0b20; color:#fbbf24; border:1px solid #f59e0b40; }
</style>
""", unsafe_allow_html=True)

# ── System prompt ────────────────────────────────────────────
SYSTEM_PROMPT = """You are a highly experienced clinical AI assistant trained on medical literature.
Analyze the provided medical report (which may be text, an image of a report, or a PDF) and return ONLY a valid JSON object with exactly these keys:
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
ANTHROPIC_API_KEY = "your_anthropic_api_key_here"   # ← paste your Anthropic API key here

# ── Helper: encode image to base64 ──────────────────────────
def encode_image(file_bytes, media_type):
    return base64.standard_b64encode(file_bytes).decode("utf-8")

# ── Helper: extract text from PDF ───────────────────────────
def extract_pdf_text(file_bytes):
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        return None

# ── Core analyze function ────────────────────────────────────
def analyze_report(text=None, image_bytes=None, image_type=None, pdf_bytes=None):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Build message content
    content = []

    if image_bytes and image_type:
        # Image mode — use vision
        b64 = encode_image(image_bytes, image_type)
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": image_type,
                "data": b64
            }
        })
        content.append({"type": "text", "text": "Analyze this medical report image:"})

    elif pdf_bytes:
        # PDF mode — try text extraction first, fall back to base64 document
        extracted = extract_pdf_text(pdf_bytes)
        if extracted and len(extracted) > 50:
            content.append({"type": "text", "text": f"Analyze this medical report PDF (extracted text):\n\n{extracted}"})
        else:
            # Send as base64 document
            b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")
            content.append({
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": b64
                }
            })
            content.append({"type": "text", "text": "Analyze this medical report PDF:"})

    else:
        # Text mode
        if not text or not text.strip():
            raise ValueError("No content to analyze.")
        content.append({"type": "text", "text": f"Analyze this medical report:\n\n{text}"})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}]
    )

    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "")
    return json.loads(raw)

# ── UI helpers ───────────────────────────────────────────────
def risk_badge(risk):
    r = risk.lower()
    color = "#ef4444" if r == "high" else "#f59e0b" if r in ("moderate", "medium") else "#22c55e"
    return f'<span style="background:{color}22;color:{color};border-radius:6px;padding:2px 12px;font-size:11px;font-weight:700;margin-left:6px">{risk}</span>'

def score_svg(score):
    color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"
    r, cx, cy = 54, 64, 64
    circ = 2 * 3.14159 * r
    dash = (min(max(score, 0), 100) / 100) * circ
    return f"""<svg width="128" height="128" viewBox="0 0 128 128">
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#0e1c2f" stroke-width="10"/>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="10"
        stroke-dasharray="{dash:.1f} {circ:.1f}" stroke-linecap="round"
        transform="rotate(-90 {cx} {cy})"/>
      <text x="{cx}" y="{cy+8}" text-anchor="middle" fill="{color}" font-size="24" font-weight="bold"
        font-family="Sora,sans-serif">{score}</text>
    </svg><p style="color:#4a6580;font-size:11px;margin-top:-8px;text-align:center;font-weight:600;text-transform:uppercase;letter-spacing:0.05em">Health Score</p>"""

# ── Page Header ──────────────────────────────────────────────
st.markdown("""<div class="main-header">
  <h1>🩺 Medical Report Analyzer</h1>
  <p>AI-powered clinical analysis • Text • Image • PDF • Powered by Claude Sonnet</p>
</div>""", unsafe_allow_html=True)

# ── Input Mode Tabs ──────────────────────────────────────────
st.markdown("#### 📥 Choose your input method")
input_tab1, input_tab2, input_tab3 = st.tabs(["✏️ Paste Text", "🖼️ Upload Image", "📄 Upload PDF"])

report_text    = None
image_bytes    = None
image_type     = None
pdf_bytes      = None
input_source   = None

with input_tab1:
    st.markdown('<span class="source-badge source-text">TEXT INPUT</span>', unsafe_allow_html=True)
    report_text = st.text_area(
        "Paste your medical report below",
        height=240,
        placeholder="Paste your lab report, blood work results, radiology report, or any medical text here...",
    )
    if report_text and report_text.strip():
        input_source = "text"

with input_tab2:
    st.markdown('<span class="source-badge source-image">IMAGE INPUT</span>', unsafe_allow_html=True)
    st.markdown("Upload a **photo or scan** of your medical report (JPG, PNG, WEBP)")
    uploaded_img = st.file_uploader(
        "Upload report image",
        type=["jpg", "jpeg", "png", "webp"],
        key="img_uploader",
        label_visibility="collapsed"
    )
    if uploaded_img:
        image_bytes = uploaded_img.read()
        ext = uploaded_img.name.split(".")[-1].lower()
        type_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
        image_type = type_map.get(ext, "image/jpeg")
        input_source = "image"
        st.image(uploaded_img, caption="Uploaded Report", use_container_width=True)

with input_tab3:
    st.markdown('<span class="source-badge source-pdf">PDF INPUT</span>', unsafe_allow_html=True)
    st.markdown("Upload a **PDF** of your medical report or lab results")
    uploaded_pdf = st.file_uploader(
        "Upload PDF report",
        type=["pdf"],
        key="pdf_uploader",
        label_visibility="collapsed"
    )
    if uploaded_pdf:
        pdf_bytes = uploaded_pdf.read()
        input_source = "pdf"
        st.success(f"✅ PDF loaded: **{uploaded_pdf.name}** ({len(pdf_bytes)//1024} KB)")

st.markdown("---")

# ── Analyze Button ───────────────────────────────────────────
col_btn, col_info = st.columns([2, 3])
with col_btn:
    analyze_clicked = st.button("🧠 Analyze Medical Report")
with col_info:
    if input_source == "text":
        st.info("📝 Mode: Text analysis")
    elif input_source == "image":
        st.info("🖼️ Mode: Image / Vision analysis")
    elif input_source == "pdf":
        st.info("📄 Mode: PDF document analysis")
    else:
        st.warning("⬆️ Please provide a report above to analyze.")

if analyze_clicked:
    if not input_source:
        st.error("⚠️ Please provide a medical report (text, image, or PDF) before analyzing.")
    else:
        with st.spinner("🔬 Analyzing report with Claude AI..."):
            try:
                result = analyze_report(
                    text=report_text if input_source == "text" else None,
                    image_bytes=image_bytes if input_source == "image" else None,
                    image_type=image_type if input_source == "image" else None,
                    pdf_bytes=pdf_bytes if input_source == "pdf" else None,
                )
                st.session_state["result"] = result
                st.session_state["input_source"] = input_source
            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")

# ── Results ──────────────────────────────────────────────────
if "result" in st.session_state:
    result = st.session_state["result"]
    src    = st.session_state.get("input_source", "text")
    src_labels = {"text": "Text", "image": "Image", "pdf": "PDF"}
    src_cls    = {"text": "source-text", "image": "source-image", "pdf": "source-pdf"}

    st.markdown("---")
    st.markdown(f'<span class="source-badge {src_cls.get(src, "source-text")}">Analyzed from: {src_labels.get(src, src)}</span>', unsafe_allow_html=True)
    st.markdown("### 📊 Analysis Results")

    # ── Metrics row ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(score_svg(result.get("overall_health_score", 0)), unsafe_allow_html=True)
    with c2:
        urgency = result.get("urgency", "N/A")
        urg_color = "#ef4444" if urgency == "Urgent" else "#f59e0b" if urgency == "Soon" else "#22c55e"
        st.markdown(f'<div class="metric-box"><div class="metric-label">Urgency</div><div class="metric-value" style="color:{urg_color}">{urgency}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-box"><div class="metric-label">Conditions Detected</div><div class="metric-value">{len(result.get("predicted_conditions", []))}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-box"><div class="metric-label">Abnormalities</div><div class="metric-value">{len(result.get("abnormalities", []))}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tabs = st.tabs(["📋 Summary", "⚠️ Disease Risk", "🔍 Abnormalities", "🧬 Predictions", "💊 Recommendations"])

    with tabs[0]:
        st.markdown(f'<div class="result-card"><p style="line-height:1.9;font-size:15px;color:#cbd5e1">{result.get("summary", "")}</p></div>', unsafe_allow_html=True)

    with tabs[1]:
        risks = result.get("disease_risk", [])
        if not risks:
            st.success("✅ No disease risks identified.")
        for d in risks:
            r = d["risk"].lower()
            cls = "risk-high" if r == "high" else "risk-medium" if r in ("moderate", "medium") else "risk-low"
            st.markdown(
                f'<div class="{cls}"><strong style="color:#e2e8f0">{d["condition"]}</strong>'
                f'{risk_badge(d["risk"])}'
                f'<br><small style="color:#94a3b8;line-height:1.7">{d["reason"]}</small></div>',
                unsafe_allow_html=True
            )

    with tabs[2]:
        abnorms = result.get("abnormalities", [])
        if not abnorms:
            st.success("✅ No significant abnormalities detected.")
        for a in abnorms:
            st.markdown(
                f'<div class="result-card">'
                f'<strong style="color:#e2e8f0">{a["parameter"]}</strong> '
                f'<span style="background:#ef444420;color:#ef4444;border-radius:6px;padding:2px 10px;font-size:12px;font-weight:700">{a["value"]}</span>'
                f'<br><small style="color:#4a6580">Normal range: {a["normal_range"]}</small>'
                f'<br><span style="color:#94a3b8;font-size:13px;line-height:1.7">{a["interpretation"]}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    with tabs[3]:
        preds = result.get("predicted_conditions", [])
        if not preds:
            st.success("✅ No conditions predicted.")
        for c in preds:
            conf = c["confidence"].lower()
            cls = "risk-high" if conf == "high" else "risk-medium" if conf in ("moderate", "medium") else "risk-low"
            st.markdown(
                f'<div class="{cls}"><strong style="color:#e2e8f0">{c["condition"]}</strong>'
                f'{risk_badge(c["confidence"])}'
                f'<br><small style="color:#94a3b8;line-height:1.7">{c["basis"]}</small></div>',
                unsafe_allow_html=True
            )

    with tabs[4]:
        recs = result.get("recommendations", [])
        if not recs:
            st.info("No specific recommendations provided.")
        for i, rec in enumerate(recs, 1):
            st.markdown(
                f'<div class="result-card">'
                f'<span style="color:#0ea5e9;font-weight:700;margin-right:8px">{i:02d}.</span>'
                f'<span style="color:#cbd5e1;font-size:14px;line-height:1.8">{rec}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown(
        '<div class="disclaimer">⚠️ <strong>Disclaimer:</strong> This AI analysis is for informational purposes only and does not constitute medical advice. Always consult a qualified healthcare professional for diagnosis and treatment.</div>',
        unsafe_allow_html=True
    )
