"""
Testing dan Evaluasi Lengkap AI Detection System
Script untuk test seluruh pipeline dan generate evaluation report
"""

import os
import json
import csv
import numpy as np
from pathlib import Path
from datetime import datetime

from fuzzy_engine import SugenoInferenceEngine, classify_result
from evaluation_engine import EvaluationEngine
from dataset_handler import DatasetLoader, FeatureExtractor, FeatureNormalizer, ResultsDatabase
from heatmap_generator import HeatmapGenerator, HeatmapSaver


class SystemEvaluator:
    """Evaluasi lengkap sistem AI detection"""
    
    def __init__(self):
        self.sugeno_engine = SugenoInferenceEngine()
        self.evaluation_engine = EvaluationEngine()
        self.feature_extractor = FeatureExtractor()
        self.feature_normalizer = FeatureNormalizer()
        self.dataset_loader = DatasetLoader('dataset')
        self.results_db = ResultsDatabase('detection_results.db')
        
        self.results = []
        self.evaluation_report = {}
    
    def load_and_prepare_dataset(self):
        """Load dan prepare dataset untuk evaluasi"""
        print("[1] Loading dataset...")
        images = self.dataset_loader.load_all_images()
        print(f"    Total images: {len(images)}")
        print(f"    AI images: {sum(1 for img in images if img['label'] == 'AI')}")
        print(f"    Human images: {sum(1 for img in images if img['label'] == 'HUMAN')}")
        
        # Fit normalizer dengan semua data
        print("\n[2] Fitting feature normalizer...")
        all_features = []
        for img_data in images:
            features = self.feature_extractor.extract_all_features(img_data['image'])
            all_features.append(features)
        
        self.feature_normalizer.fit(all_features)
        print(f"    Normalizer fitted with {len(all_features)} samples")
        
        return images
    
    def evaluate_image(self, image_data):
        """Evaluasi satu gambar melalui pipeline lengkap"""
        try:
            # Extract features
            features = self.feature_extractor.extract_all_features(image_data['image'])
            
            # Normalize
            normalized_features = self.feature_normalizer.normalize(features)
            
            # Fuzzy inference
            fuzzy_result = self.sugeno_engine.process(normalized_features)
            
            # Classification
            classification = classify_result(fuzzy_result.ai_score)
            
            # Store result
            result = {
                'filename': image_data['filename'],
                'ground_truth': image_data['label'],
                'ai_score': fuzzy_result.ai_score,
                'confidence': fuzzy_result.confidence,
                'classification': classification,
                'correct': (image_data['label'] == 'AI' and classification == 'AI Generated') or \
                          (image_data['label'] == 'HUMAN' and classification == 'Human Made'),
                'fired_rules': fuzzy_result.inference['total_fired'],
                'max_firing_strength': fuzzy_result.inference['max_firing_strength'],
            }
            
            # Add ke evaluation engine
            self.evaluation_engine.add_result(
                image_data['label'],
                fuzzy_result.ai_score,
                classification
            )
            
            # Save ke database
            self.results_db.insert_detection(
                filename=image_data['filename'],
                label=image_data['label'],
                prediction=classification,
                ai_score=fuzzy_result.ai_score,
                confidence=fuzzy_result.confidence,
                features=features
            )
            
            return result
        
        except Exception as e:
            print(f"    Error processing {image_data['filename']}: {e}")
            return None
    
    def run_full_evaluation(self):
        """Jalankan evaluasi lengkap"""
        print("\n[3] Running full system evaluation...\n")
        
        images = self.load_and_prepare_dataset()
        
        print("\n[3] Processing images...")
        for idx, image_data in enumerate(images):
            if (idx + 1) % 10 == 0 or idx == 0:
                print(f"    Progress: {idx + 1}/{len(images)}")
            
            result = self.evaluate_image(image_data)
            if result:
                self.results.append(result)
        
        print(f"\n    Total processed: {len(self.results)}")
        
        # Get evaluation
        self.evaluation_report = self.evaluation_engine.get_full_evaluation()
        
        return self.results
    
    def generate_report(self):
        """Generate evaluation report"""
        print("\n" + "="*80)
        print("AI DETECTION SYSTEM - COMPREHENSIVE EVALUATION REPORT")
        print("="*80)
        
        if not self.evaluation_report:
            print("No evaluation data available")
            return
        
        # Confusion Matrix
        print("\n[CONFUSION MATRIX]")
        cm = self.evaluation_report['confusion_matrix']
        print(f"  True Positives (TP):   {cm['tp']}")
        print(f"  True Negatives (TN):   {cm['tn']}")
        print(f"  False Positives (FP):  {cm['fp']}")
        print(f"  False Negatives (FN):  {cm['fn']}")
        
        # Metrics
        print("\n[PERFORMANCE METRICS]")
        metrics = self.evaluation_report['metrics']
        print(f"  Accuracy:              {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
        print(f"  Precision:             {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
        print(f"  Recall (Sensitivity):  {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
        print(f"  Specificity:           {metrics['specificity']:.4f} ({metrics['specificity']*100:.2f}%)")
        print(f"  F1 Score:              {metrics['f1_score']:.4f}")
        print(f"  False Positive Rate:   {metrics['false_positive_rate']:.4f} ({metrics['false_positive_rate']*100:.2f}%)")
        print(f"  False Negative Rate:   {metrics['false_negative_rate']:.4f} ({metrics['false_negative_rate']*100:.2f}%)")
        
        # ROC AUC
        print("\n[ROC ANALYSIS]")
        roc = self.evaluation_report['roc']
        print(f"  AUC (Area Under Curve): {roc['auc']:.4f}")
        
        # Dataset Statistics
        print("\n[DATASET STATISTICS]")
        stats = self.evaluation_report['dataset_statistics']
        print(f"  Total Samples:         {stats['total_samples']}")
        print(f"  AI Samples:            {stats['ai_samples']}")
        print(f"  Human Samples:         {stats['human_samples']}")
        print(f"  AI Score Mean (AI):    {stats['ai_score_stats']['mean']:.4f}")
        print(f"  AI Score Std (AI):     {stats['ai_score_stats']['std']:.4f}")
        print(f"  AI Score Mean (Human): {stats['human_score_stats']['mean']:.4f}")
        print(f"  AI Score Std (Human):  {stats['human_score_stats']['std']:.4f}")
        
        # Classification Distribution
        print("\n[CLASSIFICATION DISTRIBUTION]")
        for result in self.results:
            if result['ground_truth'] == 'AI':
                if result['classification'] == 'AI Generated':
                    status = "✓ CORRECT"
                else:
                    status = "✗ WRONG"
                print(f"  {result['filename']:40} | Score: {result['ai_score']:.4f} | {status}")
        
        print("\n" + "="*80)
    
    def save_results_to_csv(self, filename='evaluation_results.csv'):
        """Simpan hasil ke CSV"""
        print(f"\n[4] Saving results to {filename}...")
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Filename', 'Ground Truth', 'Classification', 'AI Score', 
                'Confidence', 'Correct', 'Fired Rules', 'Max Firing Strength'
            ])
            
            for result in self.results:
                writer.writerow([
                    result['filename'],
                    result['ground_truth'],
                    result['classification'],
                    f"{result['ai_score']:.4f}",
                    f"{result['confidence']:.4f}",
                    "Yes" if result['correct'] else "No",
                    result['fired_rules'],
                    f"{result['max_firing_strength']:.4f}",
                ])
        
        print(f"    Results saved to {filename}")
    
    def save_evaluation_report(self, filename='evaluation_report.json'):
        """Simpan evaluation report ke JSON"""
        print(f"\n[5] Saving evaluation report to {filename}...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_config': {
                'fuzzy_engine': 'Sugeno',
                'total_rules': 55,
                'thresholds': {
                    'ai': 0.65,
                    'uncertain_high': 0.64,
                    'uncertain_low': 0.45,
                    'human': 0.45
                }
            },
            'evaluation': self.evaluation_report
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"    Report saved to {filename}")
    
    def export_database_to_csv(self, filename='database_export.csv'):
        """Export database ke CSV"""
        print(f"\n[6] Exporting database to {filename}...")
        self.results_db.export_to_csv(filename)
        print(f"    Database exported to {filename}")


def main():
    """Main evaluation script"""
    print("\n" + "="*80)
    print("AI DETECTION SYSTEM - COMPREHENSIVE TESTING & EVALUATION")
    print("="*80)
    
    # Create evaluator
    evaluator = SystemEvaluator()
    
    # Run evaluation
    evaluator.run_full_evaluation()
    
    # Generate and print report
    evaluator.generate_report()
    
    # Save results
    evaluator.save_results_to_csv('evaluation_results.csv')
    evaluator.save_evaluation_report('evaluation_report.json')
    evaluator.export_database_to_csv('database_export.csv')
    
    print("\n" + "="*80)
    print("EVALUATION COMPLETED")
    print("="*80)
    print("\nGenerated files:")
    print("  - evaluation_results.csv")
    print("  - evaluation_report.json")
    print("  - database_export.csv")
    print("  - detection_results.db")
    print("\n")


if __name__ == '__main__':
    main()
