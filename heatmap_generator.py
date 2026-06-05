"""
AI Artifact Heatmap Generator
Visualisasi area gambar yang dianggap AI menggunakan berbagai teknik
"""

import numpy as np
import cv2
from PIL import Image
from typing import Tuple
import os


class HeatmapGenerator:
    """Generator untuk berbagai jenis heatmap"""
    
    @staticmethod
    def laplacian_activation_map(image: np.ndarray, sigma: float = 1.5) -> np.ndarray:
        """
        Generate heatmap berdasarkan Laplacian activation
        Menonjolkan area dengan perubahan intensitas tinggi (potential AI artifacts)
        """
        # Convert ke grayscale jika perlu
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Gaussian blur untuk smoothing
        blurred = cv2.GaussianBlur(gray, (5, 5), sigma)
        
        # Compute Laplacian
        laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
        
        # Take absolute value dan normalize
        laplacian_abs = np.abs(laplacian)
        heatmap = cv2.normalize(laplacian_abs, None, 0, 255, cv2.NORM_MINMAX)
        
        return heatmap.astype(np.uint8)
    
    @staticmethod
    def edge_anomaly_map(image: np.ndarray, ksize: int = 5) -> np.ndarray:
        """
        Generate heatmap berdasarkan edge anomaly detection
        Deteksi area dengan edge pattern yang tidak wajar (characteristic AI artifacts)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Canny edge detection
        edges = cv2.Canny(gray, 100, 200)
        
        # Morphological operations untuk highlight anomalies
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Gaussian blur untuk smooth transition
        heatmap = cv2.GaussianBlur(dilated.astype(np.float32), (11, 11), 2.0)
        heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
        
        return heatmap.astype(np.uint8)
    
    @staticmethod
    def texture_response_map(image: np.ndarray) -> np.ndarray:
        """
        Generate heatmap berdasarkan texture analysis
        Highlight area dengan texture pattern yang berbeda dari natural
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Local Binary Pattern (LBP)-like texture analysis
        # Compute texture using Gabor filters
        kernels = []
        for theta in [0, np.pi/4, np.pi/2, 3*np.pi/4]:
            kernel = cv2.getGaborKernel((21, 21), 5.0, theta, 10.0, 0.5, 0)
            kernel = kernel / kernel.sum()
            kernels.append(kernel)
        
        # Apply Gabor filters
        responses = []
        for kernel in kernels:
            response = cv2.filter2D(gray.astype(np.float32), cv2.CV_32F, kernel)
            responses.append(np.abs(response))
        
        # Combine responses
        texture_map = np.mean(responses, axis=0)
        heatmap = cv2.normalize(texture_map, None, 0, 255, cv2.NORM_MINMAX)
        
        return heatmap.astype(np.uint8)
    
    @staticmethod
    def frequency_anomaly_map(image: np.ndarray) -> np.ndarray:
        """
        Generate heatmap berdasarkan frequency domain analysis
        Highlight area dengan anomali di frequency domain
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        h, w = gray.shape
        
        # Compute FFT
        f = np.fft.fft2(gray.astype(np.float32))
        fshift = np.fft.fftshift(f)
        magnitude = np.abs(fshift)
        
        # Compute phase
        phase = np.angle(fshift)
        
        # Spatial domain anomaly from magnitude
        magnitude_normalized = np.log(magnitude + 1)
        
        # Inverse FFT of magnitude to get spatial anomaly map
        f_inv = np.fft.ifftshift(magnitude_normalized * np.exp(1j * phase))
        spatial_anomaly = np.abs(np.fft.ifft2(f_inv))
        
        # Normalize
        heatmap = cv2.normalize(spatial_anomaly, None, 0, 255, cv2.NORM_MINMAX)
        
        return heatmap.astype(np.uint8)
    
    @staticmethod
    def composite_artifact_map(image: np.ndarray, weights: dict = None) -> np.ndarray:
        """
        Generate composite heatmap menggabungkan multiple detection methods
        Setiap method memberikan kontribusi pada deteksi akhir
        """
        if weights is None:
            weights = {
                "laplacian": 0.35,
                "edge": 0.30,
                "texture": 0.20,
                "frequency": 0.15,
            }
        
        maps = {}
        
        # Generate individual maps
        maps["laplacian"] = HeatmapGenerator.laplacian_activation_map(image)
        maps["edge"] = HeatmapGenerator.edge_anomaly_map(image)
        maps["texture"] = HeatmapGenerator.texture_response_map(image)
        maps["frequency"] = HeatmapGenerator.frequency_anomaly_map(image)
        
        # Weighted combination
        composite = np.zeros_like(maps["laplacian"], dtype=np.float32)
        for key, weight in weights.items():
            if key in maps:
                composite += maps[key].astype(np.float32) * weight
        
        # Normalize
        heatmap = cv2.normalize(composite, None, 0, 255, cv2.NORM_MINMAX)
        
        return heatmap.astype(np.uint8)
    
    @staticmethod
    def apply_colormap(heatmap: np.ndarray, colormap_type: str = "jet") -> np.ndarray:
        """
        Terapkan colormap ke heatmap
        colormap_type: "jet", "plasma", "hot", "cool", "viridis"
        """
        colormap_map = {
            "jet": cv2.COLORMAP_JET,
            "plasma": cv2.COLORMAP_PLASMA,
            "hot": cv2.COLORMAP_HOT,
            "cool": cv2.COLORMAP_COOL,
            "viridis": cv2.COLORMAP_VIRIDIS,
            "magma": cv2.COLORMAP_MAGMA,
        }
        
        cm = colormap_map.get(colormap_type, cv2.COLORMAP_JET)
        colored = cv2.applyColorMap(heatmap, cm)
        
        # Convert BGR to RGB
        return cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)
    
    @staticmethod
    def overlay_heatmap(original_image: np.ndarray, heatmap: np.ndarray, 
                       alpha: float = 0.5) -> np.ndarray:
        """
        Overlay heatmap di atas original image
        """
        if len(original_image.shape) == 2:
            original_bgr = cv2.cvtColor(original_image, cv2.COLOR_GRAY2RGB)
        elif original_image.shape[2] == 3:
            # Ensure RGB format
            if isinstance(original_image, Image.Image):
                original_bgr = cv2.cvtColor(np.array(original_image), cv2.COLOR_RGB2BGR)
            else:
                original_bgr = cv2.cvtColor(original_image, cv2.COLOR_RGB2BGR)
        else:
            original_bgr = original_image
        
        # Resize heatmap jika berbeda ukuran
        if heatmap.shape != original_bgr.shape[:2]:
            heatmap = cv2.resize(heatmap, (original_bgr.shape[1], original_bgr.shape[0]))
        
        # Apply colormap
        heatmap_colored = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        
        # Overlay
        blended = cv2.addWeighted(original_bgr, 1 - alpha, heatmap_colored, alpha, 0)
        
        # Convert back to RGB
        return cv2.cvtColor(blended, cv2.COLOR_BGR2RGB)


class GradCAMDetector:
    """Simple Grad-CAM style visualization untuk mendeteksi AI artifacts"""
    
    @staticmethod
    def compute_grad_cam(image: np.ndarray) -> np.ndarray:
        """
        Compute gradient-based activation map
        Simplified version yang tidak perlu neural network
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        gray_float = gray.astype(np.float32)
        
        # Compute gradients
        gx = cv2.Sobel(gray_float, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray_float, cv2.CV_32F, 0, 1, ksize=3)
        
        # Magnitude of gradients
        magnitude = np.sqrt(gx**2 + gy**2)
        
        # Weighted by gradient direction consistency
        angle = np.arctan2(gy, gx)
        
        # Compute local variation of angle (consistency)
        angle_var = cv2.GaussianBlur((angle * 180 / np.pi).astype(np.float32), (5, 5), 0)
        
        # Combine magnitude and angle consistency
        grad_cam = magnitude * (1 - np.abs(angle_var) / 180.0)
        
        # Normalize
        grad_cam = cv2.normalize(grad_cam, None, 0, 255, cv2.NORM_MINMAX)
        
        return grad_cam.astype(np.uint8)


