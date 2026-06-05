"""
Fuzzy Logic Sugeno Inference Engine untuk AI Image Detection
Implementasi lengkap dengan membership functions, rules, dan defuzzification
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class FuzzySet(Enum):
    """Enum untuk himpunan fuzzy"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


@dataclass
class FuzzyResult:
    """Hasil dari fuzzy inference"""
    ai_score: float
    confidence: float
    fuzzification: Dict
    inference: Dict
    defuzzification: Dict


class MembershipFunction:
    """Membership function untuk fuzzifikasi"""
    
    @staticmethod
    def triangular(x: float, a: float, b: float, c: float) -> float:
        """
        Triangular membership function
        a: left peak, b: center, c: right peak
        """
        if x <= a or x >= c:
            return 0.0
        if x <= b:
            return (x - a) / (b - a) if b > a else 0.0
        return (c - x) / (c - b) if c > b else 0.0
    
    @staticmethod
    def trapezoidal(x: float, a: float, b: float, c: float, d: float) -> float:
        """
        Trapezoidal membership function
        a: left slope start, b: left peak, c: right peak, d: right slope end
        """
        if x <= a or x >= d:
            return 0.0
        if x <= b:
            return (x - a) / (b - a) if b > a else 0.0
        if x <= c:
            return 1.0
        return (d - x) / (d - c) if d > c else 0.0
    
    @staticmethod
    def sigmoid(x: float, center: float, steepness: float = 1.0) -> float:
        """Sigmoid membership function"""
        return 1.0 / (1.0 + np.exp(-steepness * (x - center)))


class FuzzyVariables:
    """Definisi variabel fuzzy dan membership functions"""
    
    def __init__(self):
        # Use tighter, less overlapping membership parameterization per request
        # Low: 0.00 - 0.30, Medium: 0.25 - 0.60, High: 0.55 - 1.00
        template_low = (0.0, 0.0, 0.20, 0.30)
        template_med = (0.25, 0.425, 0.60)
        template_high = (0.55, 0.70, 1.0, 1.0)

        # For each input variable we'll use the same scheme (can be tuned per-var)
        self.entropy_ranges = {"Low": template_low, "Medium": template_med, "High": template_high}
        self.texture_ranges = {"Low": template_low, "Medium": template_med, "High": template_high}
        self.edge_density_ranges = {"Low": template_low, "Medium": template_med, "High": template_high}
        self.fft_ranges = {"Low": template_low, "Medium": template_med, "High": template_high}
        self.blur_ranges = {"Low": template_low, "Medium": template_med, "High": template_high}
        self.noise_ranges = {"Low": template_low, "Medium": template_med, "High": template_high}
        self.histogram_ranges = {"Low": template_low, "Medium": template_med, "High": template_high}
        self.brightness_ranges = {"Low": template_low, "Medium": template_med, "High": template_high}
        self.contrast_ranges = {"Low": template_low, "Medium": template_med, "High": template_high}

        # Output targets for Sugeno rules (fixed discrete outputs to reduce mid-values)
        # Use user-requested canonical outputs: Human=0.20, Uncertain=0.50, AI=0.85
        self.output_targets = {"HUMAN": 0.20, "UNCERTAIN": 0.50, "AI": 0.85}
    
    def fuzzify_value(self, value: float, ranges: Dict) -> Dict[str, float]:
        """Fuzzifikasi nilai ke himpunan fuzzy"""
        result = {}
        # ranges for each label may be either a 3-tuple (triangular) or 4-tuple (trapezoid)
        for label, params in ranges.items():
            if len(params) == 3:
                a, b, c = params
                result[label] = MembershipFunction.triangular(value, a, b, c)
            elif len(params) == 4:
                a, b, c, d = params
                result[label] = MembershipFunction.trapezoidal(value, a, b, c, d)
            else:
                result[label] = 0.0

        return result


