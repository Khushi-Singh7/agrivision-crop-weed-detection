import hashlib
import io
import json
from collections import Counter
from pathlib import Path

import streamlit as st
from PIL import Image

from backend.predict import CropWeedDetector
from backend.recommendations import get_recommendations

# ---------- Page configuration ----------
st.set_page_config(
    page_title="AgriVision | Crop & Weed AI",
    page_icon="🌱",
    layout="wide",
)

MODEL_PATH = Path(__file__).parent / "models" / "best.pt"
CROPS = ["Wheat", "Rice", "Sugarcane", "Maize", "Cotton", "Vegetables"]
PAGES = ["Overview", "Detect & Analyze", "Crop Protection", "About Project"]

# ---------- Theme (light / dark) ----------
# The toggle is drawn next to the navigation tabs further down. Its value is read
# from session_state here, so the colours are known before the page is drawn.
dark_mode = st.session_state.get("dark_mode", False)

DARK = {
    "background": "#101A15", "sidebar": "#17251D", "card": "#1E3025",
    "text": "#F1F7F2", "muted": "#B8CABC", "border": "#355241",
    "input": "#24382B", "accent": "#42C779", "hero1": "#123B2A", "hero2": "#187747",
}
LIGHT = {
    "background": "#F5F9F5", "sidebar": "#EAF3EB", "card": "#FFFFFF",
    "text": "#193526", "muted": "#52675A", "border": "#D5E4D8",
    "input": "#FFFFFF", "accent": "#16834A", "hero1": "#123B2A", "hero2": "#16834A",
}
theme = DARK if dark_mode else LIGHT

# Dark tables: Streamlit draws dataframes on a canvas that CSS cannot recolour,
# so in dark mode the table is inverted to match the page.
table_fix = (
    '[data-testid="stDataFrame"] { filter: invert(0.9) hue-rotate(180deg); }'
    if dark_mode else ""
)

STYLE = f"""<style>
:root {{ color-scheme: {"dark" if dark_mode else "light"}; }}
.stApp {{ background-color: {theme["background"]}; color: {theme["text"]}; }}
[data-testid="stHeader"] {{ background-color: {theme["background"]}; }}
[data-testid="stSidebar"] {{ background-color: {theme["sidebar"]}; border-right: 1px solid {theme["border"]}; }}
[data-testid="stSidebar"] * {{ color: {theme["text"]} !important; }}
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li, [data-testid="stCaptionContainer"],
[data-testid="stWidgetLabel"] p, [data-testid="stMetricLabel"],
[data-testid="stMetricValue"], [data-testid="stMetricDelta"] {{ color: {theme["text"]} !important; }}
h1, h2, h3, h4, label {{ color: {theme["text"]} !important; }}
.block-container {{ padding-top: 4.5rem; padding-bottom: 3rem; max-width: 1200px; }}
.agri-hero {{ background: linear-gradient(120deg, {theme["hero1"]}, {theme["hero2"]}); padding: 30px 32px 28px 32px; border-radius: 16px; margin-bottom: 16px; }}
.agri-hero h1 {{ color: #FFFFFF !important; margin: 0 0 4px 0; padding: 0; }}
.agri-hero p {{ color: #E3F3E8 !important; margin: 0; font-size: 1.05rem; }}
.agri-card {{ background: {theme["card"]}; border: 1px solid {theme["border"]}; border-radius: 14px; padding: 16px 18px; height: 100%; }}
.agri-card h4 {{ margin: 0 0 6px 0; padding: 0; }}
.agri-card p {{ margin: 0; color: {theme["muted"]} !important; }}
[data-testid="stMetric"] {{ background-color: {theme["card"]}; border: 1px solid {theme["border"]}; padding: 16px; border-radius: 14px; }}
[data-testid="stTabs"] button {{ color: {theme["text"]} !important; }}
.stButton > button, .stDownloadButton > button, [data-testid="stFileUploader"] button {{
    border-radius: 9px; font-weight: 600; border: 1px solid {theme["border"]};
    background-color: {theme["card"]}; color: {theme["text"]} !important; }}
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {{
    background-color: {theme["accent"]}; color: #FFFFFF !important; border: none; }}
input, textarea {{ color: {theme["text"]} !important; }}
[data-baseweb="select"] > div {{ background-color: {theme["input"]}; color: {theme["text"]}; border-color: {theme["border"]}; }}
[data-testid="stDataFrame"] {{ border: 1px solid {theme["border"]}; border-radius: 10px; }}
{table_fix}
[data-testid="stFileUploader"] section {{ background-color: {theme["card"]}; border: 1px dashed {theme["border"]}; border-radius: 12px; }}
[data-testid="stFileUploader"] * {{ color: {theme["text"]} !important; }}
[data-testid="stAlert"] p {{ color: inherit !important; }}
[data-testid="stToggle"] label > div:first-child {{ background-color: {theme["border"]}; }}
[data-testid="stToggle"] label:has(input:checked) > div:first-child {{ background-color: {theme["accent"]}; }}
hr {{ border-color: {theme["border"]}; }}
</style>"""

