"""
AI Detection System Backend
Integrasi lengkap dengan Fuzzy Logic Sugeno, Dataset Handler, Evaluation Engine, dan Heatmap Generator
"""

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import cv2
import os
import uuid
import json
from datetime import datetime
import traceback

# Import modul-modul yang telah dibuat
from fuzzy_engine import SugenoInferenceEngine, classify_result, get_confidence_color
from evaluation_engine import EvaluationEngine, ConfusionMatrix, DatasetStatistics
from dataset_handler import DatasetLoader, FeatureExtractor, FeatureNormalizer, ResultsDatabase
from heatmap_generator import HeatmapGenerator, HeatmapSaver, GradCAMDetector

# Try importing OpenAI integration (optional)
try:
    from openai_integration import get_ai_insight, get_openai_status
except ImportError:
    print("Warning: OpenAI integration not available")
    get_ai_insight = None
    get_openai_status = None

# Pengecekan versi library
def check_library_versions():
    try:
        import skimage
        print(f"scikit-image version: {skimage.__version__}")
        import cv2
        print(f"OpenCV version: {cv2.__version__}")
        import flask
        print(f"Flask version: {flask.__version__}")
        import PIL
        print(f"Pillow version: {PIL.__version__}")
        print(f"NumPy version: {np.__version__}")
    except ImportError as e:
        print(f"Error importing library: {e}")

check_library_versions()

# Flask app configuration
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/assets/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB
app.config['HISTORY_FILE'] = 'detection_history.json'

# Initialize engines
sugeno_engine = SugenoInferenceEngine()
evaluation_engine = EvaluationEngine()
feature_extractor = FeatureExtractor()
feature_normalizer = FeatureNormalizer()
results_db = ResultsDatabase('detection_results.db')
dataset_loader = DatasetLoader('dataset')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_detection_history():
    """Memuat riwayat deteksi dari file JSON"""
    try:
        if os.path.exists(app.config['HISTORY_FILE']):
            with open(app.config['HISTORY_FILE'], 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading detection history: {e}")
    return []


def save_detection_history(detection_data):
    """Menyimpan riwayat deteksi ke file JSON"""
    try:
        history = load_detection_history()
        
        history_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'filename': detection_data.get('filename', 'unknown'),
            'classification': detection_data.get('classification', 'Unknown'),
            'status': detection_data.get('classification', 'Unknown'),
            'ai_score': detection_data.get('ai_score', 0),
            'confidence': detection_data.get('confidence', 0),
            'accuracy': round(detection_data.get('confidence', 0) * 100, 2),
            'imageUrl': detection_data.get('imageUrl', ''),
        }
        
        history.append(history_entry)
        
        # Batasi ke 500 history terbaru
        with open(app.config['HISTORY_FILE'], 'w') as f:
            json.dump(history[-500:], f, indent=2)
        
        return history_entry
    except Exception as e:
        print(f"Error saving detection history: {e}")
        return None