class SugenoRules:
    """Kumpulan fuzzy rules untuk inferensi Sugeno"""
    
    def __init__(self):
        self.output_targets = {
            "HUMAN": 0.20,
            "UNCERTAIN": 0.50,
            "AI": 0.85
        }
        self.rules = self._create_rules()
    
    def _create_rules(self) -> List[Dict]:
        """
        Membuat 50+ fuzzy rules untuk AI detection
        Setiap rule: IF (conditions) THEN (output_weight)
        Output weight antara 0 (Human) hingga 1 (AI)
        """
        rules = [
            # Rules untuk deteksi AI (output tinggi)
            {"name": "R1", "conditions": {"entropy": "HIGH", "fft": "HIGH", "texture": "LOW"}, "weight": 0.95, "confidence": 0.9},
            {"name": "R2", "conditions": {"entropy": "HIGH", "edge_density": "HIGH", "noise": "MEDIUM"}, "weight": 0.88, "confidence": 0.85},
            {"name": "R3", "conditions": {"entropy": "MEDIUM", "fft": "HIGH", "blur": "HIGH"}, "weight": 0.82, "confidence": 0.8},
            {"name": "R4", "conditions": {"texture": "LOW", "histogram": "HIGH", "brightness": "MEDIUM"}, "weight": 0.80, "confidence": 0.78},
            {"name": "R5", "conditions": {"fft": "HIGH", "noise": "MEDIUM", "contrast": "HIGH"}, "weight": 0.85, "confidence": 0.82},
            {"name": "R6", "conditions": {"entropy": "HIGH", "blur": "MEDIUM", "edge_density": "MEDIUM"}, "weight": 0.78, "confidence": 0.75},
            {"name": "R7", "conditions": {"texture": "MEDIUM", "fft": "HIGH", "histogram": "MEDIUM"}, "weight": 0.80, "confidence": 0.77},
            {"name": "R8", "conditions": {"entropy": "HIGH", "noise": "LOW", "fft": "HIGH"}, "weight": 0.90, "confidence": 0.88},
            {"name": "R9", "conditions": {"histogram": "HIGH", "blur": "HIGH", "texture": "LOW"}, "weight": 0.83, "confidence": 0.81},
            {"name": "R10", "conditions": {"fft": "HIGH", "contrast": "HIGH", "entropy": "MEDIUM"}, "weight": 0.81, "confidence": 0.79},
            
            # Rules untuk deteksi HUMAN (output rendah)
            {"name": "R11", "conditions": {"entropy": "LOW", "fft": "LOW", "texture": "HIGH"}, "weight": 0.15, "confidence": 0.9},
            {"name": "R12", "conditions": {"entropy": "LOW", "edge_density": "LOW", "noise": "LOW"}, "weight": 0.12, "confidence": 0.85},
            {"name": "R13", "conditions": {"texture": "HIGH", "fft": "LOW", "blur": "LOW"}, "weight": 0.18, "confidence": 0.8},
            {"name": "R14", "conditions": {"histogram": "LOW", "texture": "HIGH", "brightness": "MEDIUM"}, "weight": 0.20, "confidence": 0.78},
            {"name": "R15", "conditions": {"fft": "LOW", "noise": "LOW", "contrast": "LOW"}, "weight": 0.10, "confidence": 0.82},
            {"name": "R16", "conditions": {"entropy": "LOW", "blur": "LOW", "edge_density": "LOW"}, "weight": 0.14, "confidence": 0.75},
            {"name": "R17", "conditions": {"texture": "HIGH", "fft": "LOW", "histogram": "LOW"}, "weight": 0.16, "confidence": 0.77},
            {"name": "R18", "conditions": {"entropy": "LOW", "noise": "LOW", "fft": "LOW"}, "weight": 0.08, "confidence": 0.88},
            {"name": "R19", "conditions": {"histogram": "LOW", "blur": "LOW", "texture": "HIGH"}, "weight": 0.17, "confidence": 0.81},
            {"name": "R20", "conditions": {"fft": "LOW", "contrast": "LOW", "entropy": "LOW"}, "weight": 0.11, "confidence": 0.79},
            
            # Rules untuk kasus intermediate
            {"name": "R21", "conditions": {"entropy": "MEDIUM", "texture": "MEDIUM", "fft": "MEDIUM"}, "weight": 0.50, "confidence": 0.65},
            {"name": "R22", "conditions": {"noise": "MEDIUM", "blur": "MEDIUM", "edge_density": "MEDIUM"}, "weight": 0.48, "confidence": 0.62},
            {"name": "R23", "conditions": {"entropy": "HIGH", "texture": "HIGH", "blur": "LOW"}, "weight": 0.72, "confidence": 0.70},
            {"name": "R24", "conditions": {"histogram": "MEDIUM", "brightness": "HIGH", "contrast": "MEDIUM"}, "weight": 0.58, "confidence": 0.68},
            {"name": "R25", "conditions": {"fft": "MEDIUM", "noise": "HIGH", "texture": "LOW"}, "weight": 0.65, "confidence": 0.72},
            {"name": "R26", "conditions": {"entropy": "LOW", "fft": "MEDIUM", "texture": "MEDIUM"}, "weight": 0.35, "confidence": 0.60},
            {"name": "R27", "conditions": {"blur": "HIGH", "edge_density": "HIGH", "texture": "MEDIUM"}, "weight": 0.70, "confidence": 0.68},
            {"name": "R28", "conditions": {"noise": "LOW", "histogram": "HIGH", "entropy": "MEDIUM"}, "weight": 0.62, "confidence": 0.65},
            {"name": "R29", "conditions": {"contrast": "HIGH", "brightness": "MEDIUM", "fft": "MEDIUM"}, "weight": 0.60, "confidence": 0.63},
            {"name": "R30", "conditions": {"texture": "MEDIUM", "entropy": "MEDIUM", "blur": "MEDIUM"}, "weight": 0.52, "confidence": 0.64},
            
            # Rules tambahan untuk spesifikasi tinggi
            {"name": "R31", "conditions": {"entropy": "HIGH", "fft": "HIGH", "noise": "HIGH", "texture": "LOW"}, "weight": 0.92, "confidence": 0.87},
            {"name": "R32", "conditions": {"edge_density": "HIGH", "histogram": "HIGH", "brightness": "HIGH"}, "weight": 0.86, "confidence": 0.84},
            {"name": "R33", "conditions": {"entropy": "LOW", "texture": "HIGH", "noise": "LOW", "fft": "LOW"}, "weight": 0.13, "confidence": 0.86},
            {"name": "R34", "conditions": {"blur": "LOW", "edge_density": "LOW", "histogram": "LOW"}, "weight": 0.14, "confidence": 0.83},
            {"name": "R35", "conditions": {"fft": "HIGH", "entropy": "HIGH", "blur": "LOW", "texture": "LOW"}, "weight": 0.89, "confidence": 0.86},
            {"name": "R36", "conditions": {"noise": "MEDIUM", "contrast": "HIGH", "fft": "HIGH"}, "weight": 0.84, "confidence": 0.81},
            {"name": "R37", "conditions": {"entropy": "LOW", "noise": "LOW", "texture": "HIGH", "fft": "LOW"}, "weight": 0.11, "confidence": 0.84},
            {"name": "R38", "conditions": {"blur": "LOW", "texture": "HIGH", "noise": "LOW"}, "weight": 0.16, "confidence": 0.80},
            {"name": "R39", "conditions": {"entropy": "MEDIUM", "fft": "HIGH", "texture": "LOW", "noise": "MEDIUM"}, "weight": 0.79, "confidence": 0.76},
            {"name": "R40", "conditions": {"histogram": "MEDIUM", "entropy": "MEDIUM", "brightness": "MEDIUM"}, "weight": 0.50, "confidence": 0.61},
            
            # Rules tambahan untuk kompleksitas lebih tinggi
            {"name": "R41", "conditions": {"entropy": "HIGH", "fft": "HIGH", "edge_density": "HIGH", "blur": "MEDIUM"}, "weight": 0.87, "confidence": 0.85},
            {"name": "R42", "conditions": {"texture": "LOW", "noise": "MEDIUM", "fft": "HIGH", "histogram": "HIGH"}, "weight": 0.85, "confidence": 0.83},
            {"name": "R43", "conditions": {"entropy": "LOW", "texture": "HIGH", "blur": "LOW", "edge_density": "LOW"}, "weight": 0.12, "confidence": 0.85},
            {"name": "R44", "conditions": {"fft": "LOW", "noise": "LOW", "texture": "HIGH", "contrast": "MEDIUM"}, "weight": 0.14, "confidence": 0.81},
            {"name": "R45", "conditions": {"entropy": "HIGH", "blur": "HIGH", "histogram": "HIGH", "fft": "MEDIUM"}, "weight": 0.81, "confidence": 0.78},
            {"name": "R46", "conditions": {"texture": "MEDIUM", "entropy": "LOW", "fft": "MEDIUM", "noise": "LOW"}, "weight": 0.32, "confidence": 0.62},
            {"name": "R47", "conditions": {"entropy": "MEDIUM", "fft": "MEDIUM", "blur": "MEDIUM", "texture": "MEDIUM"}, "weight": 0.51, "confidence": 0.60},
            {"name": "R48", "conditions": {"noise": "HIGH", "entropy": "HIGH", "contrast": "HIGH", "fft": "HIGH"}, "weight": 0.88, "confidence": 0.82},
            {"name": "R49", "conditions": {"blur": "HIGH", "histogram": "LOW", "texture": "HIGH", "entropy": "LOW"}, "weight": 0.25, "confidence": 0.65},
            {"name": "R50", "conditions": {"edge_density": "MEDIUM", "entropy": "MEDIUM", "fft": "MEDIUM", "texture": "MEDIUM"}, "weight": 0.52, "confidence": 0.63},
            
            # Rules final untuk edge cases
            {"name": "R51", "conditions": {"entropy": "HIGH", "fft": "HIGH", "texture": "LOW", "noise": "LOW"}, "weight": 0.91, "confidence": 0.88},
            {"name": "R52", "conditions": {"entropy": "LOW", "fft": "LOW", "texture": "HIGH", "noise": "LOW"}, "weight": 0.09, "confidence": 0.87},
            {"name": "R53", "conditions": {"blur": "MEDIUM", "histogram": "MEDIUM", "brightness": "MEDIUM"}, "weight": 0.49, "confidence": 0.61},
            {"name": "R54", "conditions": {"contrast": "MEDIUM", "fft": "MEDIUM", "entropy": "MEDIUM"}, "weight": 0.50, "confidence": 0.62},
            {"name": "R55", "conditions": {"texture": "LOW", "fft": "HIGH", "edge_density": "HIGH"}, "weight": 0.86, "confidence": 0.83},
        ]
        # Remap rule weights to canonical Sugeno outputs to avoid mid-value crowding
        for r in rules:
            orig_w = r.get("weight", 0.5)
            # Strong AI-like rules keep AI output
            if orig_w >= 0.7:
                r["weight"] = self.output_targets["AI"]
            # Strong Human-like rules
            elif orig_w <= 0.25:
                r["weight"] = self.output_targets["HUMAN"]
            else:
                # Intermediate rules map to Uncertain
                r["weight"] = self.output_targets["UNCERTAIN"]

        return rules
    
    def get_fired_rules(self, fuzzification: Dict[str, Dict[str, float]]) -> List[Tuple[Dict, float]]:
        """
        Dapatkan rules yang fire berdasarkan membership degrees fuzzy
        Return: list of (rule, firing_strength)
        """
        fired = []
        for rule in self.rules:
            degrees = []
            for feature, fuzzy_set in rule["conditions"].items():
                feature_membership = fuzzification.get(feature, {})
                degrees.append(feature_membership.get(fuzzy_set, 0.0))

            firing_strength = min(degrees) if degrees else 0.0

            # Only include meaningful firing strengths
            if firing_strength > 0.05:
                fired.append((rule, float(firing_strength)))

        return fired