# ---------- Helpers ----------
@st.cache_resource
def load_detector(model_path):
    return CropWeedDetector(model_path)


def count_classes(detections):
    return Counter(item["class"].lower() for item in detections)


def stat(column, label, value):
    column.metric(label, value)


def card(column, title, text):
    column.markdown(
        f'<div class="agri-card"><h4>{title}</h4><p>{text}</p></div>',
        unsafe_allow_html=True,
    )


def go_to_detect():
    st.session_state.navigation = "Detect & Analyze"


# ---------- Session state ----------
if "analysis" not in st.session_state:
    st.session_state.analysis = None

# ---------- Sidebar: analysis settings ----------
with st.sidebar:
    st.markdown("## 🌱 AgriVision")
    st.caption("AI-powered agricultural assistance")
    st.divider()
    st.markdown("### Analysis settings")

    selected_crop = st.selectbox("Crop being grown", CROPS, key="selected_crop")
    confidence = st.slider(
        "Confidence threshold", 0.10, 0.90, 0.25, 0.05, key="confidence"
    )
    iou = st.slider("NMS IoU threshold", 0.10, 0.90, 0.50, 0.05, key="iou")
    image_size = st.select_slider(
        "Inference image size", options=[320, 416, 512, 640, 800], value=640, key="image_size"
    )
    st.caption("Model classes: crop and weed")

# ---------- Header, navigation and theme toggle ----------
HERO = """<div class="agri-hero">
<h1>🌿 AgriVision</h1>
<p>Crop &amp; weed detection · smart agricultural analysis</p>
</div>"""
st.markdown(STYLE + HERO, unsafe_allow_html=True)

nav_col, toggle_col = st.columns([5, 1])
with nav_col:
    page = st.radio(
        "Navigation", PAGES, horizontal=True, key="navigation", label_visibility="collapsed"
    )
with toggle_col:
    st.toggle("🌙 Dark mode", key="dark_mode", help="Switch between light and dark themes")

analysis = st.session_state.analysis


# ---------- Overview ----------
if page == "Overview":
    st.subheader("Check your field in three steps")

    counts = count_classes(analysis["detections"]) if analysis else Counter()
    c1, c2, c3 = st.columns(3)
    stat(c1, "Objects in latest analysis", len(analysis["detections"]) if analysis else 0)
    stat(c2, "Crops detected", counts.get("crop", 0))
    stat(c3, "Weeds detected", counts.get("weed", 0))

    a, b, c = st.columns(3)
    card(a, "1. Upload", "Add a photo of your field in the Detect &amp; Analyze tab.")
    card(b, "2. Detect", "The model boxes every crop plant and weed it finds.")
    card(c, "3. Act", "Get prevention advice for your crop and download the report.")

    st.write("")
    st.button("Start detecting", type="primary", on_click=go_to_detect)

    st.caption(
        "Counts describe the latest analysis in this browser session. "
        "They are not a measurement of every plant in the field."
    )


