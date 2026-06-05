# SISTEM DETEKSI GAMBAR AI BERBASIS FUZZY LOGIC SUGENO
## Dokumentasi Lengkap v2.0

---

## 📋 DAFTAR ISI

1. [Ringkasan Perbaikan](#ringkasan-perbaikan)
2. [Arsitektur Sistem](#arsitektur-sistem)
3. [Komponen Utama](#komponen-utama)
4. [Instalasi & Setup](#instalasi--setup)
5. [Penggunaan](#penggunaan)
6. [Pipeline Fuzzy Inference](#pipeline-fuzzy-inference)
7. [Evaluasi Sistem](#evaluasi-sistem)
8. [Struktur Dataset](#struktur-dataset)
9. [Database & Penyimpanan](#database--penyimpanan)
10. [API Endpoints](#api-endpoints)

---

## ✨ RINGKASAN PERBAIKAN

Sistem telah diperbaiki dan dioptimalkan dengan fokus pada:

### ✅ Perbaikan Utama:

1. **Sinkronisasi Dataset** ✓
   - Folder dataset terpisah: `dataset/ai/` dan `dataset/human/`
   - Labeling system dengan CSV (`dataset_labels.csv`)
   - Auto-loading dari kedua folder secara bersamaan
   - Train-test split dengan reproducibility

2. **Implementasi Fuzzy Sugeno Lengkap** ✓
   - 55 fuzzy rules yang komprehensif
   - Membership functions yang optimal dengan overlap minimal
   - Fuzzifikasi, inference, dan defuzzifikasi yang proper
   - Output Sugeno dengan weighted average

3. **Feature Extraction & Normalisasi** ✓
   - 10 fitur utama: entropy, contrast, edge_density, FFT, blur, noise, histogram, brightness, saturation, color_variance
   - Normalisasi dengan z-score normalization
   - Feature fitting pada dataset training

4. **Threshold Klasifikasi Optimal** ✓
   - AI Generated: score ≥ 0.65
   - Uncertain: 0.45 - 0.64
   - Human Made: score < 0.45
   - Aplikasi konsisten di seluruh sistem

5. **Evaluation Engine Lengkap** ✓
   - Confusion Matrix: TP, TN, FP, FN
   - Metrics: Accuracy, Precision, Recall, F1 Score, Specificity
   - ROC Curve dengan AUC calculation
   - Dataset statistics dan distribution analysis

6. **Heatmap Visualization Sophisticated** ✓
   - Laplacian activation map
   - Edge anomaly detection
   - Texture response map
   - Frequency domain analysis
   - Composite artifact map (weighted combination)
   - Grad-CAM style visualization
   - Overlay visualization dengan original image

7. **Database & Penyimpanan** ✓
   - SQLite database untuk hasil deteksi
   - Penyimpanan fitur, score, dan metadata
   - Export ke CSV
   - Detection history dalam JSON

8. **Batch Processing** ✓
   - Deteksi batch gambar dari dataset
   - Real-time progress tracking
   - Evaluation otomatis pada batch

---

## 🏗️ ARSITEKTUR SISTEM

```
┌─────────────────────────────────────────────────────────────┐
│                     WEB INTERFACE (HTML/JS)                  │
└─────────────────────────────────────────┬───────────────────┘
                                          │
┌─────────────────────────────────────────▼───────────────────┐
│                    FLASK BACKEND (app_new.py)                │
├─────────────────────────────────────────────────────────────┤
│  Upload Handling │ Batch Processing │ API Endpoints        │
└────────┬──────────────────────┬──────────────────┬──────────┘
         │                      │                  │
    ┌────▼─────┐    ┌──────────▼────┐   ┌────────▼─────┐
    │ Dataset   │    │ Feature        │   │ Evaluation   │
    │ Handler   │    │ Extraction     │   │ Engine       │
    │           │    │ & Normalization│   │              │
    └────┬─────┘    └──────────┬─────┘   └────────┬─────┘
         │                     │                  │
    ┌────▼─────────────────────▼──────────────────▼─────┐
    │          FUZZY SUGENO INFERENCE ENGINE            │
    ├─────────────────────────────────────────────────────┤
    │ Fuzzification → Rules Firing → Defuzzification    │
    │ (55 Rules) (Membership Functions) (Weighted Avg)   │
    └────────┬─────────────────────────────────────────┘
             │
    ┌────────▼──────────┐    ┌────────────────┐
    │  Classification   │    │  Heatmap       │
    │  + Confidence     │    │  Generation    │
    └────────┬──────────┘    └────────┬───────┘
             │                       │
    ┌────────▼───────────────────────▼──────┐
    │     RESULTS DATABASE & STORAGE         │
    ├────────────────────────────────────────┤
    │ SQLite DB │ CSV Export │ JSON History │
    └────────────────────────────────────────┘
```

---

## 🔧 KOMPONEN UTAMA

### 1. **fuzzy_engine.py** - Fuzzy Sugeno Inference Engine
   - `MembershipFunction`: Triangular dan trapezoidal membership
   - `FuzzyVariables`: Definisi rentang fuzzy untuk 9 input variables
   - `SugenoRules`: 55 fuzzy rules yang spesifik dan realistis
   - `SugenoInferenceEngine`: Pipeline lengkap fuzzifikasi → inference → defuzzifikasi
   - Output: AI score (0-1) dan confidence level

### 2. **dataset_handler.py** - Dataset Management
   - `DatasetLoader`: Load gambar dari folder ai/ dan human/
   - `FeatureExtractor`: Ekstraksi 10 fitur dari gambar
   - `FeatureNormalizer`: Normalisasi features dengan z-score
   - `ResultsDatabase`: SQLite database untuk penyimpanan hasil

### 3. **evaluation_engine.py** - Evaluation & Metrics
   - `ConfusionMatrix`: TP, TN, FP, FN calculation
   - `PerformanceEvaluator`: Accuracy, Precision, Recall, F1, dll
   - `ROCAnalysis`: ROC curve dan AUC calculation
   - `DatasetStatistics`: Statistik dan distribusi AI scores
   - `EvaluationEngine`: Unified evaluation interface

### 4. **heatmap_generator.py** - Visualization
   - `HeatmapGenerator`: Multiple heatmap generation methods
   - `GradCAMDetector`: Gradient-based activation mapping
   - `HeatmapSaver`: Save heatmap dengan berbagai format
   - Support untuk: Laplacian, Edge, Texture, Frequency, Composite, GradCAM

### 5. **app_new.py** - Flask Backend
   - RESTful API endpoints untuk deteksi gambar
   - Batch processing pipeline
   - Dataset loading dan evaluation
   - Integration dengan semua modul

### 6. **test_system.py** - Comprehensive Testing
   - Full dataset evaluation
   - Report generation
   - CSV export
   - Database export

---

## 💻 INSTALASI & SETUP

### Prasyarat:
- Python 3.8+
- pip package manager

### 1. Clone Repository & Masuk ke Folder:
```bash
cd "path/to/deteksi ai lama"
```

### 2. Buat Virtual Environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies:
```bash
pip install -r requirements.txt
```

### 4. Setup Dataset:
```
dataset/
├── ai/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── human/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
└── dataset_labels.csv
```

### 5. Jalankan Server:
```bash
python app_new.py
```

Server akan berjalan di `http://127.0.0.1:5000`

---

## 📖 PENGGUNAAN

### A. Deteksi Gambar Tunggal via Web Interface:
1. Buka http://127.0.0.1:5000
2. Upload gambar melalui drag-drop area
3. Tunggu hasil deteksi
4. Lihat: AI Score, Confidence, Classification, Heatmap

### B. Batch Detection API:
```python
import requests

files = [('images', open('image1.jpg', 'rb')), ('images', open('image2.jpg', 'rb'))]
labels = ['AI', 'HUMAN']
data = {'labels': labels}

response = requests.post('http://127.0.0.1:5000/api/batch-detection', files=files, data=data)
print(response.json())
```

### C. Full Dataset Evaluation:
```bash
python test_system.py
```

Output:
- `evaluation_results.csv` - Hasil deteksi per gambar
- `evaluation_report.json` - Laporan evaluasi lengkap
- `database_export.csv` - Export dari database
- Console report dengan metrics lengkap

### D. API Endpoints:

**Single Image Upload:**
```
POST /api/upload
Form: image (file)
Response: {ai_score, confidence, classification, features, heatmap_url, ...}
```

**Batch Detection:**
```
POST /api/batch-detection
Form: images (multiple files), labels (optional)
Response: {total, results[], evaluation}
```

**Dataset Detection:**
```
POST /api/dataset-detection
Response: {total_processed, results[], evaluation}
```

**Get Detection History:**
```
GET /api/detection-history
Response: {history[], total}
```

**Get Evaluation:**
```
GET /api/evaluation
Response: {confusion_matrix, metrics, roc, dataset_statistics, ...}
```

**System Information:**
```
GET /api/system-info
Response: {fuzzy_engine, feature_extractor, database, ...}
```

---

## 🔍 PIPELINE FUZZY INFERENCE

### Step-by-Step Process:

```
1. IMAGE INPUT
   └─ Load & Resize (max 1024x1024)

2. FEATURE EXTRACTION (10 features)
   ├─ Entropy
   ├─ Contrast (texture)
   ├─ Edge Density
   ├─ FFT High-Frequency Ratio
   ├─ Blur Score
   ├─ Noise Score
   ├─ Histogram Std
   ├─ Brightness
   ├─ Saturation
   └─ Color Variance

3. NORMALIZATION (z-score)
   └─ Transform to [0, 1] range

4. FUZZIFICATION
   ├─ Map each feature to fuzzy sets: LOW, MEDIUM, HIGH
   ├─ Compute membership degrees
   └─ Get fuzzy conditions

5. RULE INFERENCE (55 rules)
   ├─ Match fuzzy conditions dengan rules
   ├─ Calculate firing strength
   └─ Collect fired rules

6. WEIGHTED AGGREGATION
   ├─ Sum (rule_weight × firing_strength)
   └─ Normalize dengan total firing strength

7. DEFUZZIFICATION (Sugeno)
   ├─ AI Score = Weighted Average
   ├─ Confidence = Max Firing Strength (boosted)
   └─ Output: [0, 1]

8. CLASSIFICATION
   ├─ AI Generated:  AI Score ≥ 0.65
   ├─ Uncertain:     0.45 ≤ AI Score < 0.65
   └─ Human Made:    AI Score < 0.45

9. HEATMAP GENERATION
   ├─ Laplacian activation map
   ├─ Edge anomaly map
   ├─ Texture response map
   ├─ Frequency anomaly map
   └─ Composite (weighted combination)

10. OUTPUT
    ├─ Classification result
    ├─ AI Score & Confidence
    ├─ Feature values
    ├─ Inference details
    ├─ Heatmap visualization
    └─ Overlay image
```

### Fuzzy Rules Summary:

- **Rules 1-10**: AI Detection (entropy HIGH, FFT HIGH, texture LOW, dll)
- **Rules 11-20**: Human Detection (entropy LOW, FFT LOW, texture HIGH, dll)
- **Rules 21-30**: Intermediate cases (MEDIUM values, edge cases)
- **Rules 31-55**: Complex & specific conditions (multi-condition rules)

Setiap rule memiliki:
- **Conditions**: Feature fuzzy set combinations
- **Weight**: Output value (0 = Human, 1 = AI)
- **Confidence**: Trust level (0.6 - 0.9)

---

## 📊 EVALUASI SISTEM

### Metrics yang Diukur:

**Confusion Matrix:**
```
                 Predicted
              AI    HUMAN
Actual AI    [TP]   [FN]
       HUMAN [FP]   [TN]
```

**Performance Metrics:**
- **Accuracy** = (TP + TN) / Total
- **Precision** = TP / (TP + FP)
- **Recall** = TP / (TP + FN)
- **F1 Score** = 2 × (Precision × Recall) / (Precision + Recall)
- **Specificity** = TN / (TN + FP)
- **Sensitivity** = Recall
- **FPR** = FP / (FP + TN)
- **FNR** = FN / (FN + TP)

**ROC Curve:**
- Plot TPR vs FPR untuk berbagai threshold
- Calculate AUC (Area Under Curve)
- Nilai AUC: 0.5 = random, 1.0 = perfect

### Evaluasi Dataset:

Jalankan full evaluation dengan:
```bash
python test_system.py
```

Output Example:
```
[CONFUSION MATRIX]
  True Positives (TP):   45
  True Negatives (TN):   42
  False Positives (FP):  5
  False Negatives (FN):  8

[PERFORMANCE METRICS]
  Accuracy:              0.8700 (87.00%)
  Precision:             0.9000 (90.00%)
  Recall (Sensitivity):  0.8491 (84.91%)
  Specificity:           0.8941 (89.41%)
  F1 Score:              0.8735
  False Positive Rate:   0.1059 (10.59%)
  False Negative Rate:   0.1509 (15.09%)

[ROC ANALYSIS]
  AUC (Area Under Curve): 0.9216
```

---

## 📁 STRUKTUR DATASET

### Folder Structure:
```
dataset/
├── ai/
│   ├── sample_ai_001.jpg
│   ├── sample_ai_002.jpg
│   ├── sample_ai_003.jpg
│   └── ... (minimal 100 gambar AI)
├── human/
│   ├── sample_human_001.jpg
│   ├── sample_human_002.jpg
│   ├── sample_human_003.jpg
│   └── ... (minimal 100 gambar HUMAN)
└── dataset_labels.csv
```

### Dataset Labels CSV Format:
```csv
filename,label,category,split
sample_ai_001.jpg,AI,animal,train
sample_ai_002.jpg,AI,animal,train
sample_ai_003.jpg,AI,human,train
sample_human_001.jpg,HUMAN,animal,train
sample_human_002.jpg,HUMAN,animal,train
...
```

### Dataset Categories (Optional):
- animal
- human
- object
- landscape
- abstract
- texture

### Rekomendasi Dataset:
- **Total**: 200-500 gambar
- **AI**: 100-250 gambar dari berbagai sumber (DALL-E, Midjourney, Stable Diffusion)
- **Human**: 100-250 gambar asli dari berbagai fotograper
- **Format**: JPG, PNG
- **Ukuran**: 256x256 hingga 2048x2048 pixels
- **Kualitas**: High quality, diverse content

---

## 💾 DATABASE & PENYIMPANAN

### SQLite Database (`detection_results.db`):

**Table: detection_results**
```sql
CREATE TABLE detection_results (
    id INTEGER PRIMARY KEY,
    filename TEXT,
    label_asli TEXT,
    hasil_prediksi TEXT,
    ai_score REAL,
    confidence REAL,
    entropy REAL,
    texture REAL,
    fft REAL,
    edge_density REAL,
    blur_score REAL,
    noise_score REAL,
    histogram_std REAL,
    brightness REAL,
    saturation REAL,
    color_variance REAL,
    timestamp DATETIME
)
```

**Table: evaluation_results**
```sql
CREATE TABLE evaluation_results (
    id INTEGER PRIMARY KEY,
    total_samples INTEGER,
    accuracy REAL,
    precision REAL,
    recall REAL,
    f1_score REAL,
    specificity REAL,
    auc REAL,
    timestamp DATETIME
)
```

### File Storage:

**Detection History** (`detection_history.json`):
- JSON format
- Max 500 entries
- Fields: id, timestamp, filename, classification, ai_score, confidence

**Evaluation Report** (`evaluation_report.json`):
- Confusion matrix
- Performance metrics
- ROC data
- Dataset statistics
- Timestamp

**CSV Exports**:
- `evaluation_results.csv` - Hasil per gambar
- `database_export.csv` - Export database lengkap

**Heatmaps** (`static/assets/uploads/`):
- `heatmap_*.png` - Composite heatmap
- `overlay_*.png` - Overlay dengan original image

---

## 🔌 API ENDPOINTS

### 1. Upload & Detection

**POST /api/upload**
```json
Request:
{
  "file": "image.jpg"
}

Response:
{
  "filename": "image.jpg",
  "ai_score": 0.7823,
  "confidence": 0.85,
  "classification": "AI Generated",
  "features": {
    "entropy": 0.6234,
    "contrast": 0.5123,
    ...
  },
  "heatmap_url": "/static/assets/uploads/heatmap_xxx.png",
  "overlay_url": "/static/assets/uploads/overlay_xxx.png"
}
```

### 2. Batch Detection

**POST /api/batch-detection**
```json
Request:
{
  "images": [file1, file2, ...],
  "labels": ["AI", "HUMAN", ...] (optional)
}

Response:
{
  "total": 5,
  "results": [
    {...image1 result...},
    {...image2 result...}
  ],
  "evaluation": {
    "confusion_matrix": {...},
    "metrics": {...},
    "roc": {...}
  }
}
```

### 3. Dataset Detection

**POST /api/dataset-detection**
```json
Request: (none - uses dataset folder)

Response:
{
  "total_processed": 200,
  "results": [
    {...results for each image...}
  ],
  "evaluation": {
    "full_evaluation_data"
  }
}
```

### 4. Detection History

**GET /api/detection-history**
```json
Response:
{
  "history": [
    {
      "id": "uuid",
      "timestamp": "2024-05-26T...",
      "filename": "image.jpg",
      "classification": "AI Generated",
      "ai_score": 0.78,
      "confidence": 0.85
    }
  ],
  "total": 150
}
```

### 5. Clear History

**POST /api/detection-history/clear**
```json
Response:
{
  "success": true
}
```

### 6. Get Evaluation

**GET /api/evaluation**
```json
Response:
{
  "confusion_matrix": {
    "tp": 45,
    "tn": 42,
    "fp": 5,
    "fn": 8
  },
  "metrics": {
    "accuracy": 0.87,
    "precision": 0.90,
    "recall": 0.85,
    "f1_score": 0.87,
    ...
  },
  "roc": {
    "fpr": [...],
    "tpr": [...],
    "auc": 0.92
  },
  "dataset_statistics": {...}
}
```

### 7. Reset Evaluation

**POST /api/evaluation/reset**
```json
Response:
{
  "success": true
}
```

### 8. Get Statistics

**GET /api/statistics**
```json
Response:
{
  "total_detections": 250,
  "predictions": {
    "AI Generated": 120,
    "Human Made": 100,
    "Uncertain": 30
  },
  "avg_ai_score": 0.52,
  "avg_confidence": 0.78
}
```

### 9. Export Results

**GET /api/results-export**
```json
Response:
{
  "success": true,
  "file": "detection_results_export.csv"
}
```

### 10. System Info

**GET /api/system-info**
```json
Response:
{
  "fuzzy_engine": {
    "engine_type": "Sugeno",
    "total_rules": 55,
    "thresholds": {
      "ai": 0.65,
      "uncertain_high": 0.64,
      "uncertain_low": 0.45,
      "human": 0.45
    }
  },
  "feature_extractor": {
    "features": ["entropy", "contrast", ...],
    "total_features": 10
  },
  "database": {
    "path": "detection_results.db",
    "status": "active"
  }
}
```

---

## 🎯 CHECKLIST PERBAIKAN

- [x] Sinkronisasi dataset (folder ai/ & human/)
- [x] Labeling system dengan CSV
- [x] Fuzzy Sugeno implementation (55 rules)
- [x] Membership functions optimal
- [x] Feature extraction lengkap (10 features)
- [x] Feature normalization
- [x] Threshold klasifikasi (0.65, 0.45)
- [x] Confusion matrix real
- [x] Accuracy, Precision, Recall, F1
- [x] ROC curve dengan AUC
- [x] Advanced heatmap visualization
- [x] Batch processing
- [x] Database storage
- [x] CSV export
- [x] Detection history
- [x] Evaluation engine
- [x] API endpoints
- [x] System testing
- [x] Comprehensive documentation

---

## 📞 SUPPORT & TROUBLESHOOTING

### Common Issues:

**1. "No module named 'fuzzy_engine'"**
- Solution: Pastikan semua file Python ada di folder root
- Check: fuzzy_engine.py, dataset_handler.py, evaluation_engine.py, heatmap_generator.py

**2. "No images found in dataset"**
- Solution: Pastikan folder `dataset/ai/` dan `dataset/human/` ada
- Add: Minimal 1 gambar di masing-masing folder

**3. "Feature normalizer not fitted"**
- Solution: Jalankan test_system.py terlebih dahulu untuk fit normalizer
- Or: Manual fit dengan dataset images

**4. Port 5000 already in use**
- Solution: Edit app_new.py baris akhir
- Change: `port=5001` atau gunakan port lain

**5. Out of memory pada dataset besar**
- Solution: Process batch lebih kecil
- Or: Resize image lebih kecil (512x512)

---

## 📝 VERSION HISTORY

- **v1.0** - Initial system (basic fuzzy scoring)
- **v2.0** - Complete optimization
  - ✨ Full Fuzzy Sugeno implementation
  - ✨ Dataset synchronization
  - ✨ Advanced evaluation engine
  - ✨ Sophisticated heatmap visualization
  - ✨ Database storage
  - ✨ Comprehensive testing & documentation

---

## 📄 LICENSE & CREDIT

Dikembangkan untuk penelitian skripsi:
**"Penerapan Fuzzy Logic Sugeno dalam Mendeteksi Gambar AI"**

---

**Status**: ✅ Production Ready  
**Last Updated**: May 26, 2024  
**Maintained by**: Development Team