class SugenoInferenceEngine:
    """Fuzzy Sugeno Inference Engine utama"""
    
    def __init__(self):
        self.fuzzy_vars = FuzzyVariables()
        self.rules = SugenoRules()
        self.max_firing_strength = 0.0
        self.fired_rules_count = 0
    
    def fuzzify(self, features: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """
        Fuzzifikasi input features ke himpunan fuzzy
        """
        fuzzification = {}
        
        # Fuzzify entropy
        if "entropy" in features:
            fuzzification["entropy"] = self._fuzzify_feature(
                features["entropy"], 
                self.fuzzy_vars.entropy_ranges
            )
        
        # Fuzzify texture (contrast)
        if "contrast" in features:
            fuzzification["texture"] = self._fuzzify_feature(
                features["contrast"],
                self.fuzzy_vars.texture_ranges
            )
        
        # Fuzzify edge density
        if "edge_density" in features:
            normalized_edge = np.clip(features["edge_density"] / 100.0, 0, 1)
            fuzzification["edge_density"] = self._fuzzify_feature(
                normalized_edge,
                self.fuzzy_vars.edge_density_ranges
            )
        
        # Fuzzify FFT
        if "fft_hf_ratio" in features:
            fuzzification["fft"] = self._fuzzify_feature(
                features["fft_hf_ratio"],
                self.fuzzy_vars.fft_ranges
            )
        
        # Fuzzify blur
        if "blur_score" in features:
            fuzzification["blur"] = self._fuzzify_feature(
                features["blur_score"],
                self.fuzzy_vars.blur_ranges
            )
        
        # Fuzzify noise
        if "noise_score" in features:
            fuzzification["noise"] = self._fuzzify_feature(
                features["noise_score"],
                self.fuzzy_vars.noise_ranges
            )
        
        # Fuzzify histogram entropy
        if "histogram_std" in features:
            normalized_hist = np.clip(features["histogram_std"] / 100.0, 0, 1)
            fuzzification["histogram"] = self._fuzzify_feature(
                normalized_hist,
                self.fuzzy_vars.histogram_ranges
            )
        
        # Fuzzify brightness
        if "brightness_score" in features:
            fuzzification["brightness"] = self._fuzzify_feature(
                features["brightness_score"],
                self.fuzzy_vars.brightness_ranges
            )
        
        return fuzzification
    
    def _fuzzify_feature(self, value: float, ranges: Dict) -> Dict[str, float]:
        """Fuzzifikasi satu feature ke membership values"""
        result = {}
        # ranges argument expected to have labels 'Low','Medium','High'
        for lab in ["Low", "Medium", "High"]:
            params = ranges.get(lab)
            if not params:
                result[lab.upper()] = 0.0
                continue
            if len(params) == 3:
                a, b, c = params
                mem = MembershipFunction.triangular(value, a, b, c)
            else:
                a, b, c, d = params
                mem = MembershipFunction.trapezoidal(value, a, b, c, d)
            result[lab.upper()] = mem

        # Normalize by max (not forcing sum to 1 to avoid smoothing all to center)
        maxv = max(result.values()) if result else 0.0
        if maxv > 0:
            for k in result:
                result[k] = result[k] / maxv

        return result
    
    def _get_fuzzy_set(self, membership_dict: Dict[str, float]) -> str:
        """Dapatkan fuzzy set yang dominan"""
        if not membership_dict:
            return "MEDIUM"
        
        max_key = max(membership_dict, key=membership_dict.get)
        return max_key
    
    def inference(self, fuzzification: Dict[str, Dict[str, float]]) -> Dict:
        """
        Lakukan inference menggunakan fired rules
        """
        inference_result = {
            "fired_rules": [],
            "total_fired": 0,
            "total_rules": len(self.rules.rules),
            "weighted_sum": 0.0,
            "weight_sum": 0.0,
            "max_firing_strength": 0.0,
        }
        
# Get fired rules using actual membership degrees directly
        fired_rules = self.rules.get_fired_rules(fuzzification)
        
        weighted_sum = 0.0
        weight_sum = 0.0
        
        for rule, firing_strength in fired_rules:
            weighted_sum += rule["weight"] * firing_strength
            weight_sum += firing_strength
            
            inference_result["fired_rules"].append({
                "name": rule["name"],
                "weight": rule["weight"],
                "firing_strength": firing_strength,
                "conditions": rule["conditions"],
            })
            
            if firing_strength > inference_result["max_firing_strength"]:
                inference_result["max_firing_strength"] = firing_strength
        
        inference_result["total_fired"] = len(fired_rules)
        inference_result["weighted_sum"] = weighted_sum
        inference_result["weight_sum"] = weight_sum
        
        self.fired_rules_count = len(fired_rules)
        self.max_firing_strength = inference_result["max_firing_strength"]
        
        return inference_result
    
    def defuzzify(self, inference_result: Dict) -> Tuple[float, float]:
        """
        Defuzzifikasi menggunakan weighted average (Sugeno method)
        Return: (ai_score, confidence)
        """
        weight_sum = inference_result["weight_sum"]
        weighted_sum = inference_result["weighted_sum"]
        
        if weight_sum > 0:
            ai_score = weighted_sum / weight_sum
        else:
            ai_score = 0.5  # Default ke uncertain
        
        # Confidence berdasarkan firing strength dan jumlah rules yang fire
        max_firing = inference_result["max_firing_strength"]
        confidence = np.clip(max_firing, 0.3, 1.0)
        
        # Boost confidence jika banyak rules yang fire
        if inference_result["total_fired"] >= 3:
            confidence *= 1.1
        
        confidence = np.clip(confidence, 0, 1)
        
        return float(ai_score), float(confidence)
    
    def process(self, features: Dict[str, float]) -> FuzzyResult:
        """
        Pipeline lengkap: fuzzify -> inference -> defuzzify
        """
        fuzzification = self.fuzzify(features)
        inference = self.inference(fuzzification)
        ai_score, confidence = self.defuzzify(inference)
        
        return FuzzyResult(
            ai_score=ai_score,
            confidence=confidence,
            fuzzification=fuzzification,
            inference=inference,
            defuzzification={"ai_score": ai_score, "confidence": confidence}
        )


# Threshold untuk klasifikasi akhir
CLASSIFICATION_THRESHOLDS = {
    "AI": 0.65,
    "UNCERTAIN_HIGH": 0.64,
    "UNCERTAIN_LOW": 0.45,
    "HUMAN": 0.45,
}


def classify_result(ai_score: float) -> str:
    """
    Klasifikasi hasil berdasarkan AI score
    """
    if ai_score >= CLASSIFICATION_THRESHOLDS["AI"]:
        return "AI Generated"
    elif ai_score >= CLASSIFICATION_THRESHOLDS["UNCERTAIN_LOW"]:
        return "Uncertain"
    else:
        return "Human Made"


def get_confidence_color(classification: str) -> str:
    """Get warna HTML berdasarkan klasifikasi"""
    if classification == "AI Generated":
        return "#FF4444"  # Red
    elif classification == "Uncertain":
        return "#FFD700"  # Yellow
    else:
        return "#44FF44"  # Green
