"""
Evaluation Engine untuk mengukur performa sistem deteksi AI
Menghitung: Confusion Matrix, Accuracy, Precision, Recall, F1 Score, ROC Curve
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import json


@dataclass
class ConfusionMatrixData:
    """Data confusion matrix"""
    tp: int  # True Positive (AI detected as AI)
    tn: int  # True Negative (Human detected as Human)
    fp: int  # False Positive (Human detected as AI)
    fn: int  # False Negative (AI detected as Human)
    
    def to_dict(self):
        return asdict(self)


@dataclass
class PerformanceMetrics:
    """Metrik performa sistem"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    specificity: float
    sensitivity: float
    false_positive_rate: float
    false_negative_rate: float
    
    def to_dict(self):
        return asdict(self)


class ConfusionMatrix:
    """Kelas untuk menghitung dan merepresentasikan confusion matrix"""
    
    def __init__(self):
        self.tp = 0  # AI detected as AI
        self.tn = 0  # Human detected as Human
        self.fp = 0  # Human detected as AI
        self.fn = 0  # AI detected as Human
        self.predictions = []  # Menyimpan semua prediksi untuk analisis
    
    def add_prediction(self, ground_truth: str, prediction: str, ai_score: float):
        """
        Tambahkan satu prediksi ke confusion matrix
        ground_truth: "AI" atau "HUMAN"
        prediction: "AI Generated", "Uncertain", "Human Made"
        """
        self.predictions.append({
            "ground_truth": ground_truth,
            "prediction": prediction,
            "ai_score": ai_score
        })
        
        # Map prediction to classes; treat 'Uncertain' explicitly (do not count as TP/TN)
        if prediction == "AI Generated":
            pred_class = "AI"
        elif prediction == "Human Made":
            pred_class = "HUMAN"
        else:
            pred_class = "UNCERTAIN"

        truth_class = ground_truth

        # If prediction is UNCERTAIN, do not increment TP/TN/FP/FN (uncertain not counted as correct)
        if pred_class == "UNCERTAIN":
            return

        if truth_class == "AI":
            if pred_class == "AI":
                self.tp += 1
            else:
                self.fn += 1
        else:  # truth_class == "HUMAN"
            if pred_class == "HUMAN":
                self.tn += 1
            else:
                self.fp += 1
    
    def get_matrix(self) -> ConfusionMatrixData:
        """Return confusion matrix data"""
        return ConfusionMatrixData(tp=self.tp, tn=self.tn, fp=self.fp, fn=self.fn)
    
    def get_matrix_array(self) -> np.ndarray:
        """Return confusion matrix sebagai array 2D untuk visualization"""
        return np.array([
            [self.tp, self.fn],
            [self.fp, self.tn]
        ])
    
    def reset(self):
        """Reset confusion matrix"""
        self.tp = 0
        self.tn = 0
        self.fp = 0
        self.fn = 0
        self.predictions = []


class PerformanceEvaluator:
    """Menghitung metrik performa dari confusion matrix"""
    
    @staticmethod
    def calculate_metrics(cm: ConfusionMatrixData) -> PerformanceMetrics:
        """
        Hitung semua metrik performa dari confusion matrix
        """
        tp, tn, fp, fn = cm.tp, cm.tn, cm.fp, cm.fn
        
        # Total samples
        total = tp + tn + fp + fn
        
        # Accuracy: (TP + TN) / Total
        accuracy = (tp + tn) / total if total > 0 else 0.0
        
        # Precision: TP / (TP + FP)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        
        # Recall (Sensitivity): TP / (TP + FN)
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        # F1 Score: 2 * (Precision * Recall) / (Precision + Recall)
        if (precision + recall) > 0:
            f1_score = 2 * (precision * recall) / (precision + recall)
        else:
            f1_score = 0.0
        
        # Specificity: TN / (TN + FP)
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        
        # Sensitivity = Recall
        sensitivity = recall
        
        # False Positive Rate: FP / (FP + TN)
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        
        # False Negative Rate: FN / (FN + TP)
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
        
        return PerformanceMetrics(
            accuracy=float(accuracy),
            precision=float(precision),
            recall=float(recall),
            f1_score=float(f1_score),
            specificity=float(specificity),
            sensitivity=float(sensitivity),
            false_positive_rate=float(fpr),
            false_negative_rate=float(fnr)
        )
    
    @staticmethod
    def get_classification_report(cm: ConfusionMatrix, metrics: PerformanceMetrics) -> Dict:
        """Generate classification report"""
        matrix_data = cm.get_matrix()
        
        return {
            "confusion_matrix": matrix_data.to_dict(),
            "metrics": metrics.to_dict(),
            "total_samples": sum([matrix_data.tp, matrix_data.tn, matrix_data.fp, matrix_data.fn]),
            "ai_samples": sum([matrix_data.tp, matrix_data.fn]),
            "human_samples": sum([matrix_data.tn, matrix_data.fp]),
        }


