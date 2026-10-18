# 🌱 AgriVision — AI-Powered Crop & Weed Detection

AgriVision is a machine learning project that uses computer vision to detect crops and weeds in agricultural images. It uses a fine-tuned YOLO object detection model and a Streamlit dashboard to make image analysis easy to use.

## 🚀 Live Demo

**Try the application:** [AgriVision Live App](https://agrivision-crop-weed-detection-eycrbf3di56s6sqrc3cuxg.streamlit.app/)

## ✨ Features

- **AI-Based Detection:** Detects crops and weeds in uploaded images.
- **Bounding Boxes:** Displays detected objects with confidence scores.
- **Interactive Dashboard:** Provides a simple interface for image analysis.
- **Crop Protection Guidance:** Shows general crop-care and weed-management recommendations.
- **Dark and Light Themes:** Supports different visual preferences.
- **Web-Based Application:** Accessible through a browser using Streamlit Community Cloud.

## 🧠 Technology Stack

- **Python** — Core programming language
- **YOLO11n (Ultralytics)** — Object detection model
- **PyTorch** — Deep learning framework used by the model
- **Streamlit** — Interactive web application
- **Pillow** — Image handling
- **NumPy** — Numerical operations
- **OpenCV** — Computer vision dependency

## 📊 Model Performance

The trained model was evaluated on a validation dataset of 260 images containing 380 labeled instances.

| Metric | Result |
|---|---:|
| Precision | 81.9% |
| Recall | 78.7% |
| mAP@50 | 85.1% |
| mAP@50–95 | 59.3% |

These results reflect performance on the validation dataset. Actual results may vary with image quality, lighting, camera angle, and field conditions.

## 🌾 Supported Detection Classes

The model is trained to detect two classes:

- `crop`
- `weed`

The crop selection in the Crop Protection section provides general guidance; the model does not identify individual crop species or diagnose plant diseases.

## 🛠️ Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Khushi-Singh7/agrivision-crop-weed-detection.git
cd agrivision-crop-weed-detection
```

### 2. Create and activate a virtual environment

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Start the application

```bash
python -m streamlit run app.py
```

Open the local URL displayed in your terminal.

## 📁 Project Structure

```text
agrivision-crop-weed-detection/
├── backend/
│   ├── __init__.py
│   ├── predict.py
│   └── recommendations.py
├── models/
│   └── best.pt
├── app.py
├── packages.txt
├── requirements.txt
├── README.md
└── .gitignore
```

## ⚠️ Limitations

- Predictions depend on the quality and suitability of the input image.
- The model detects generic crop and weed classes, not specific diseases or crop varieties.
- Crop-protection information is general educational guidance, not a confirmed diagnosis or pesticide prescription.
- Always consult local agricultural experts before applying crop treatments or pesticides.

## 👩‍💻 Project Purpose

This project demonstrates the application of computer vision and deep learning to an agricultural problem. It combines an object detection model with a user-friendly web interface to explore how AI can support crop monitoring and weed management.

## 📄 License

No license has been specified yet. Please add a license if you intend to distribute or reuse this project under particular terms.
