"""
SAR Image Preprocessing Service.
Handles SAR image preprocessing for GLOF detection.
"""
import os
import numpy as np
import cv2
from pathlib import Path
from typing import Union, Tuple
from skimage.restoration import denoise_bilateral
from sklearn.preprocessing import StandardScaler


class SARPreprocessor:
    """Preprocesses SAR images for CNN model input."""
    
    def __init__(self, target_size: Tuple[int, int] = (128, 128)):
        """
        Initialize preprocessor.
        
        Args:
            target_size: Target image dimensions (height, width)
        """
        self.target_size = target_size
    
    def read_image(self, image_path: Union[str, Path]) -> np.ndarray:
        """
        Read SAR image from file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Grayscale image as numpy array
        """
        image_path = str(image_path)
        
        # Try to read as grayscale first
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        return image
    
    def speckle_filter(self, image: np.ndarray) -> np.ndarray:
        """
        Apply speckle noise reduction using bilateral filter.
        
        Args:
            image: Input grayscale image
            
        Returns:
            Filtered image
        """
        # Convert to float for bilateral filter
        image_float = image.astype(np.float64) / 255.0
        filtered = denoise_bilateral(image_float, sigma_color=0.05, sigma_spatial=15)
        return filtered
    
    def convert_to_sigma0(self, image: np.ndarray) -> np.ndarray:
        """
        Convert digital numbers to sigma0 (radar backscatter coefficient).
        
        Args:
            image: Input image in DN values
            
        Returns:
            Image in dB scale
        """
        # Replace zeros/negatives with small positive value to avoid log errors
        image = np.where(image > 0, image, 1e-10)
        sigma0 = 10 * np.log10(image)
        return sigma0
    
    def clean_image(self, image: np.ndarray) -> np.ndarray:
        """
        Clean image by replacing infinities and NaNs with mean value.
        
        Args:
            image: Input image
            
        Returns:
            Cleaned image
        """
        finite_mask = np.isfinite(image)
        if np.any(finite_mask):
            mean_value = np.mean(image[finite_mask])
            image = np.where(finite_mask, image, mean_value)
        return image
    
    def normalize(self, image: np.ndarray) -> np.ndarray:
        """
        Normalize image to 0-1 range.
        
        Args:
            image: Input image
            
        Returns:
            Normalized image
        """
        min_val = np.min(image)
        max_val = np.max(image)
        
        if max_val - min_val > 0:
            normalized = (image - min_val) / (max_val - min_val)
        else:
            normalized = np.zeros_like(image)
        
        return normalized
    
    def resize(self, image: np.ndarray) -> np.ndarray:
        """
        Resize image to target size.
        
        Args:
            image: Input image
            
        Returns:
            Resized image
        """
        resized = cv2.resize(image, self.target_size, interpolation=cv2.INTER_LINEAR)
        return resized
    
    def preprocess(self, image_path: Union[str, Path]) -> np.ndarray:
        """
        Full preprocessing pipeline for SAR image.
        
        Args:
            image_path: Path to SAR image
            
        Returns:
            Preprocessed image ready for model input (shape: 1, H, W, 3)
        """
        # Read image
        image = self.read_image(image_path)
        
        # Apply speckle filter
        filtered = self.speckle_filter(image)
        
        # Convert to sigma0
        sigma0 = self.convert_to_sigma0(filtered)
        
        # Clean infinities/NaNs
        cleaned = self.clean_image(sigma0)
        
        # Normalize to 0-1
        normalized = self.normalize(cleaned)
        
        # Resize to target size
        resized = self.resize(normalized)
        
        # Convert to RGB (duplicate grayscale to 3 channels for CNN)
        rgb_image = np.stack([resized, resized, resized], axis=-1)
        
        # Add batch dimension
        batch_image = np.expand_dims(rgb_image, axis=0)
        
        return batch_image.astype(np.float32)
    
    def preprocess_from_bytes(self, image_bytes: bytes) -> np.ndarray:
        """
        Preprocess image from bytes (for file upload).
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Preprocessed image ready for model input
        """
        # Decode image from bytes
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if image is None:
            raise ValueError("Could not decode image from bytes")
        
        # Apply preprocessing (skip read step)
        filtered = self.speckle_filter(image)
        sigma0 = self.convert_to_sigma0(filtered)
        cleaned = self.clean_image(sigma0)
        normalized = self.normalize(cleaned)
        resized = self.resize(normalized)
        
        # Convert to RGB and add batch dimension
        rgb_image = np.stack([resized, resized, resized], axis=-1)
        batch_image = np.expand_dims(rgb_image, axis=0)
        
        return batch_image.astype(np.float32)