def process_single_image(image_path: str, filename: str, ground_truth: str = None) -> dict:
    """
    Proses gambar tunggal melalui pipeline fuzzy inference lengkap
    """
    try:
        # Load image
        color_image = Image.open(image_path).convert('RGB')
        
        # Resize jika terlalu besar
        max_size = 1024
        if color_image.width > max_size or color_image.height > max_size:
            color_image.thumbnail((max_size, max_size), Image.LANCZOS)
        
        # Extract features
        features = feature_extractor.extract_all_features(color_image)
        
        # Compute extended image analysis for indicator panels
        gray_image = np.array(color_image.convert('L'))
        image_analysis = feature_extractor.extract_image_analysis(np.array(color_image), gray_image)
        
        # Normalize features
        normalized_features = feature_normalizer.normalize(features)
        
        # Fuzzy inference
        fuzzy_result = sugeno_engine.process(normalized_features)
        
        # Classification
        classification = classify_result(fuzzy_result.ai_score)
        color = get_confidence_color(classification)
        
        # Generate heatmap
        img_array = np.array(color_image)
        composite_heatmap = HeatmapGenerator.composite_artifact_map(img_array)
        
        # Save heatmap
        heatmap_filename = f'heatmap_{uuid.uuid4().hex}.png'
        heatmap_path = os.path.join(app.config['UPLOAD_FOLDER'], heatmap_filename)
        HeatmapSaver.save_heatmap(composite_heatmap, heatmap_path)
        
        # Save overlay
        overlay_filename = f'overlay_{uuid.uuid4().hex}.png'
        overlay_path = os.path.join(app.config['UPLOAD_FOLDER'], overlay_filename)
        HeatmapSaver.save_overlay(color_image, composite_heatmap, overlay_path)
        
        # Prepare result
        result = {
            'filename': filename,
            'ai_score': round(fuzzy_result.ai_score, 4),
            'confidence': round(fuzzy_result.confidence, 4),
            'classification': classification,
            'color': color,
            'ground_truth': ground_truth,
            'features': {k: round(v, 4) if isinstance(v, float) else v 
                        for k, v in features.items()},
            'varianceIntensity': image_analysis.get('varianceIntensity'),
            'histogramAnalysis': image_analysis.get('histogramAnalysis'),
            'rgbChannels': image_analysis.get('rgbChannels'),
            'fuzzification': {
                k: {kk: round(vv, 4) if isinstance(vv, float) else vv 
                    for kk, vv in v.items()}
                for k, v in fuzzy_result.fuzzification.items()
            },
            'inference': {
                'fired_rules': len(fuzzy_result.inference['fired_rules']),
                'total_rules': fuzzy_result.inference['total_rules'],
                'max_firing_strength': round(fuzzy_result.inference['max_firing_strength'], 4),
            },
            'heatmap_url': f'/static/assets/uploads/{heatmap_filename}',
            'overlay_url': f'/static/assets/uploads/{overlay_filename}',
        }
        
        # Save ke database; if DB logging fails, preserve the detection result
        try:
            results_db.insert_detection(
                filename=filename,
                label=ground_truth or 'UNKNOWN',
                prediction=classification,
                ai_score=fuzzy_result.ai_score,
                confidence=fuzzy_result.confidence,
                features=features
            )
        except Exception as db_e:
            print(f"Warning: failed to save detection to DB: {db_e}")
        
        # Add ke evaluation engine jika ada ground truth
        if ground_truth:
            evaluation_engine.add_result(ground_truth, fuzzy_result.ai_score, classification)

        # Debug logging for diagnosis
        try:
            print(f"[DEBUG] {filename} -> ai_score={fuzzy_result.ai_score:.4f}, confidence={fuzzy_result.confidence:.4f}, class={classification}")
            # Optionally show fired rules count and max strength
            inf = fuzzy_result.inference
            print(f"[DEBUG] fired_rules={inf.get('total_fired', len(inf.get('fired_rules', [])))}, max_strength={inf.get('max_firing_strength', 0):.4f}")
        except Exception:
            pass
        
        return result
        
    except Exception as e:
        print(f"Error processing image: {e}")
        print(traceback.format_exc())
        return {
            'error': str(e),
            'filename': filename
        }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Upload dan deteksi gambar tunggal"""
    if 'image' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    try:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(upload_path)
        
        result = process_single_image(upload_path, filename)
        result['imageUrl'] = f'/static/assets/uploads/{unique_filename}'
        
        # Save to history
        save_detection_history(result)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/batch-detection', methods=['POST'])
def batch_detection():
    """Deteksi batch gambar dari dataset"""
    files = request.files.getlist('images') or request.files.getlist('batchImages')
    if not files:
        return jsonify({'error': 'No files provided'}), 400

    results = []
    ground_truths = request.form.getlist('labels')
    
    for idx, file in enumerate(files):
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            try:
                file.save(upload_path)
                ground_truth = ground_truths[idx] if idx < len(ground_truths) else None
                result = process_single_image(upload_path, filename, ground_truth)
                result['imageUrl'] = f'/static/assets/uploads/{unique_filename}'
                results.append(result)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                results.append({'error': str(e), 'filename': filename})

    return jsonify({
        'total': len(results),
        'results': results,
        'evaluation': evaluation_engine.get_full_evaluation() if len(results) > 0 else None
    })


@app.route('/dataset', methods=['POST'])
def dataset_detection_legacy():
    """Compatibility route for legacy frontend: forward to new dataset_detection."""
    return dataset_detection()


@app.route('/api/dataset-detection', methods=['POST'])
def dataset_detection():
    """Deteksi seluruh dataset dan generate evaluation lengkap"""
    try:
        # First: if client uploaded files via FormData 'datasetFiles' or 'images', use them
        uploaded_files = (request.files.getlist('datasetFiles') or request.files.getlist('images')) if request.files else []
        results = []

        evaluation_engine.reset()

        if uploaded_files and len(uploaded_files) > 0:
            ground_truths = request.form.getlist('labels')
            for idx, file in enumerate(uploaded_files):
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    try:
                        file.save(upload_path)
                        ground_truth = ground_truths[idx] if idx < len(ground_truths) else None
                        result = process_single_image(upload_path, filename, ground_truth)
                        result['imageUrl'] = f'/static/assets/uploads/{unique_filename}'
                        results.append(result)
                    except Exception as e:
                        print(f"Error processing uploaded {filename}: {e}")
                        results.append({
                            'error': str(e),
                            'filename': filename,
                            'classification': 'Error',
                            'confidence': 0.0
                        })

            valid_results = [r for r in results if r.get('classification') in ('AI Generated', 'Human Made', 'Uncertain')]
            total = len(results)
            ai_count = sum(1 for r in valid_results if r.get('classification') == 'AI Generated')
            human_count = sum(1 for r in valid_results if r.get('classification') == 'Human Made')
            uncertain_count = sum(1 for r in valid_results if r.get('classification') == 'Uncertain')

            evaluation = evaluation_engine.get_full_evaluation()
            if isinstance(evaluation, dict) and evaluation.get('total_evaluated', 0) > 0:
                avg_accuracy = evaluation.get('metrics', {}).get('accuracy', 0)
            else:
                avg_accuracy = (sum(r.get('confidence', 0) for r in valid_results) / len(valid_results)) if valid_results else 0

            frontend_results = []
            for r in results:
                frontend_results.append({
                    'filename': r.get('filename'),
                    'status': r.get('classification') or 'Error',
                    'accuracy': round(r.get('confidence', 0) * 100, 2),
                    'confidence': round(r.get('confidence', 0), 4),
                    'features': r.get('features', {}),
                    'varianceIntensity': r.get('varianceIntensity'),
                    'histogramAnalysis': r.get('histogramAnalysis'),
                    'rgbChannels': r.get('rgbChannels'),
                    'heatmap_url': r.get('heatmap_url'),
                    'overlay_url': r.get('overlay_url')
                })

            return jsonify({
                'total': total,
                'aiCount': ai_count,
                'humanCount': human_count,
                'uncertainCount': uncertain_count,
                'averageAccuracy': round(avg_accuracy * 100, 2),
                'results': frontend_results,
                'evaluation': evaluation
            })

        # Fallback: load from dataset folders on disk
        images = dataset_loader.load_all_images()

        if not images:
            return jsonify({'error': 'No images found in dataset'}), 400

        for img_data in images:
            try:
                temp_filename = f"temp_{uuid.uuid4().hex}.png"
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                img_data['image'].save(temp_path)

                result = process_single_image(
                    temp_path,
                    img_data['filename'],
                    ground_truth=img_data['label']
                )
                result['imageUrl'] = f'/static/assets/uploads/{temp_filename}'
                results.append(result)
            except Exception as e:
                print(f"Error processing {img_data['filename']}: {e}")
                results.append({
                    'error': str(e),
                    'filename': img_data['filename'],
                    'classification': 'Error',
                    'confidence': 0.0
                })

        evaluation = evaluation_engine.get_full_evaluation()

        valid_results = [r for r in results if r.get('classification') in ('AI Generated', 'Human Made', 'Uncertain')]
        total = len(results)
        ai_count = sum(1 for r in valid_results if r.get('classification') == 'AI Generated')
        human_count = sum(1 for r in valid_results if r.get('classification') == 'Human Made')
        uncertain_count = sum(1 for r in valid_results if r.get('classification') == 'Uncertain')
        if isinstance(evaluation, dict) and evaluation.get('total_evaluated', 0) > 0:
            avg_accuracy = evaluation.get('metrics', {}).get('accuracy', 0)
        else:
            avg_accuracy = (sum(r.get('confidence', 0) for r in valid_results) / len(valid_results)) if valid_results else 0

        frontend_results = []
        for r in results:
            frontend_results.append({
                'filename': r.get('filename'),
                'status': r.get('classification') or 'Error',
                'accuracy': round(r.get('confidence', 0) * 100, 2),
                'confidence': round(r.get('confidence', 0), 4),
                'features': r.get('features', {}),
                'varianceIntensity': r.get('varianceIntensity'),
                'histogramAnalysis': r.get('histogramAnalysis'),
                'rgbChannels': r.get('rgbChannels'),
                'heatmap_url': r.get('heatmap_url'),
                'overlay_url': r.get('overlay_url')
            })

        return jsonify({
            'total': total,
            'aiCount': ai_count,
            'humanCount': human_count,
            'uncertainCount': uncertain_count,
            'averageAccuracy': round(avg_accuracy * 100, 2),
            'results': frontend_results,
            'evaluation': evaluation
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/detection-history', methods=['GET'])
def get_detection_history():
    """Dapatkan riwayat deteksi"""
    history = load_detection_history()
    stats = {
        'total': len(history),
        'aiCount': sum(1 for entry in history if entry.get('classification') == 'AI Generated'),
        'humanCount': sum(1 for entry in history if entry.get('classification') == 'Human Made'),
        'uncertainCount': sum(1 for entry in history if entry.get('classification') == 'Uncertain'),
        'averageAccuracy': round(sum(entry.get('confidence', 0) for entry in history) / len(history) * 100, 2) if history else 0
    }
    return jsonify({
        'history': history,
        'total': len(history),
        'statistics': stats
    })


@app.route('/api/detection-history/clear', methods=['POST'])
def clear_detection_history():
    """Clear riwayat deteksi"""
    try:
        if os.path.exists(app.config['HISTORY_FILE']):
            os.remove(app.config['HISTORY_FILE'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/evaluation', methods=['GET'])
def get_evaluation():
    """Dapatkan hasil evaluasi terkini"""
    evaluation = evaluation_engine.get_full_evaluation()
    return jsonify(evaluation)


@app.route('/api/evaluation/reset', methods=['POST'])
def reset_evaluation():
    """Reset evaluation engine"""
    evaluation_engine.reset()
    return jsonify({'success': True})


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Dapatkan statistik dari database"""
    stats = results_db.get_statistics()
    return jsonify(stats)


