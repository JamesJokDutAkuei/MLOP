"""
Retraining Module for Cassava Leaf Disease Classifier

Handles model retraining on newly uploaded data with:
- Data loading and preprocessing
- Model fine-tuning
- Model versioning and checkpointing
- Performance monitoring
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple
import shutil

import numpy as np
import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from PIL import Image

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/retraining.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / 'models'
DATA_DIR = PROJECT_ROOT / 'data'
UPLOADS_DIR = DATA_DIR / 'uploads'
TRAIN_DIR = DATA_DIR / 'train'

# Configuration
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
LEARNING_RATE = 1e-5
IMAGENET_MEAN = np.array([0.485, 0.456, 0.406])
IMAGENET_STD = np.array([0.229, 0.224, 0.225])


class CassavaRetrainer:
    """Handles model retraining on new data."""
    
    def __init__(self, model_path: str, version: int = 1):
        """
        Initialize retrainer.
        
        Args:
            model_path: Path to base model
            version: Version number for new model
        """
        self.model_path = model_path
        self.version = version
        self.model = None
        self.history = None
        
        self.load_model()
    
    def load_model(self):
        """Load base model."""
        try:
            self.model = tf.keras.models.load_model(self.model_path)
            logger.info(f"✓ Model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"✗ Failed to load model: {e}")
            raise
    
    def load_images_from_directory(self, directory: Path) -> Tuple[np.ndarray, np.ndarray]:
        """Load images from directory."""
        images = []
        labels = []
        
        class_label_map = {
            'CBSD': 0, 'CGM': 1, 'CMD': 2, 'Healthy': 3, 'Unknown': 4
        }
        
        for class_name, class_idx in class_label_map.items():
            class_dir = directory / class_name
            if not class_dir.exists():
                continue
            
            for img_file in list(class_dir.glob('*.jpg')) + list(class_dir.glob('*.png')):
                try:
                    img = Image.open(img_file).convert('RGB')
                    img = img.resize(IMAGE_SIZE, Image.LANCZOS)
                    img_array = np.array(img, dtype=np.float32) / 255.0
                    
                    # Apply ImageNet normalization
                    for i in range(3):
                        img_array[:, :, i] = (img_array[:, :, i] - IMAGENET_MEAN[i]) / IMAGENET_STD[i]
                    
                    images.append(img_array)
                    labels.append(class_idx)
                except Exception as e:
                    logger.warning(f"Failed to load {img_file}: {e}")
                    continue
        
        return np.array(images), np.array(labels)
    
    def retrain(
        self,
        epochs: int = 10,
        batch_size: int = BATCH_SIZE,
        learning_rate: float = LEARNING_RATE,
        validation_split: float = 0.2
    ) -> Dict:
        """
        Retrain model on uploaded data.
        
        Args:
            epochs: Training epochs
            batch_size: Batch size
            learning_rate: Learning rate
            validation_split: Validation split ratio
            
        Returns:
            Dictionary with training results
        """
        logger.info("Starting model retraining...")
        
        # Load new training data
        logger.info("Loading uploaded training data...")
        X_train, y_train = self.load_images_from_directory(UPLOADS_DIR)
        
        if len(X_train) == 0:
            logger.warning("No new training data found")
            return {'status': 'failed', 'error': 'No training data found'}
        
        logger.info(f"Loaded {len(X_train)} new training samples")
        
        # One-hot encode labels
        NUM_CLASSES = 5
        y_train_encoded = tf.keras.utils.to_categorical(y_train, num_classes=NUM_CLASSES)
        
        # Update learning rate
        self.model.optimizer.learning_rate = learning_rate
        
        # Define callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=3,
                restore_best_weights=True,
                verbose=1
            ),
            ModelCheckpoint(
                filepath=str(MODELS_DIR / f'cassava_model_checkpoint_v{self.version}.h5'),
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            )
        ]
        
        # Train
        try:
            self.history = self.model.fit(
                X_train, y_train_encoded,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=validation_split,
                callbacks=callbacks,
                verbose=1
            )
            
            logger.info("✓ Retraining complete")
            
            return {
                'status': 'success',
                'epochs_trained': len(self.history.history['loss']),
                'final_loss': float(self.history.history['loss'][-1]),
                'final_accuracy': float(self.history.history['accuracy'][-1]),
                'val_loss': float(self.history.history['val_loss'][-1]),
                'val_accuracy': float(self.history.history['val_accuracy'][-1])
            }
        
        except Exception as e:
            logger.error(f"✗ Retraining failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def save_model(self, version: int = None) -> str:
        """
        Save retrained model with version.
        
        Args:
            version: Version number (auto-increment if None)
            
        Returns:
            Path to saved model
        """
        if version is None:
            version = self.version
        
        model_path = MODELS_DIR / f'cassava_model_v{version}.h5'
        
        try:
            self.model.save(str(model_path))
            logger.info(f"✓ Model saved to {model_path}")
            return str(model_path)
        except Exception as e:
            logger.error(f"✗ Failed to save model: {e}")
            raise
    
    def save_metadata(self, metrics: Dict, version: int = None):
        """Save model metadata and metrics."""
        if version is None:
            version = self.version
        
        metadata = {
            'model_version': f'v{version}',
            'retrained_at': datetime.now().isoformat(),
            'metrics': metrics,
            'training_config': {
                'learning_rate': LEARNING_RATE,
                'batch_size': BATCH_SIZE,
                'image_size': IMAGE_SIZE
            }
        }
        
        metadata_path = MODELS_DIR / f'model_metadata_v{version}.json'
        
        try:
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"✓ Metadata saved to {metadata_path}")
        except Exception as e:
            logger.error(f"✗ Failed to save metadata: {e}")
    
    def evaluate_model(self, test_data: Tuple = None) -> Dict:
        """Evaluate retrained model."""
        if test_data is None:
            # Load test data
            X_test, y_test = self.load_images_from_directory(TRAIN_DIR)
            
            if len(X_test) == 0:
                logger.warning("No test data available")
                return {}
            
            y_test_encoded = tf.keras.utils.to_categorical(y_test, num_classes=5)
        else:
            X_test, y_test_encoded = test_data
        
        try:
            loss, accuracy, precision, recall = self.model.evaluate(
                X_test, y_test_encoded, verbose=0
            )
            
            return {
                'test_loss': float(loss),
                'test_accuracy': float(accuracy),
                'test_precision': float(precision),
                'test_recall': float(recall)
            }
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {}


def archive_uploaded_data():
    """Archive uploaded data after retraining."""
    archive_dir = DATA_DIR / 'uploads_archive' / datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        for class_dir in UPLOADS_DIR.iterdir():
            if class_dir.is_dir():
                shutil.move(str(class_dir), str(archive_dir / class_dir.name))
        logger.info(f"✓ Uploaded data archived to {archive_dir}")
    except Exception as e:
        logger.error(f"Failed to archive data: {e}")


def main():
    """Main retraining workflow."""
    try:
        # Initialize retrainer
        base_model_path = MODELS_DIR / 'cassava_model_v1.h5'
        retrainer = CassavaRetrainer(str(base_model_path), version=2)
        
        # Retrain model
        retrain_results = retrainer.retrain(
            epochs=10,
            batch_size=32,
            learning_rate=1e-5
        )
        
        if retrain_results['status'] == 'success':
            # Evaluate
            eval_results = retrainer.evaluate_model()
            
            # Save new model
            new_model_path = retrainer.save_model(version=2)
            
            # Save metadata
            all_metrics = {**retrain_results, **eval_results}
            retrainer.save_metadata(all_metrics, version=2)
            
            # Archive uploaded data
            archive_uploaded_data()
            
            logger.info("✓ Retraining workflow complete!")
            logger.info(f"New model saved to {new_model_path}")
            logger.info(f"Metrics: {all_metrics}")
        else:
            logger.error(f"Retraining failed: {retrain_results}")
    
    except Exception as e:
        logger.error(f"Retraining workflow failed: {e}", exc_info=True)


if __name__ == '__main__':
    main()