class ROCAnalysis:
    """ROC Curve Analysis"""
    
    def __init__(self):
        self.thresholds = np.linspace(0, 1, 101)
        self.tpr_values = []
        self.fpr_values = []
        self.auc = 0.0
    
    def calculate_roc(self, predictions: List[Dict]) -> Tuple[List[float], List[float], float]:
        """
        Hitung ROC curve dari predictions
        predictions: list of {"ground_truth": "AI"/"HUMAN", "ai_score": float}
        """
        ai_scores = np.array([p["ai_score"] for p in predictions])
        true_labels = np.array([1 if p["ground_truth"] == "AI" else 0 for p in predictions])
        
        tpr_list = []
        fpr_list = []
        
        for threshold in self.thresholds:
            # Predictions dengan threshold
            predicted_positive = ai_scores >= threshold
            
            # TP dan FN (actual positive)
            actual_positive = true_labels == 1
            tp = np.sum(predicted_positive & actual_positive)
            fn = np.sum(~predicted_positive & actual_positive)
            
            # FP dan TN (actual negative)
            actual_negative = true_labels == 0
            fp = np.sum(predicted_positive & actual_negative)
            tn = np.sum(~predicted_positive & actual_negative)
            
            # TPR dan FPR
            tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
            
            tpr_list.append(tpr)
            fpr_list.append(fpr)
        
        self.tpr_values = tpr_list
        self.fpr_values = fpr_list
        
        # Hitung AUC menggunakan trapezoidal rule
        self.auc = self._calculate_auc(fpr_list, tpr_list)
        
        return fpr_list, tpr_list, self.auc
    
    @staticmethod
    def _calculate_auc(fpr: List[float], tpr: List[float]) -> float:
        """Hitung AUC menggunakan trapezoidal rule"""
        fpr = np.array(fpr)
        tpr = np.array(tpr)
        
        # Sort by FPR
        sorted_indices = np.argsort(fpr)
        fpr = fpr[sorted_indices]
        tpr = tpr[sorted_indices]
        
        # Trapezoidal integration
        auc = 0.0
        for i in range(len(fpr) - 1):
            auc += (fpr[i + 1] - fpr[i]) * (tpr[i + 1] + tpr[i]) / 2
        
        return float(np.clip(auc, 0, 1))
    
    def get_roc_data(self) -> Dict:
        """Return ROC curve data untuk plotting"""
        return {
            "fpr": self.fpr_values,
            "tpr": self.tpr_values,
            "auc": self.auc,
            "thresholds": self.thresholds.tolist()
        }


