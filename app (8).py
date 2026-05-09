# ============================================================
# 🩺 Medical Report Analyzer — Groq AI Edition
# Only needs: streamlit, Pillow   (requests is Python built-in)
# pip install streamlit Pillow
# streamlit run app.py
# Get your FREE Groq key at: https://console.groq.com
# ============================================================

import streamlit as st
import requests
import json
import base64
from PIL import Image

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Medical Report Analyzer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
[data-testid="stAppViewContainer"] { background: #f8f6f1; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding: 2rem 3rem 4rem; max-width: 960px; }

.hero {
    background: #1a1a2e; border-radius: 20px;
    padding: 2.5rem 3rem; margin-bottom: 2rem;
}
.hero-eyebrow {
    font-size: 11px; letter-spacing: 3px; text-transform: uppercase;
    color: #64b5f6; font-weight: 500; margin-bottom: 10px;
}
.hero h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem; color: #f1f5f9; margin: 0 0 8px; line-height: 1.15;
}
.hero p { color: #94a3b8; font-size: 14px; margin: 0; font-weight: 300; }

.card {
    background: #fff; border-radius: 16px; padding: 1.6rem 1.8rem;
    border: 1px solid #e8e4dc; margin-bottom: 1.2rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.card-title {
    font-size: 11px; letter-spacing: 2.5px; text-transform: uppercase;
    color: #94a3b8; font-weight: 600; margin-bottom: 1rem;
}

.metrics-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 1.4rem; }
.metric-tile {
    background: #fff; border: 1px solid #e8e4dc; border-radius: 14px;
    padding: 1.2rem 1.4rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.mt-label {
    font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
    color: #94a3b8; font-weight: 600; margin-bottom: 6px;
}
.mt-value { font-family: 'DM Serif Display', serif; font-size: 2rem; line-height: 1; }
.mt-sub   { font-size: 12px; color: #94a3b8; margin-top: 4px; }

.score-high   { color: #16a34a; }
.score-medium { color: #d97706; }
.score-low    { color: #dc2626; }

.urgency-routine { color: #16a34a; font-family: 'DM Serif Display', serif; font-size: 1.8rem; }
.urgency-soon    { color: #d97706; font-family: 'DM Serif Display', serif; font-size: 1.8rem; }
.urgency-urgent  { color: #dc2626; font-family: 'DM Serif Display', serif; font-size: 1.8rem; }

.progress-wrap { height: 6px; background: #e8e4dc; border-radius: 99px; margin-top: 8px; overflow: hidden; }
.progress-fill { height: 6px; border-radius: 99px; }

.risk-row {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 11px 0; border-bottom: 1px solid #f1ede6;
}
.risk-row:last-child { border-bottom: none; }
.risk-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; margin-top: 5px; }
.dot-high      { background: #ef4444; box-shadow: 0 0 8px #ef444455; }
.dot-moderate  { background: #f59e0b; box-shadow: 0 0 8px #f59e0b55; }
.dot-low       { background: #22c55e; box-shadow: 0 0 8px #22c55e55; }
.dot-predicted { background: #6366f1; box-shadow: 0 0 8px #6366f155; }

.risk-name   { font-weight: 500; font-size: 14px; color: #1a1a2e; }
.risk-reason { font-size: 12px; color: #64748b; margin-top: 2px; line-height: 1.5; }

.badge {
    display: inline-block; font-size: 10px; font-weight: 600;
    letter-spacing: 1px; padding: 2px 9px; border-radius: 99px;
    vertical-align: middle; margin-left: 6px;
}
.badge-high      { background: #fef2f2; color: #dc2626; }
.badge-moderate  { background: #fffbeb; color: #d97706; }
.badge-low       { background: #f0fdf4; color: #16a34a; }
.badge-confident { background: #eff6ff; color: #2563eb; }

.abnorm-item {
    background: #faf9f7; border: 1px solid #e8e4dc;
    border-radius: 12px; padding: 12px 16px; margin-bottom: 8px;
}
.abnorm-header { display: flex; justify-content: space-between; align-items: center; }
.abnorm-param  { font-weight: 500; font-size: 14px; color: #1a1a2e; }
.abnorm-val    { font-size: 12px; background: #fef2f2; color: #dc2626; border-radius: 6px; padding: 2px 10px; font-weight: 600; }
.abnorm-range  { font-size: 12px; color: #94a3b8; margin-top: 4px; }
.abnorm-interp { font-size: 13px; color: #475569; margin-top: 6px; line-height: 1.5; }

.rec-item {
    display: flex; gap: 12px; align-items: flex-start;
    padding: 10px 14px; background: #faf9f7;
    border: 1px solid #e8e4dc; border-radius: 10px;
    margin-bottom: 8px; font-size: 14px; color: #334155; line-height: 1.6;
}
.rec-arrow { color: #1a1a2e; font-weight: 700; flex-shrink: 0; margin-top: 1px; }

.stButton > button {
    background: #1a1a2e !important; color: #f1f5f9 !important;
    border: none !important; border-radius: 12px !important;
    padding: 0.6rem 2rem !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important; font-size: 15px !important; width: 100% !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

.stTextArea textarea {
    background: #fff !important; border: 1px solid #e8e4dc !important;
    border-radius: 12px !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important; color: #334155 !important; line-height: 1.6 !important;
}

.disclaimer {
    background: #fffbeb; border: 1px solid #fde68a; border-radius: 12px;
    padding: 12px 16px; font-size: 12px; color: #78350f;
    line-height: 1.6; margin-top: 1.2rem;
}

.img-note {
    background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px;
    padding: 10px 14px; font-size: 12px; color: #1e40af; margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)


# ── Constants ─────────────────────────────────────────────────
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"   # best free Groq model for text

# Vision model — used only when image is uploaded
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

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
Return ONLY valid JSON. No markdown fences, no preamble, no trailing text."""


# ── Core API call ─────────────────────────────────────────────
def call_groq(messages: list, api_key: str, model: str = GROQ_MODEL) -> dict:
    """POST to Groq OpenAI-compatible endpoint and parse JSON result."""
    resp = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "max_tokens": 1500,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT}
            ] + messages
        },
        timeout=60
    )
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"].strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def analyze_text(text: str, api_key: str) -> dict:
    """Analyze plain text report via Groq."""
    return call_groq(
        [{"role": "user", "content": f"Analyze this medical report:\n\n{text}"}],
        api_key,
        model=GROQ_MODEL
    )


def analyze_image(image_bytes: bytes, media_type: str, api_key: str) -> dict:
    """Analyze an uploaded image via Groq vision model."""
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{media_type};base64,{b64}"
    messages = [{
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {"url": data_url}
            },
            {
                "type": "text",
                "text": "This is a medical report image. Extract all visible text and findings, then perform a full clinical analysis."
            }
        ]
    }]
    return call_groq(messages, api_key, model=GROQ_VISION_MODEL)


# ── Render helpers ────────────────────────────────────────────
def badge_cls(level: str) -> str:
    l = level.lower()
    return "badge-high" if l == "high" else "badge-moderate" if l == "moderate" else "badge-low"

def dot_cls(level: str) -> str:
    l = level.lower()
    return "dot-high" if l == "high" else "dot-moderate" if l == "moderate" else "dot-low"

def score_cls(s: int) -> str:
    return "score-high" if s >= 70 else "score-medium" if s >= 40 else "score-low"

def fill_color(s: int) -> str:
    return "#16a34a" if s >= 70 else "#d97706" if s >= 40 else "#dc2626"


def render_results(result: dict):
    score   = max(0, min(100, result.get("overall_health_score", 0)))
    urgency = result.get("urgency", "Routine")
    preds   = result.get("predicted_conditions", [])

    # ── Metric tiles
    st.markdown(f"""
    <div class="metrics-row">
      <div class="metric-tile">
        <div class="mt-label">Health Score</div>
        <div class="mt-value {score_cls(score)}">{score}</div>
        <div class="progress-wrap">
          <div class="progress-fill" style="width:{score}%;background:{fill_color(score)}"></div>
        </div>
        <div class="mt-sub">out of 100</div>
      </div>
      <div class="metric-tile">
        <div class="mt-label">Urgency</div>
        <div class="urgency-{urgency.lower()}">{urgency}</div>
      </div>
      <div class="metric-tile">
        <div class="mt-label">Conditions Found</div>
        <div class="mt-value" style="color:#1a1a2e">{len(preds)}</div>
        <div class="mt-sub">predicted</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Result tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Summary", "⚠️ Disease Risk", "🔍 Abnormalities", "🧬 Predictions", "💊 Recommendations"
    ])

    with tab1:
        st.markdown(f"""
        <div class="card">
          <div class="card-title">Clinical Summary</div>
          <p style="font-size:15px;color:#334155;line-height:1.8;margin:0">
            {result.get("summary", "No summary available.")}
          </p>
        </div>""", unsafe_allow_html=True)

    with tab2:
        risks = result.get("disease_risk", [])
        if not risks:
            st.info("No disease risks identified.")
        else:
            rows = "".join(f"""
            <div class="risk-row">
              <div class="risk-dot {dot_cls(d.get('risk',''))}"></div>
              <div>
                <div class="risk-name">{d.get('condition','')}
                  <span class="badge {badge_cls(d.get('risk',''))}">{d.get('risk','').upper()}</span>
                </div>
                <div class="risk-reason">{d.get('reason','')}</div>
              </div>
            </div>""" for d in risks)
            st.markdown(
                f'<div class="card"><div class="card-title">Disease Risk Assessment</div>{rows}</div>',
                unsafe_allow_html=True
            )

    with tab3:
        abnorms = result.get("abnormalities", [])
        if not abnorms:
            st.success("✅ No significant abnormalities detected.")
        else:
            html = '<div class="card"><div class="card-title">Abnormal Parameters</div>'
            for a in abnorms:
                html += f"""
                <div class="abnorm-item">
                  <div class="abnorm-header">
                    <span class="abnorm-param">{a.get('parameter','')}</span>
                    <span class="abnorm-val">{a.get('value','')}</span>
                  </div>
                  <div class="abnorm-range">Normal range: {a.get('normal_range','')}</div>
                  <div class="abnorm-interp">{a.get('interpretation','')}</div>
                </div>"""
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)

    with tab4:
        if not preds:
            st.info("No conditions predicted.")
        else:
            rows = "".join(f"""
            <div class="risk-row">
              <div class="risk-dot dot-predicted"></div>
              <div>
                <div class="risk-name">{c.get('condition','')}
                  <span class="badge badge-confident">{c.get('confidence','').upper()} CONFIDENCE</span>
                </div>
                <div class="risk-reason">{c.get('basis','')}</div>
              </div>
            </div>""" for c in preds)
            st.markdown(
                f'<div class="card"><div class="card-title">Predicted Conditions</div>{rows}</div>',
                unsafe_allow_html=True
            )

    with tab5:
        recs = result.get("recommendations", [])
        if not recs:
            st.info("No recommendations generated.")
        else:
            items = "".join(
                f'<div class="rec-item"><span class="rec-arrow">→</span> {r}</div>'
                for r in recs
            )
            st.markdown(
                f'<div class="card"><div class="card-title">Clinical Recommendations</div>{items}</div>',
                unsafe_allow_html=True
            )

    st.markdown("""
    <div class="disclaimer">
      ⚠️ <strong>Disclaimer:</strong> This AI analysis is for informational purposes only and does not
      constitute medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional.
    </div>""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    api_key_input = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Get your FREE key at console.groq.com"
    )
    if api_key_input:
        st.session_state["api_key"] = api_key_input
        st.success("Groq API key saved ✓")

    st.markdown("---")
    st.markdown("""
**How to use:**
1. Get a free key at [console.groq.com](https://console.groq.com)
2. Paste your `gsk_...` key above
3. Choose text or image input
4. Click **Analyze Report**
5. Browse the result tabs
    """)
    st.markdown("---")
    st.caption("Powered by Groq · LLaMA 3.3 70B · Free tier available")


# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">AI · CLINICAL ANALYSIS · GEN AI · GROQ</div>
  <h1>Medical Report Analyzer</h1>
  <p>Paste text or upload a report image — Groq + LLaMA delivers structured clinical insights instantly.</p>
</div>
""", unsafe_allow_html=True)


# ── Input ─────────────────────────────────────────────────────
input_mode = st.radio(
    "Input method",
    ["✏️ Paste text", "🖼️ Upload image"],
    horizontal=True,
    label_visibility="collapsed"
)

report_text   = ""
uploaded_file = None

if input_mode == "✏️ Paste text":
    report_text = st.text_area(
        "Report text",
        height=220,
        placeholder="Paste your lab report, blood work, radiology findings, or any medical report here…",
        label_visibility="collapsed"
    )
else:
    uploaded_file = st.file_uploader(
        "Upload report image",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded report preview", use_container_width=True)
        st.markdown(
            '<div class="img-note">ℹ️ Image will be analyzed using Groq vision model (Llama 4 Scout).</div>',
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Analyze button ────────────────────────────────────────────
if st.button("🧠 Analyze Report", use_container_width=True):
    saved_key = st.session_state.get("api_key", "")

    if not saved_key:
        st.error("⚠️ Enter your Groq API key in the sidebar first.")
    elif input_mode == "✏️ Paste text" and not report_text.strip():
        st.error("⚠️ Please paste some report text before analyzing.")
    elif input_mode == "🖼️ Upload image" and uploaded_file is None:
        st.error("⚠️ Please upload an image before analyzing.")
    else:
        with st.spinner("🔬 Analyzing report with Groq AI…"):
            try:
                if input_mode == "✏️ Paste text":
                    result = analyze_text(report_text, saved_key)
                else:
                    uploaded_file.seek(0)
                    img_bytes = uploaded_file.read()
                    ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
                    media_map = {
                        "jpg": "image/jpeg", "jpeg": "image/jpeg",
                        "png": "image/png",  "webp": "image/webp"
                    }
                    result = analyze_image(
                        img_bytes,
                        media_map.get(ext, "image/jpeg"),
                        saved_key
                    )

                st.session_state["result"] = result
                st.success("✅ Analysis complete!")

            except requests.exceptions.HTTPError as e:
                try:
                    err_detail = e.response.json().get("error", {}).get("message", "")
                except Exception:
                    err_detail = e.response.text[:200]
                st.error(f"Groq API error {e.response.status_code}: {err_detail or 'Check your API key.'}")
            except json.JSONDecodeError:
                st.error("Unexpected response format from Groq. Please try again.")
            except Exception as e:
                st.error(f"Error: {e}")

# ── Show results ──────────────────────────────────────────────
if "result" in st.session_state:
    st.markdown("---")
    render_results(st.session_state["result"])