# ---------- Detection ----------
elif page == "Detect & Analyze":
    st.subheader("Image detection")

    uploaded_file = st.file_uploader(
        "Upload a field image (JPG, PNG or WebP)",
        type=["jpg", "jpeg", "png", "webp"],
        key="field_image",
    )

    if not uploaded_file:
        st.info("Upload a field photo to begin. Adjust thresholds in the sidebar if needed.")
    else:
        image_bytes = uploaded_file.getvalue()
        image_hash = hashlib.sha256(image_bytes).hexdigest()
        original_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        st.caption(
            f"{uploaded_file.name} · {original_image.width} × {original_image.height} pixels"
        )

        if st.button("Run crop and weed detection", type="primary"):
            try:
                with st.spinner("Analyzing image with YOLO..."):
                    detector = load_detector(str(MODEL_PATH))
                    annotated_image, detections = detector.predict(
                        original_image,
                        confidence=confidence,
                        iou=iou,
                        image_size=image_size,
                    )
                st.session_state.analysis = {
                    "image_hash": image_hash,
                    "filename": uploaded_file.name,
                    "crop": selected_crop,
                    "detections": detections,
                    "annotated_image": annotated_image,
                    "confidence": confidence,
                    "iou": iou,
                    "image_size": image_size,
                }
            except Exception as error:
                st.error(f"Detection failed: {error}")

        analysis = st.session_state.analysis

        if analysis and analysis["image_hash"] == image_hash:
            detections = analysis["detections"]
            annotated_image = analysis["annotated_image"]
            counts = count_classes(detections)
            crop_count, weed_count = counts.get("crop", 0), counts.get("weed", 0)
            total = len(detections)

            left, right = st.columns(2)
            left.image(original_image, caption="Original image")
            right.image(annotated_image, caption="Annotated predictions")

            m1, m2, m3, m4 = st.columns(4)
            stat(m1, "Total detections", total)
            stat(m2, "Crops", crop_count)
            stat(m3, "Weeds", weed_count)
            stat(m4, "Weed share of detections", f"{weed_count / total:.0%}" if total else "–")

            tab_list, tab_advice, tab_export = st.tabs(
                ["Detections", "Crop protection", "Export"]
            )

            guidance = get_recommendations(analysis["crop"], weed_count)

            with tab_list:
                if detections:
                    st.dataframe(
                        [
                            {
                                "Class": item["class"],
                                "Confidence (%)": round(item["confidence"] * 100, 2),
                                "Bounding box": str(item["box"]),
                            }
                            for item in detections
                        ],
                        hide_index=True,
                    )
                else:
                    st.warning(
                        "No objects passed the confidence threshold. "
                        "Try a lower threshold or a clearer image."
                    )

            with tab_advice:
                st.write(guidance["status"])
                st.markdown("**Prevention**")
                for item in guidance["prevention"]:
                    st.markdown(f"- {item}")
                st.markdown("**Possible management steps**")
                for item in guidance["management"]:
                    st.markdown(f"- {item}")
                st.caption(guidance["safety"])

            with tab_export:
                image_buffer = io.BytesIO()
                annotated_image.save(image_buffer, format="PNG")
                st.download_button(
                    "Download annotated image",
                    data=image_buffer.getvalue(),
                    file_name="crop_weed_detection.png",
                    mime="image/png",
                )
                report = {
                    "filename": analysis["filename"],
                    "selected_crop": analysis["crop"],
                    "confidence_threshold": analysis["confidence"],
                    "iou_threshold": analysis["iou"],
                    "image_size": analysis["image_size"],
                    "detection_counts": {"crop": crop_count, "weed": weed_count},
                    "detections": detections,
                    "recommendations": guidance,
                }
                st.download_button(
                    "Download analysis report (JSON)",
                    data=json.dumps(report, indent=2),
                    file_name="crop_weed_report.json",
                    mime="application/json",
                )


# ---------- Crop protection ----------
elif page == "Crop Protection":
    st.subheader("Crop protection assistant")
    st.write(f"General guidance for **{selected_crop}** (change the crop in the sidebar).")

    weeds_found = 0
    if analysis and analysis["crop"] == selected_crop:
        weeds_found = count_classes(analysis["detections"]).get("weed", 0)

    guidance = get_recommendations(selected_crop, weeds_found)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Preventive practices")
        for item in guidance["prevention"]:
            st.markdown(f"- {item}")
    with col2:
        st.markdown("#### Weed-management options")
        for item in guidance["management"]:
            st.markdown(f"- {item}")

    st.warning(guidance["safety"])
    st.caption(
        "For location-specific advice, consult your local agricultural extension "
        "service or a qualified agronomist. Do not choose a chemical treatment "
        "based only on this model's generic weed label."
    )


# ---------- About ----------
elif page == "About Project":
    st.subheader("About this project")
    st.write(
        "AgriVision is an object-detection application built around a "
        "fine-tuned YOLO model for crop and weed detection."
    )

    if True:
        st.markdown("#### Technology stack")
        st.markdown(
            "- **Python:** application and inference logic\n"
            "- **Streamlit:** interactive frontend\n"
            "- **Ultralytics YOLO:** object detection\n"
            "- **Pillow:** image processing"
        )

    st.markdown("#### Model evaluation")
    m1, m2, m3, m4 = st.columns(4)
    stat(m1, "Precision", "81.9%")
    stat(m2, "Recall", "78.7%")
    stat(m3, "mAP@50", "85.1%")
    stat(m4, "mAP@50–95", "59.3%")
    st.caption(
        "Previously measured validation results on 260 images. "
        "They are not recalculated by this interface."
    )

    st.markdown("#### Limitations")
    st.write(
        "The model has two classes: crop and weed. It does not identify weed "
        "species, diagnose diseases, or determine the correct pesticide. "
        "Predictions should be verified in the field."
    )
