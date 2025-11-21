"""
Prediction Module for Brain Tumor MRI Classification

Handles model inference and prediction on single images.
"""

import logging
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
from PIL import Image

import tensorflow as tf

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Class labels
CLASS_LABELS = {
    0: 'Cassava Brown Streak Disease (CBSD)',
    1: 'Cassava Green Mottle (CGM)',
    2: 'Cassava Mosaic Disease (CMD)',
    3: 'Healthy',
    4: 'Unknown'
}

SHORT_LABELS = {
    0: 'CBSD',
    1: 'CGM',
    2: 'CMD',
    3: 'Healthy',
    4: 'Unknown'
}

# Configuration
IMAGE_SIZE = (224, 224)
CONFIDENCE_THRESHOLD = 0.5


class CassavaPredictor:
    """Predictor class for Cassava Leaf Disease classification."""
    
    def __init__(self, model_path: str):
        """
        Initialize predictor with trained model.
        
        Args:
            model_path: Path to saved model file
        """
        self.model_path = model_path
        self.model = None
        self.load_model()
    
    def load_model(self) -> None:
        """Load trained model from disk."""
        try:
            self.model = tf.keras.models.load_model(self.model_path)
            logger.info(f"✓ Model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"✗ Failed to load model: {e}")
            raise
    
    def preprocess_image(
        self,
        image_input,
        target_size: Tuple[int, int] = IMAGE_SIZE
    ) -> np.ndarray:
        """
        Preprocess image for prediction.
        
        Args:
            image_input: Image file path or PIL Image or numpy array
            target_size: Target image size
            
        Returns:
            Preprocessed image array
        """
        # Handle different input types
        if isinstance(image_input, str):
            # File path
            try:
                img = Image.open(image_input).convert('RGB')
            except Exception as e:
                logger.error(f"Failed to load image from path: {e}")
                raise
        elif isinstance(image_input, Image.Image):
            # PIL Image
            img = image_input.convert('RGB')
        elif isinstance(image_input, np.ndarray):
            # Numpy array
            if image_input.dtype != np.uint8:
                # Assume normalized (0-1)
                img = Image.fromarray((image_input * 255).astype(np.uint8))
            else:
                img = Image.fromarray(image_input)
            img = img.convert('RGB')
        else:
            raise TypeError(f"Unsupported image input type: {type(image_input)}")
        
        # Resize
        img = img.resize(target_size, Image.LANCZOS)
        
        # Convert to array and normalize
        img_array = np.array(img, dtype=np.float32) / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def predict_single(
        self,
        image_input
    ) -> Dict:
        """
        Predict class for a single image.
        
        Args:
            image_input: Image file path or PIL Image or numpy array
            
        Returns:
            Dictionary with predictions and confidence
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Preprocess image
        img_array = self.preprocess_image(image_input)
        
        # Make prediction
        predictions = self.model.predict(img_array, verbose=0)
        probabilities = predictions[0]
        predicted_class = np.argmax(probabilities)
        confidence = float(probabilities[predicted_class])
        
        # Format results
        result = {
            'predicted_class': CLASS_LABELS[predicted_class],
            'predicted_class_short': SHORT_LABELS[predicted_class],
            'class_index': int(predicted_class),
            'confidence': confidence,
            'probabilities': {
                SHORT_LABELS[i]: float(prob)
                for i, prob in enumerate(probabilities)
            }
        }
        
        return result
    
    def predict_batch(
        self,
        image_paths: list
    ) -> list:
        """
        Predict classes for multiple images.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of prediction results
        """
        results = []
        
        for img_path in image_paths:
            try:
                result = self.predict_single(img_path)
                result['image_path'] = str(img_path)
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to predict for {img_path}: {e}")
                results.append({
                    'image_path': str(img_path),
                    'error': str(e)
                })
        
        return results


def get_predictor(model_path: str) -> CassavaPredictor:
    """
    Get or create predictor instance.
    
    Args:
        model_path: Path to model file
        
    Returns:
        CassavaPredictor instance
    """
    return CassavaPredictor(model_path)