class DatasetStatistics:
    """Statistik dataset"""
    
    def __init__(self):
        self.ai_count = 0
        self.human_count = 0
        self.ai_scores = []
        self.human_scores = []
        self.predictions = []
    
    def add_prediction(self, ground_truth: str, ai_score: float, classification: str):
        """Tambahkan prediksi untuk statistik"""
        self.predictions.append({
            "ground_truth": ground_truth,
            "ai_score": ai_score,
            "classification": classification
        })
        
        if ground_truth == "AI":
            self.ai_count += 1
            self.ai_scores.append(ai_score)
        else:
            self.human_count += 1
            self.human_scores.append(ai_score)
    
    def get_statistics(self) -> Dict:
        """Dapatkan statistik dataset"""
        ai_scores_arr = np.array(self.ai_scores) if self.ai_scores else np.array([])
        human_scores_arr = np.array(self.human_scores) if self.human_scores else np.array([])
        
        stats = {
            "total_samples": self.ai_count + self.human_count,
            "ai_samples": self.ai_count,
            "human_samples": self.human_count,
            "ai_percentage": (self.ai_count / (self.ai_count + self.human_count) * 100) if (self.ai_count + self.human_count) > 0 else 0,
            "ai_score_stats": {
                "mean": float(np.mean(ai_scores_arr)) if len(ai_scores_arr) > 0 else 0,
                "std": float(np.std(ai_scores_arr)) if len(ai_scores_arr) > 0 else 0,
                "min": float(np.min(ai_scores_arr)) if len(ai_scores_arr) > 0 else 0,
                "max": float(np.max(ai_scores_arr)) if len(ai_scores_arr) > 0 else 0,
                "median": float(np.median(ai_scores_arr)) if len(ai_scores_arr) > 0 else 0,
            },
            "human_score_stats": {
                "mean": float(np.mean(human_scores_arr)) if len(human_scores_arr) > 0 else 0,
                "std": float(np.std(human_scores_arr)) if len(human_scores_arr) > 0 else 0,
                "min": float(np.min(human_scores_arr)) if len(human_scores_arr) > 0 else 0,
                "max": float(np.max(human_scores_arr)) if len(human_scores_arr) > 0 else 0,
                "median": float(np.median(human_scores_arr)) if len(human_scores_arr) > 0 else 0,
            },
            "predictions": self.predictions
        }
        
        return stats
    
    def get_distribution_histogram(self, bins=20) -> Dict:
        """Dapatkan distribusi histogram AI scores"""
        all_scores = self.ai_scores + self.human_scores
        
        if not all_scores:
            return {"bins": [], "counts": [], "labels": []}
        
        counts, bin_edges = np.histogram(all_scores, bins=bins, range=(0, 1))
        
        return {
            "bins": bin_edges.tolist(),
            "counts": counts.tolist(),
            "ai_counts": np.histogram(self.ai_scores, bins=bins, range=(0, 1))[0].tolist() if self.ai_scores else [],
            "human_counts": np.histogram(self.human_scores, bins=bins, range=(0, 1))[0].tolist() if self.human_scores else [],
        }
    
    def reset(self):
        """Reset statistik"""
        self.ai_count = 0
        self.human_count = 0
        self.ai_scores = []
        self.human_scores = []
        self.predictions = []


class EvaluationEngine:
    """Engine utama untuk evaluasi sistem"""
    
    def __init__(self):
        self.confusion_matrix = ConfusionMatrix()
        self.roc_analysis = ROCAnalysis()
        self.dataset_stats = DatasetStatistics()
        self.evaluator = PerformanceEvaluator()
    
    def add_result(self, ground_truth: str, ai_score: float, classification: str):
        """
        Tambahkan hasil deteksi untuk evaluasi
        """
        self.confusion_matrix.add_prediction(ground_truth, classification, ai_score)
        self.dataset_stats.add_prediction(ground_truth, ai_score, classification)
    
    def get_full_evaluation(self) -> Dict:
        """Dapatkan evaluasi lengkap"""
        matrix_data = self.confusion_matrix.get_matrix()
        metrics = self.evaluator.calculate_metrics(matrix_data)
        
        # Calculate ROC
        predictions_for_roc = [
            {"ground_truth": p["ground_truth"], "ai_score": p["ai_score"]}
            for p in self.confusion_matrix.predictions
        ]
        if predictions_for_roc:
            self.roc_analysis.calculate_roc(predictions_for_roc)
        
        return {
            "confusion_matrix": matrix_data.to_dict(),
            "metrics": metrics.to_dict(),
            "confusion_matrix_array": self.confusion_matrix.get_matrix_array().tolist(),
            "roc": self.roc_analysis.get_roc_data(),
            "dataset_statistics": self.dataset_stats.get_statistics(),
            "distribution": self.dataset_stats.get_distribution_histogram(),
            "total_evaluated": len(self.confusion_matrix.predictions),
        }
    
    def reset(self):
        """Reset engine"""
        self.confusion_matrix.reset()
        self.roc_analysis = ROCAnalysis()
        self.dataset_stats.reset()