@app.route('/api/results-export', methods=['GET'])
def export_results():
    """Export hasil deteksi ke CSV"""
    try:
        output_file = 'detection_results_export.csv'
        results_db.export_to_csv(output_file)
        return jsonify({
            'success': True,
            'file': output_file,
            'message': 'Results exported to CSV'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/system-info', methods=['GET'])
def system_info():
    """Dapatkan informasi sistem"""
    return jsonify({
        'fuzzy_engine': {
            'engine_type': 'Sugeno',
            'total_rules': 55,
            'thresholds': {
                'ai': 0.65,
                'uncertain_high': 0.64,
                'uncertain_low': 0.45,
                'human': 0.45
            }
        },
        'feature_extractor': {
            'features': feature_extractor.feature_names,
            'total_features': len(feature_extractor.feature_names)
        },
        'database': {
            'path': 'detection_results.db',
            'status': 'active'
        },
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'max_file_size_mb': app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
    })


# OpenAI integration endpoints (jika tersedia)
if get_openai_status and get_ai_insight:
    @app.route('/api/openai-status', methods=['GET'])
    def openai_status():
        """Status OpenAI integration"""
        return jsonify(get_openai_status())
    
    @app.route('/api/analyze-with-ai', methods=['POST'])
    def analyze_with_ai():
        """Dapatkan AI insight dari OpenAI"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            insight = get_ai_insight(data)
            return jsonify({
                'success': True,
                'insight': insight,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
else:
    @app.route('/api/openai-status', methods=['GET'])
    def openai_status_unavailable():
        return jsonify({'available': False, 'message': 'OpenAI integration unavailable'})

    @app.route('/api/analyze-with-ai', methods=['POST'])
    def analyze_with_ai_unavailable():
        return jsonify({'error': 'OpenAI integration unavailable'}), 503


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Try to fit normalizer with some initial data
    try:
        dataset_images = dataset_loader.load_all_images()
        if dataset_images:
            initial_features = []
            for img_data in dataset_images[:min(20, len(dataset_images))]:
                features = feature_extractor.extract_all_features(img_data['image'])
                initial_features.append(features)
            
            if initial_features:
                feature_normalizer.fit(initial_features)
                print(f"Feature normalizer fitted with {len(initial_features)} samples")
    except Exception as e:
        print(f"Warning: Could not fit feature normalizer: {e}")
    
    print("Starting AI Detection System...")
    app.run(debug=True, host='127.0.0.1', port=5000)
