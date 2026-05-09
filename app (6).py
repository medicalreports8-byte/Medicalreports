# ============================================================
# 🩺 Medical Report Analyzer — Claude AI Edition
# pip install streamlit anthropic pillow
# streamlit run app.py
# ============================================================

import streamlit as st
import anthropic
import json
import base64
from PIL import Image
import io

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Medical Report Analyzer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: #f8f6f1;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding: 2.5rem 3rem 4rem; max-width: 960px; }

/* ── Header ── */
.hero {
    background: #1a1a2e;
    border-radius: 20px;
    padding: 2.8rem 3rem;
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 280px; height: 280px;
    border-radius: 50%;
    background: radial-gradient(circle, #16213e88 0%, transparent 70%);
}
.hero-eyebrow {
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #64b5f6;
    font-weight: 500;
    margin-bottom: 10px;
}
.hero h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem;
    color: #f1f5f9;
    margin: 0 0 10px;
    line-height: 1.15;
}
.hero p {
    color: #94a3b8;
    font-size: 15px;
    margin: 0;
    font-weight: 300;
}

/* ── Cards ── */
.card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.8rem 2rem;
    border: 1px solid #e8e4dc;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.card-title {
    font-size: 11px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #94a3b8;
    font-weight: 600;
    margin-bottom: 1.2rem;
}

/* ── Metric tiles ── */
.metrics-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 14px;
    margin-bottom: 1.5rem;
}
.metric-tile {
    background: #ffffff;
    border: 1px solid #e8e4dc;
    border-radius: 14px;
    padding: 1.4rem 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.metric-tile .mt-label {
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #94a3b8;
    font-weight: 600;
    margin-bottom: 8px;
}
.metric-tile .mt-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    line-height: 1;
}
.metric-tile .mt-sub {
    font-size: 12px;
    color: #94a3b8;
    margin-top: 4px;
}