class HeatmapSaver:
    """Simpan heatmap ke file"""
    
    @staticmethod
    def save_heatmap(heatmap: np.ndarray, output_path: str, colormap_type: str = "jet"):
        """Simpan heatmap dengan colormap"""
        colored = HeatmapGenerator.apply_colormap(heatmap, colormap_type)
        img = Image.fromarray(colored)
        img.save(output_path)
    
    @staticmethod
    def save_overlay(original_image: Image.Image, heatmap: np.ndarray, 
                    output_path: str, alpha: float = 0.5):
        """Simpan overlay heatmap"""
        original_np = np.array(original_image)
        overlayed = HeatmapGenerator.overlay_heatmap(original_np, heatmap, alpha)
        img = Image.fromarray(overlayed)
        img.save(output_path)
    
    @staticmethod
    def save_comparison(original_image: Image.Image, heatmap: np.ndarray,
                       output_path: str, title: str = "AI Detection Heatmap"):
        """Simpan perbandingan original vs heatmap"""
        original_np = np.array(original_image)
        
        # Resize heatmap jika perlu
        if heatmap.shape != original_np.shape[:2]:
            heatmap = cv2.resize(heatmap, (original_np.shape[1], original_np.shape[0]))
        
        # Apply colormap to heatmap
        heatmap_colored = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
        
        # Create side-by-side comparison
        h, w = original_np.shape[:2]
        comparison = np.zeros((h, w * 2, 3), dtype=np.uint8)
        comparison[:, :w] = original_np
        comparison[:, w:] = heatmap_colored
        
        img = Image.fromarray(comparison)
        img.save(output_path)


