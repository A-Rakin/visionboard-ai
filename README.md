# VisionBoard AI — Search Images Like Google Lens, Organize Like Pinterest

VisionBoard AI is an advanced AI-powered Visual Search Engine and Image Management Platform built with **Flask**, **PyTorch**, **YOLOv8**, **BLIP**, **EasyOCR**, **OpenCV**, and **CLIP Vector Embeddings**.

---

## 🌟 Core Features

- **YOLOv8 Object Detection**: Detect objects (Person, Laptop, Bottle, Keyboard, Chair, etc.) with normalized bounding boxes and interactive HTML5 Canvas highlighting.
- **BLIP AI Image Captioning**: Generate natural language captions for any uploaded image.
- **EasyOCR Text Extraction**: Recognize and extract embedded typography, logos, and printed text.
- **K-Means Dominant Color Palette**: Extract top 5 dominant colors with hex codes, RGB values, and coverage percentages.
- **CLIP 512-d Semantic Vector Search**: Perform natural language text query search (*"Laptop on office desk"*, *"Beach sunset"*) and Google-Lens style visual reverse image search using Cosine Similarity.
- **Image Quality Scoring**: Analyze Laplacian blur/sharpness, brightness, and contrast to yield an AI Quality Score (0-100).
- **Perceptual Hash Duplicate Detection**: Detect near-duplicate photos using difference hashing.
- **PDF Report Download**: Download styled PDF AI reports using `ReportLab`.
- **Pinterest-Style Library & Collections**: Organize images into user folders/collections, save favorites, and filter by popular categories (Cars, Animals, Medical, Food, Fashion, Architecture).
- **Chart.js Analytics Dashboard**: Real-time stats on uploaded images, object detection frequencies, and color distributions.
- **Full REST API & Swagger Docs**: OpenAPI endpoints for `/api/upload`, `/api/search`, `/api/caption`, `/api/ocr`, `/api/object`, `/api/colors`, `/api/reports/<id>`.

---

## 🏗️ Folder Structure

```
VisionBoard-AI/
├── app/
│   ├── ai/
│   │   ├── yolo.py         # YOLOv8 object detection & OpenCV fallback
│   │   ├── blip.py         # BLIP image captioning
│   │   ├── clip.py         # CLIP image & text embeddings + cosine similarity
│   │   ├── ocr.py          # EasyOCR text extraction
│   │   ├── color.py        # K-Means dominant color extractor
│   │   ├── metadata.py     # EXIF & quality score calculation
│   │   └── pipeline.py     # Unified AI processing orchestrator
│   ├── models/
│   │   ├── user.py         # User model (Flask-Login)
│   │   ├── image.py        # Image model & relationships
│   │   ├── object.py       # DetectedObject model
│   │   ├── caption.py      # Caption model
│   │   ├── color.py        # DominantColor model
│   │   ├── text.py         # ExtractedText model
│   │   ├── tag.py          # Tag & image_tags model
│   │   ├── collection.py   # Collection & collection_images model
│   │   ├── embedding.py    # ImageEmbedding vector file reference
│   │   └── search_history.py
│   ├── services/
│   │   └── pdf_report.py   # ReportLab PDF generator
│   ├── auth/               # Authentication routes (login, register)
│   ├── dashboard/          # Feed, detail, collections, search, analytics
│   ├── upload/             # Drag & drop upload handler
│   ├── api/                # REST API endpoints
│   ├── static/
│   │   ├── css/style.css   # Glassmorphism design system
│   │   └── js/             # main.js, boundingbox.js, analytics.js
│   ├── templates/          # HTML templates
│   ├── uploads/            # Uploaded images
│   ├── embeddings/         # Saved .npy vector files
│   └── reports/            # Generated PDF reports
├── config.py
├── run.py
├── requirements.txt
└── README.md
```

---

## ⚡ Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Application
```bash
python run.py
```

Open your browser at `http://127.0.0.1:5000`.

Default demo credentials created automatically:
- **Username**: `demo`
- **Password**: `demo1234`

---

## 📄 REST API Endpoints

- `POST /api/upload`: Upload image file for AI processing.
- `GET /api/search?q=<query>`: Natural language semantic vector search.
- `GET /api/caption/<id>`: Get BLIP caption.
- `GET /api/ocr/<id>`: Get EasyOCR text.
- `GET /api/object/<id>`: Get YOLO bounding box coordinates.
- `GET /api/colors/<id>`: Get dominant color palette.
- `GET /api/reports/<id>`: Download PDF AI Report.
- Interactive API Docs available at `http://127.0.0.1:5000/apidocs`.
