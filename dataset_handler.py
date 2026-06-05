"""
Dataset Handler dan Feature Extraction untuk AI Detection System
Membaca dataset, ekstraksi fitur, normalisasi, dan penyimpanan
"""

import os
import csv
import json
import numpy as np
import cv2
try:
    # skimage may expose graycomatrix in different names across versions
    from skimage.feature import graycomatrix as greycomatrix, graycoprops as greycoprops
except Exception:
    try:
        from skimage.feature.texture import graycomatrix as greycomatrix, graycoprops as greycoprops
    except Exception:
        # fall back to importing by the available names if present
        from skimage.feature import graycomatrix as greycomatrix, graycoprops as greycoprops

from PIL import Image
from pathlib import Path
from typing import Dict, List, Tuple
import sqlite3
from datetime import datetime


class DatasetLoader:
    """Loader untuk dataset dari folder ai/ dan human/"""
    
    def __init__(self, dataset_root: str):
        self.dataset_root = dataset_root
        self.ai_dir = os.path.join(dataset_root, "ai")
        self.human_dir = os.path.join(dataset_root, "human")
        self.labels_file = os.path.join(dataset_root, "dataset_labels.csv")
        self.labels_cache = {}
        self._load_labels()
    
    def _load_labels(self):
        """Load dataset labels dari CSV"""
        if os.path.exists(self.labels_file):
            with open(self.labels_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.labels_cache[row['filename']] = row['label']
    
    def get_label(self, filename: str) -> str:
        """Dapatkan label dari filename"""
        return self.labels_cache.get(filename, "UNKNOWN")
    
    def load_all_images(self) -> List[Dict]:
        """
        Load semua gambar dari folder ai/ dan human/
        Return: list of {"path": str, "filename": str, "label": str, "image": PIL.Image}
        """
        images = []
        
        # Load dari AI folder
        if os.path.exists(self.ai_dir):
            for filename in os.listdir(self.ai_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    filepath = os.path.join(self.ai_dir, filename)
                    try:
                        img = Image.open(filepath).convert('RGB')
                        images.append({
                            "path": filepath,
                            "filename": filename,
                            "label": "AI",
                            "image": img,
                            "folder": "ai"
                        })
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
        
        # Load dari Human folder
        if os.path.exists(self.human_dir):
            for filename in os.listdir(self.human_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    filepath = os.path.join(self.human_dir, filename)
                    try:
                        img = Image.open(filepath).convert('RGB')
                        images.append({
                            "path": filepath,
                            "filename": filename,
                            "label": "HUMAN",
                            "image": img,
                            "folder": "human"
                        })
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
        
        return images
    
    def get_split(self, images: List[Dict], train_ratio: float = 0.8) -> Tuple[List[Dict], List[Dict]]:
        """
        Split dataset ke train dan test
        """
        np.random.seed(42)  # For reproducibility
        indices = np.random.permutation(len(images))
        split_idx = int(len(images) * train_ratio)
        
        train_indices = indices[:split_idx]
        test_indices = indices[split_idx:]
        
        train_set = [images[i] for i in train_indices]
        test_set = [images[i] for i in test_indices]
        
        return train_set, test_set
    
    def save_labels(self):
        """Simpan labels ke CSV"""
        with open(self.labels_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['filename', 'label', 'category', 'split'])
            for filename, label in self.labels_cache.items():
                writer.writerow([filename, label, 'unknown', 'train'])


class FeatureExtractor:
    """Ekstraksi fitur dari gambar untuk fuzzy inference"""
    
    def __init__(self):
        self.feature_names = [
            "entropy",
            "contrast",
            "edge_density",
            "fft_hf_ratio",
            "blur_score",
            "noise_score",
            "histogram_std",
            "brightness_score",
            "saturation_score",
            "color_variance",
        ]
    
    def extract_all_features(self, image: Image.Image) -> Dict[str, float]:
        """
        Ekstraksi semua fitur dari gambar
        """
        # Convert ke numpy
        color_np = np.array(image)
        gray_np = np.array(image.convert('L'))
        
        entropy_raw = self._compute_entropy_raw(gray_np)
        contrast_raw = self._compute_contrast_raw(gray_np)
        edge_density_pct = self._compute_edge_density_pct(gray_np)
        fft_ratio = self._compute_fft_features(gray_np)
        blur_variance = self._compute_blur_variance(gray_np)
        noise_variance = self._compute_noise_variance(gray_np)
        histogram_std_raw = self._compute_histogram_std_raw(gray_np)
        brightness_raw = self._compute_brightness_raw(gray_np)
        saturation_raw = self._compute_saturation_raw(color_np)
        color_variance_raw = self._compute_color_variance_raw(color_np)
        glcm_features = self._compute_glcm_features(gray_np)
        watermark_score = self._compute_watermark_score(gray_np)
        
        features = {
            "entropy_raw": entropy_raw,
            "entropy": self._normalize_entropy(entropy_raw),
            "contrast_raw": contrast_raw,
            "contrast": self._normalize_contrast(contrast_raw),
            "edge_density_pct": edge_density_pct,
            "edge_density": self._normalize_edge_density(edge_density_pct),
            "fft_hf_ratio": fft_ratio,
            "fft_high_freq_ratio": fft_ratio,
            "blur_variance": blur_variance,
            "blur_score": self._normalize_blur(blur_variance),
            "noise_variance": noise_variance,
            "noise_score": self._normalize_noise(noise_variance),
            "histogram_std_raw": histogram_std_raw,
            "histogram_std": self._normalize_histogram_std(histogram_std_raw),
            "brightness_raw": brightness_raw,
            "brightness_score": self._normalize_brightness(brightness_raw),
            "saturation_raw": saturation_raw,
            "saturation_score": self._normalize_saturation(saturation_raw),
            "color_variance_raw": color_variance_raw,
            "color_variance": self._normalize_color_variance(color_variance_raw),
            "glcm_contrast_raw": glcm_features['glcm_contrast_raw'],
            "glcm_contrast": glcm_features['glcm_contrast'],
            "glcm_homogeneity_raw": glcm_features['glcm_homogeneity_raw'],
            "glcm_homogeneity": glcm_features['glcm_homogeneity'],
            "glcm_energy_raw": glcm_features['glcm_energy_raw'],
            "glcm_energy": glcm_features['glcm_energy'],
            "glcm_correlation_raw": glcm_features['glcm_correlation_raw'],
            "glcm_correlation": glcm_features['glcm_correlation'],
            "watermark_score": watermark_score
        }
        
        return features

    def extract_image_analysis(self, color_image: np.ndarray, gray_image: np.ndarray) -> Dict[str, Dict]:
        """
        Extract higher-level image analysis data for charts and indicator panels.
        """
        return {
            "varianceIntensity": self._compute_variance_intensity(gray_image),
            "histogramAnalysis": self._compute_histogram_analysis(gray_image),
            "rgbChannels": self._compute_rgb_channels(color_image)
        }
    
    @staticmethod
    def _compute_entropy_raw(image: np.ndarray) -> float:
        """Compute raw grayscale entropy (0..~8)"""
        hist, _ = np.histogram(image.flatten(), bins=256, range=(0, 255))
        total = hist.sum() if hist.sum() > 0 else 1
        probs = hist.astype('float32') / total
        probs = probs[probs > 0]
        entropy = float(-np.sum(probs * np.log2(probs)))
        return entropy

    @staticmethod
    def _normalize_entropy(entropy_raw: float) -> float:
        return float(np.clip(entropy_raw / 8.0, 0, 1))

    @staticmethod
    def _compute_contrast_raw(image: np.ndarray) -> float:
        """Compute raw grayscale contrast (standard deviation)"""
        return float(np.std(image))

    @staticmethod
    def _normalize_contrast(contrast_raw: float) -> float:
        return float(np.clip(contrast_raw / 128.0, 0, 1))

    @staticmethod
    def _compute_edge_density_pct(image: np.ndarray) -> float:
        """Compute edge density in percent"""
        edges = cv2.Canny(image, 100, 200)
        return float(np.count_nonzero(edges) / edges.size * 100)

    @staticmethod
    def _normalize_edge_density(edge_pct: float) -> float:
        return float(np.clip(edge_pct / 100.0, 0, 1))

    @staticmethod
    def _compute_fft_features(image: np.ndarray) -> float:
        """Compute FFT high-frequency ratio"""
        f = np.fft.fft2(image.astype('float32'))
        fshift = np.fft.fftshift(f)
        magnitude = np.abs(fshift)
        h, w = magnitude.shape
        cy, cx = h // 2, w // 2
        half = min(10, cy, cx)

        low_freq = magnitude[max(0, cy - half):min(h, cy + half), max(0, cx - half):min(w, cx + half)]
        high_freq = magnitude.copy()
        high_freq[max(0, cy - half):min(h, cy + half), max(0, cx - half):min(w, cx + half)] = 0

        low_energy = np.sum(low_freq)
        high_energy = np.sum(high_freq)
        hf_ratio = float(np.clip(high_energy / (low_energy + high_energy + 1e-9), 0, 1))

        return hf_ratio

    @staticmethod
    def _compute_blur_variance(image: np.ndarray) -> float:
        """Compute raw Laplacian variance for sharpness/blur"""
        laplacian = cv2.Laplacian(image, cv2.CV_64F)
        return float(np.var(laplacian))

    @staticmethod
    def _normalize_blur(variance: float) -> float:
        return float(np.clip(variance / 500.0, 0, 1))

    @staticmethod
    def _compute_noise_variance(image: np.ndarray) -> float:
        """Compute raw noise variance from Laplacian energy"""
        laplacian = cv2.Laplacian(image, cv2.CV_64F)
        return float(np.var(laplacian))

    @staticmethod
    def _normalize_noise(noise_variance: float) -> float:
        return float(np.clip((noise_variance - 50.0) / 300.0, 0, 1))

    @staticmethod
    def _compute_histogram_std_raw(image: np.ndarray) -> float:
        """Compute raw histogram standard deviation"""
        hist, _ = np.histogram(image.flatten(), bins=256, range=(0, 255))
        return float(np.std(hist))

    @staticmethod
    def _normalize_histogram_std(hist_std_raw: float) -> float:
        return float(np.clip(hist_std_raw / 1000.0, 0, 1))

    @staticmethod
    def _compute_brightness_raw(image: np.ndarray) -> float:
        """Compute raw brightness as mean intensity"""
        return float(np.mean(image))

    @staticmethod
    def _normalize_brightness(brightness_raw: float) -> float:
        return float(np.clip(brightness_raw / 255.0, 0, 1))

    @staticmethod
    def _compute_saturation_raw(color_image: np.ndarray) -> float:
        """Compute raw saturation as average HSV saturation"""
        hsv = cv2.cvtColor(color_image, cv2.COLOR_RGB2HSV)
        return float(np.mean(hsv[:, :, 1]))

    @staticmethod
    def _normalize_saturation(saturation_raw: float) -> float:
        return float(np.clip(saturation_raw / 255.0, 0, 1))

    @staticmethod
    def _compute_color_variance_raw(color_image: np.ndarray) -> float:
        """Compute raw color variance from RGB channels"""
        channel_std = np.std(color_image.astype('float32'), axis=(0, 1))
        return float(np.mean(channel_std))

    @staticmethod
    def _normalize_color_variance(color_variance_raw: float) -> float:
        return float(np.clip(color_variance_raw / 128.0, 0, 1))

    @staticmethod
    def _compute_variance_intensity(gray_image: np.ndarray) -> Dict[str, float]:
        """Compute intensity variance analysis statistics."""
        pixel_values = gray_image.flatten().astype('float32')
        mean = float(np.mean(pixel_values))
        variance = float(np.var(pixel_values))
        std = float(np.std(pixel_values))
        q25 = float(np.percentile(pixel_values, 25))
        q50 = float(np.percentile(pixel_values, 50))
        q75 = float(np.percentile(pixel_values, 75))
        contrast_level = float(np.clip((np.max(pixel_values) - np.min(pixel_values)) / 255.0 * 100.0, 0, 100))
        return {
            "mean": mean,
            "variance": variance,
            "std": std,
            "contrastLevel": contrast_level,
            "q25": q25,
            "q50": q50,
            "q75": q75,
            "range": float(np.max(pixel_values) - np.min(pixel_values))
        }

    @staticmethod
    def _compute_histogram_analysis(gray_image: np.ndarray) -> Dict[str, object]:
        """Compute grayscale histogram analysis values."""
        hist, _ = np.histogram(gray_image.flatten(), bins=256, range=(0, 255))
        total = float(np.sum(hist)) if np.sum(hist) > 0 else 1.0
        left = float(np.sum(hist[0:86])) / total * 100.0
        middle = float(np.sum(hist[86:171])) / total * 100.0
        right = float(np.sum(hist[171:256])) / total * 100.0
        peak_bin = int(np.argmax(hist))
        return {
            "leftDistribution": left,
            "middleDistribution": middle,
            "rightDistribution": right,
            "peakBin": peak_bin,
            "histogram": hist.tolist()
        }

    @staticmethod
    def _compute_rgb_channels(color_image: np.ndarray) -> Dict[str, object]:
        """Compute RGB channel statistics and histograms."""
        red = color_image[:, :, 0].astype('float32')
        green = color_image[:, :, 1].astype('float32')
        blue = color_image[:, :, 2].astype('float32')
        red_hist, _ = np.histogram(red.flatten(), bins=64, range=(0, 255))
        green_hist, _ = np.histogram(green.flatten(), bins=64, range=(0, 255))
        blue_hist, _ = np.histogram(blue.flatten(), bins=64, range=(0, 255))
        return {
            "redMean": float(np.mean(red)),
            "greenMean": float(np.mean(green)),
            "blueMean": float(np.mean(blue)),
            "redStd": float(np.std(red)),
            "greenStd": float(np.std(green)),
            "blueStd": float(np.std(blue)),
            "redHistogram": red_hist.tolist(),
            "greenHistogram": green_hist.tolist(),
            "blueHistogram": blue_hist.tolist()
        }

    @staticmethod
    def _compute_glcm_features(gray_image: np.ndarray) -> Dict[str, float]:
        """
        Compute GLCM-based texture properties.
        Return both raw values and normalized values.
        """
        try:
            img = gray_image.astype('uint8')
            # ensure 0..255 integer levels
            img8 = np.clip(img, 0, 255).astype('uint8')

            distances = [1]
            angles = [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4]
            glcm = greycomatrix(
                img8,
                distances=distances,
                angles=angles,
                levels=256,
                symmetric=True,
                normed=True
            )

            contrast_raw = float(np.mean(greycoprops(glcm, 'contrast')))
            homogeneity_raw = float(np.mean(greycoprops(glcm, 'homogeneity')))
            energy_raw = float(np.mean(greycoprops(glcm, 'energy')))
            correlation_raw = float(np.mean(greycoprops(glcm, 'correlation')))

            contrast_norm = float(np.clip(contrast_raw / (contrast_raw + 1.0), 0, 1))
            homogeneity_norm = float(np.clip(homogeneity_raw, 0, 1))
            energy_norm = float(np.clip(energy_raw, 0, 1))
            correlation_norm = float(np.clip((correlation_raw + 1.0) / 2.0, 0, 1))

            return {
                'glcm_contrast_raw': contrast_raw,
                'glcm_contrast': contrast_norm,
                'glcm_homogeneity_raw': homogeneity_raw,
                'glcm_homogeneity': homogeneity_norm,
                'glcm_energy_raw': energy_raw,
                'glcm_energy': energy_norm,
                'glcm_correlation_raw': correlation_raw,
                'glcm_correlation': correlation_norm
            }
        except Exception as e:
            print(f"Warning: GLCM compute failed: {e}")
            return {
                'glcm_contrast_raw': 0.0,
                'glcm_contrast': 0.0,
                'glcm_homogeneity_raw': 0.0,
                'glcm_homogeneity': 0.0,
                'glcm_energy_raw': 0.0,
                'glcm_energy': 0.0,
                'glcm_correlation_raw': 0.0,
                'glcm_correlation': 0.0
            }

    @staticmethod
    def _compute_watermark_score(gray_image: np.ndarray) -> float:
        """
        Simple heuristic to detect faint repeated watermark-like edges in low-contrast regions.
        Returns 0..1.
        """
        try:
            imgf = gray_image.astype('float32') / 255.0
            mean = cv2.blur(imgf, (15, 15))
            mean_sq = cv2.blur(imgf * imgf, (15, 15))
            local_var = mean_sq - mean * mean

            mask = local_var < 0.002
            edges = cv2.Canny(gray_image.astype('uint8'), 50, 150)
            mask_count = int(np.count_nonzero(mask))
            if mask_count == 0:
                return 0.0
            score = float(np.sum(edges[mask]) / (mask_count * 255.0))
            return float(np.clip(score, 0, 1))
        except Exception as e:
            print(f"Warning: watermark compute failed: {e}")
            return 0.0


class FeatureNormalizer:
    """Normalisasi fitur untuk fuzzy inference"""
    
    def __init__(self):
        self.feature_stats = {}
        self.is_fitted = False
    
    def fit(self, features_list: List[Dict[str, float]]):
        """
        Fit normalizer dengan data features
        """
        if not features_list:
            return
        
        feature_names = list(features_list[0].keys())
        
        for feature_name in feature_names:
            values = [f[feature_name] for f in features_list]
            self.feature_stats[feature_name] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
            }
        
        self.is_fitted = True
    
    def normalize(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Normalisasi features ke range 0..1 menggunakan min-max.
        Jika normalizer tidak difit, nilai 0..1 tetap dipertahankan.
        """
        normalized = {}

        for feature_name, value in features.items():
            if feature_name not in self.feature_stats or not isinstance(value, (int, float)):
                normalized[feature_name] = float(np.clip(value, 0, 1)) if isinstance(value, (int, float)) else value
                continue

            stats = self.feature_stats[feature_name]
            min_val = stats.get("min", 0.0)
            max_val = stats.get("max", 1.0)

            if max_val > min_val:
                norm_value = (value - min_val) / (max_val - min_val)
                normalized[feature_name] = float(np.clip(norm_value, 0, 1))
            else:
                normalized[feature_name] = float(np.clip(value, 0, 1))

        return normalized


class ResultsDatabase:
    """SQLite database untuk menyimpan hasil deteksi"""
    
    def __init__(self, db_path: str = "detection_results.db"):
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        """Buat tabel di database"""
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            c = conn.cursor()
            
            # Tabel untuk hasil deteksi
            c.execute('''
                CREATE TABLE IF NOT EXISTS detection_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    label_asli TEXT NOT NULL,
                    hasil_prediksi TEXT NOT NULL,
                    ai_score REAL NOT NULL,
                    confidence REAL NOT NULL,
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
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(filename, timestamp)
                )
            ''')
            
            # Tabel untuk evaluasi
            c.execute('''
                CREATE TABLE IF NOT EXISTS evaluation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_samples INTEGER,
                    accuracy REAL,
                    precision REAL,
                    recall REAL,
                    f1_score REAL,
                    specificity REAL,
                    auc REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def insert_detection(self, filename: str, label: str, prediction: str, 
                        ai_score: float, confidence: float, features: Dict[str, float]):
        """Simpan hasil deteksi"""
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO detection_results 
                (filename, label_asli, hasil_prediksi, ai_score, confidence,
                 entropy, texture, fft, edge_density, blur_score, noise_score,
                 histogram_std, brightness, saturation, color_variance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                filename, label, prediction, ai_score, confidence,
                features.get("entropy"), features.get("contrast"),
                features.get("fft_hf_ratio"), features.get("edge_density"),
                features.get("blur_score"), features.get("noise_score"),
                features.get("histogram_std"), features.get("brightness_score"),
                features.get("saturation_score"), features.get("color_variance")
            ))
            conn.commit()
    
    def insert_evaluation(self, total_samples: int, metrics: Dict):
        """Simpan hasil evaluasi"""
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO evaluation_results
                (total_samples, accuracy, precision, recall, f1_score, specificity, auc)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                total_samples,
                metrics.get("accuracy", 0),
                metrics.get("precision", 0),
                metrics.get("recall", 0),
                metrics.get("f1_score", 0),
                metrics.get("specificity", 0),
                metrics.get("auc", 0)
            ))
            conn.commit()
    
    def get_all_detections(self) -> List[Dict]:
        """Dapatkan semua hasil deteksi"""
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM detection_results ORDER BY timestamp DESC')
            rows = c.fetchall()

        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "filename": row[1],
                "label_asli": row[2],
                "hasil_prediksi": row[3],
                "ai_score": row[4],
                "confidence": row[5],
                "timestamp": row[16]
            })
        return results
    
    def export_to_csv(self, output_file: str = "detection_results.csv"):
        """Export hasil ke CSV"""
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM detection_results')
            columns = [description[0] for description in c.description]
            rows = c.fetchall()

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
    
    def get_statistics(self) -> Dict:
        """Dapatkan statistik dari database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM detection_results')
        total = c.fetchone()[0]
        
        c.execute('''
            SELECT hasil_prediksi, COUNT(*) FROM detection_results
            GROUP BY hasil_prediksi
        ''')
        predictions = {}
        for row in c.fetchall():
            predictions[row[0]] = row[1]
        
        c.execute('''
            SELECT AVG(ai_score), AVG(confidence) FROM detection_results
        ''')
        avg_data = c.fetchone()
        
        conn.close()
        
        return {
            "total_detections": total,
            "predictions": predictions,
            "avg_ai_score": avg_data[0] if avg_data[0] else 0,
            "avg_confidence": avg_data[1] if avg_data[1] else 0,
        }