/* ── Score arc ── */
.score-high   { color: #16a34a; }
.score-medium { color: #d97706; }
.score-low    { color: #dc2626; }

/* ── Progress bar ── */
.progress-wrap { height: 6px; background: #e8e4dc; border-radius: 99px; margin-top: 10px; overflow: hidden; }
.progress-fill { height: 6px; border-radius: 99px; }

/* ── Risk badges ── */
.risk-row {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid #f1ede6;
}
.risk-row:last-child { border-bottom: none; }
.risk-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
    margin-top: 5px;
}
.dot-high     { background: #ef4444; box-shadow: 0 0 8px #ef444455; }
.dot-moderate { background: #f59e0b; box-shadow: 0 0 8px #f59e0b55; }
.dot-low      { background: #22c55e; box-shadow: 0 0 8px #22c55e55; }
.risk-name    { font-weight: 500; font-size: 14px; color: #1a1a2e; }
.risk-reason  { font-size: 12px; color: #64748b; margin-top: 2px; line-height: 1.5; }
.badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 2px 9px;
    border-radius: 99px;
    vertical-align: middle;
    margin-left: 6px;
}
.badge-high     { background: #fef2f2; color: #dc2626; }
.badge-moderate { background: #fffbeb; color: #d97706; }
.badge-low      { background: #f0fdf4; color: #16a34a; }
.badge-confident { background: #eff6ff; color: #2563eb; }

/* ── Abnormalities ── */
.abnorm-item {
    background: #faf9f7;
    border: 1px solid #e8e4dc;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
}
.abnorm-header { display: flex; justify-content: space-between; align-items: center; }
.abnorm-param { font-weight: 500; font-size: 14px; color: #1a1a2e; }
.abnorm-val   { font-size: 12px; background: #fef2f2; color: #dc2626; border-radius: 6px; padding: 2px 10px; font-weight: 600; }
.abnorm-range { font-size: 12px; color: #94a3b8; margin-top: 4px; }
.abnorm-interp { font-size: 13px; color: #475569; margin-top: 6px; line-height: 1.5; }

/* ── Recommendations ── */
.rec-item {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    padding: 10px 14px;
    background: #faf9f7;
    border: 1px solid #e8e4dc;
    border-radius: 10px;
    margin-bottom: 8px;
    font-size: 14px;
    color: #334155;
    line-height: 1.6;
}
.rec-arrow {
    color: #1a1a2e;
    font-weight: 700;
    flex-shrink: 0;
    margin-top: 1px;
}

/* ── Urgency colors ── */
.urgency-routine { color: #16a34a; font-family: 'DM Serif Display', serif; font-size: 1.8rem; }
.urgency-soon    { color: #d97706; font-family: 'DM Serif Display', serif; font-size: 1.8rem; }
.urgency-urgent  { color: #dc2626; font-family: 'DM Serif Display', serif; font-size: 1.8rem; }

/* ── Streamlit widget overrides ── */
.stButton > button {
    background: #1a1a2e !important;
    color: #f1f5f9 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 15px !important;
    letter-spacing: 0.3px !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

.stTextArea textarea {
    background: #fff !important;
    border: 1px solid #e8e4dc !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    color: #334155 !important;
    line-height: 1.6 !important;
}

.stFileUploader > div {
    border: 2px dashed #d1cdc4 !important;
    border-radius: 14px !important;
    background: #faf9f7 !important;
}

div[data-testid="stTabs"] button {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}

.stSpinner > div { border-top-color: #1a1a2e !important; }

/* ── Disclaimer ── */
.disclaimer {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 12px;
    color: #78350f;
    line-height: 1.6;
    margin-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────
def get_client():
    api_key = st.session_state.get("api_key", "")
    if not api_key:
        raise ValueError("Please enter your Anthropic API key in the sidebar.")
    return anthropic.Anthropic(api_key=api_key)


SYSTEM_PROMPT = """You are a highly experienced clinical AI assistant trained on medical literature.
Analyze the provided medical report (text or image) and return ONLY a valid JSON object with exactly these keys:
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


def analyze_text(text: str) -> dict:
    client = get_client()
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Analyze this medical report:\n\n{text}"}]
    )
    raw = msg.content[0].text.strip().replace("```json", "").replace("```", "")
    return json.loads(raw)


def analyze_image(image_bytes: bytes, media_type: str) -> dict:
    client = get_client()
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": b64}
                },
                {
                    "type": "text",
                    "text": "Analyze this medical report image. Extract all visible text and findings, then perform your clinical analysis."
                }
            ]
        }]
    )
    raw = msg.content[0].text.strip().replace("```json", "").replace("```", "")
    return json.loads(raw)


def risk_dot_class(risk: str) -> str:
    r = risk.lower()
    return "dot-high" if r == "high" else "dot-moderate" if r == "moderate" else "dot-low"


def badge_class(level: str) -> str:
    l = level.lower()
    return "badge-high" if l == "high" else "badge-moderate" if l == "moderate" else "badge-low"


def score_color(score: int) -> str:
    if score >= 70: return "score-high"
    if score >= 40: return "score-medium"
    return "score-low"


def score_fill_color(score: int) -> str:
    if score >= 70: return "#16a34a"
    if score >= 40: return "#d97706"
    return "#dc2626"


def render_results(result: dict):
    score = max(0, min(100, result.get("overall_health_score", 0)))
    urgency = result.get("urgency", "Routine")
    conditions = result.get("predicted_conditions", [])
    urgency_cls = f"urgency-{urgency.lower()}"
    sc = score_color(score)
    fill_color = score_fill_color(score)

    # ── Metric tiles ─────────────────────────────────────────
    st.markdown(f"""
    <div class="metrics-row">
      <div class="metric-tile">
        <div class="mt-label">Health Score</div>
        <div class="mt-value {sc}">{score}</div>
        <div class="progress-wrap">
          <div class="progress-fill" style="width:{score}%;background:{fill_color}"></div>
        </div>
        <div class="mt-sub">out of 100</div>
      </div>
      <div class="metric-tile">
        <div class="mt-label">Urgency</div>
        <div class="{urgency_cls}">{urgency}</div>
      </div>
      <div class="metric-tile">
        <div class="mt-label">Conditions Found</div>
        <div class="mt-value" style="color:#1a1a2e">{len(conditions)}</div>
        <div class="mt-sub">predicted</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Result tabs ──────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Summary", "⚠️ Disease Risk", "🔍 Abnormalities", "🧬 Predictions", "💊 Recommendations"
    ])

    with tab1:
        st.markdown(f"""
        <div class="card">
          <div class="card-title">Clinical Summary</div>
          <p style="font-size:15px;color:#334155;line-height:1.8;margin:0">{result.get("summary", "No summary available.")}</p>
        </div>""", unsafe_allow_html=True)

    with tab2:
        disease_risks = result.get("disease_risk", [])
        if not disease_risks:
            st.info("No disease risks identified.")
        else:
            rows = ""
            for d in disease_risks:
                dot = risk_dot_class(d.get("risk", ""))
                bdg = badge_class(d.get("risk", ""))
                rows += f"""
                <div class="risk-row">
                  <div class="risk-dot {dot}"></div>
                  <div>
                    <div class="risk-name">{d.get("condition", "")}
                      <span class="badge {bdg}">{d.get("risk","").upper()}</span>
                    </div>
                    <div class="risk-reason">{d.get("reason", "")}</div>
                  </div>
                </div>"""
            st.markdown(f'<div class="card"><div class="card-title">Disease Risk Assessment</div>{rows}</div>', unsafe_allow_html=True)

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
                    <span class="abnorm-param">{a.get("parameter","")}</span>
                    <span class="abnorm-val">{a.get("value","")}</span>
                  </div>
                  <div class="abnorm-range">Normal range: {a.get("normal_range","")}</div>
                  <div class="abnorm-interp">{a.get("interpretation","")}</div>
                </div>"""
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)

    with tab4:
        preds = result.get("predicted_conditions", [])
        if not preds:
            st.info("No conditions predicted.")
        else:
            rows = ""
            for c in preds:
                bdg = badge_class(c.get("confidence", ""))
                rows += f"""
                <div class="risk-row">
                  <div class="risk-dot dot-moderate" style="background:#6366f1;box-shadow:0 0 8px #6366f155"></div>
                  <div>
                    <div class="risk-name">{c.get("condition","")}
                      <span class="badge badge-confident">{c.get("confidence","").upper()} CONFIDENCE</span>
                    </div>
                    <div class="risk-reason">{c.get("basis","")}</div>
                  </div>
                </div>"""
            st.markdown(f'<div class="card"><div class="card-title">Predicted Conditions</div>{rows}</div>', unsafe_allow_html=True)

    with tab5:
        recs = result.get("recommendations", [])
        if not recs:
            st.info("No recommendations generated.")
        else:
            items = "".join(f'<div class="rec-item"><span class="rec-arrow">→</span> {r}</div>' for r in recs)
            st.markdown(f'<div class="card"><div class="card-title">Clinical Recommendations</div>{items}</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer">
      ⚠️ <strong>Disclaimer:</strong> This AI analysis is strictly for informational and educational purposes.
      It does not constitute medical advice, diagnosis, or treatment.
      Always consult a qualified healthcare professional before making any health-related decisions.
    </div>""", unsafe_allow_html=True)


# ── Sidebar — API key ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Get your key at console.anthropic.com"
    )
    if api_key:
        st.session_state["api_key"] = api_key
        st.success("API key set ✓")
    st.markdown("---")
    st.markdown("""
**How to use:**
1. Enter your Anthropic API key above
2. Paste report text **or** upload an image
3. Click **Analyze**
4. Browse results in the tabs
    """)
    st.markdown("---")
    st.caption("Powered by Claude claude-opus-4-5 · claude.ai")


# ── Hero ─────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">AI · CLINICAL ANALYSIS · GEN AI</div>
  <h1>Medical Report<br>Analyzer</h1>
  <p>Upload a report image or paste text — Claude reads it and delivers structured clinical insights instantly.</p>
</div>
""", unsafe_allow_html=True)


# ── Input section ────────────────────────────────────────────
input_mode = st.radio(
    "Input method",
    ["✏️ Paste text", "🖼️ Upload image"],
    horizontal=True,
    label_visibility="collapsed"
)

if input_mode == "✏️ Paste text":
    report_text = st.text_area(
        "Medical report text",
        height=220,
        placeholder="Paste your lab report, blood work, radiology findings, discharge summary, or any medical report here…",
        label_visibility="collapsed"
    )
    uploaded_file = None
else:
    uploaded_file = st.file_uploader(
        "Upload medical report image",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )
    report_text = ""
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded report", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
analyze_clicked = st.button("🧠 Analyze Report", use_container_width=True)

# ── Analysis logic ───────────────────────────────────────────
if analyze_clicked:
    if not st.session_state.get("api_key"):
        st.error("⚠️ Please enter your Anthropic API key in the sidebar first.")
    elif input_mode == "✏️ Paste text" and not report_text.strip():
        st.error("⚠️ Please paste some report text before analyzing.")
    elif input_mode == "🖼️ Upload image" and uploaded_file is None:
        st.error("⚠️ Please upload an image first.")
    else:
        with st.spinner("🔬 Claude is reading and analyzing the report…"):
            try:
                if input_mode == "✏️ Paste text":
                    result = analyze_text(report_text)
                else:
                    uploaded_file.seek(0)
                    img_bytes = uploaded_file.read()
                    ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
                    media_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
                    media_type = media_map.get(ext, "image/jpeg")
                    result = analyze_image(img_bytes, media_type)

                st.session_state["result"] = result
                st.success("Analysis complete!")
            except json.JSONDecodeError:
                st.error("The AI returned an unexpected format. Try again.")
            except Exception as e:
                st.error(f"Analysis failed: {e}")

# ── Show results ─────────────────────────────────────────────
if "result" in st.session_state:
    st.markdown("---")
    render_results(st.session_state["result"])