def generate_complete_heatmap_analysis(image_path: str, output_dir: str) -> dict:
    """
    Generate lengkap heatmap analysis dengan semua metode
    """
    # Load image
    img = Image.open(image_path).convert('RGB')
    img_array = np.array(img)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate all heatmaps
    laplacian_hm = HeatmapGenerator.laplacian_activation_map(img_array)
    edge_hm = HeatmapGenerator.edge_anomaly_map(img_array)
    texture_hm = HeatmapGenerator.texture_response_map(img_array)
    frequency_hm = HeatmapGenerator.frequency_anomaly_map(img_array)
    composite_hm = HeatmapGenerator.composite_artifact_map(img_array)
    gradcam_hm = GradCAMDetector.compute_grad_cam(img_array)
    
    # Save individual heatmaps
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    HeatmapSaver.save_heatmap(laplacian_hm, os.path.join(output_dir, f"{base_name}_laplacian.png"))
    HeatmapSaver.save_heatmap(edge_hm, os.path.join(output_dir, f"{base_name}_edge.png"))
    HeatmapSaver.save_heatmap(texture_hm, os.path.join(output_dir, f"{base_name}_texture.png"))
    HeatmapSaver.save_heatmap(frequency_hm, os.path.join(output_dir, f"{base_name}_frequency.png"))
    HeatmapSaver.save_heatmap(composite_hm, os.path.join(output_dir, f"{base_name}_composite.png"))
    HeatmapSaver.save_heatmap(gradcam_hm, os.path.join(output_dir, f"{base_name}_gradcam.png"))
    
    # Save overlays
    HeatmapSaver.save_overlay(img, composite_hm, os.path.join(output_dir, f"{base_name}_overlay.png"))
    
    return {
        "laplacian": f"{base_name}_laplacian.png",
        "edge": f"{base_name}_edge.png",
        "texture": f"{base_name}_texture.png",
        "frequency": f"{base_name}_frequency.png",
        "composite": f"{base_name}_composite.png",
        "gradcam": f"{base_name}_gradcam.png",
        "overlay": f"{base_name}_overlay.png",
    }
