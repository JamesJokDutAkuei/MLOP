"""
Model Creation and Training Module for Brain Tumor MRI Classification

Uses transfer learning with MobileNetV2 architecture.
"""

import logging
from pathlib import Path
from typing import Tuple, Dict
import json

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import (
    EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
INPUT_SHAPE = (224, 224, 3)
NUM_CLASSES = 5
LEARNING_RATE = 1e-4
BATCH_SIZE = 32
EPOCHS = 50

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / 'models'
LOGS_DIR = PROJECT_ROOT / 'logs'


def create_transfer_learning_model(
    num_classes: int = NUM_CLASSES,
    input_shape: Tuple[int, int, int] = INPUT_SHAPE,
    freeze_base: bool = True,
    num_freeze_layers: int = 130
) -> models.Model:
    """
    Create transfer learning model using MobileNetV2.
    
    Args:
        num_classes: Number of output classes
        input_shape: Input image shape (height, width, channels)
        freeze_base: Whether to freeze base model layers
        num_freeze_layers: Number of layers to freeze from base model
        
    Returns:
        Compiled Keras model
    """
    logger.info("Creating transfer learning model with MobileNetV2...")
    
    # Load pre-trained MobileNetV2
    base_model = MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    
    logger.info(f"Base model layers: {len(base_model.layers)}")
    
    # Freeze layers
    if freeze_base:
        for layer in base_model.layers[:num_freeze_layers]:
            layer.trainable = False
        logger.info(f"Froze first {num_freeze_layers} layers")
    
    # Add custom top layers
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation='relu', name='dense_1'),
        layers.Dropout(0.3),
        layers.Dense(128, activation='relu', name='dense_2'),
        layers.Dropout(0.2),
        layers.Dense(num_classes, activation='softmax', name='output')
    ])
    
    logger.info("Model architecture created")
    
    # Compile model
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )
    
    logger.info("Model compiled")
    
    return model


def create_custom_model(
    num_classes: int = NUM_CLASSES,
    input_shape: Tuple[int, int, int] = INPUT_SHAPE
) -> models.Model:
    """
    Create a custom CNN model from scratch (alternative to transfer learning).
    
    Args:
        num_classes: Number of output classes
        input_shape: Input image shape
        
    Returns:
        Compiled Keras model
    """
    logger.info("Creating custom CNN model...")
    
    model = models.Sequential([
        # Block 1
        layers.Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Block 2
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Block 3
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Flatten and Dense
        layers.Flatten(),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )
    
    logger.info("Custom model created and compiled")
    
    return model


def get_training_callbacks(model_name: str = 'model') -> list:
    """
    Create training callbacks for model checkpointing and monitoring.
    
    Args:
        model_name: Name for checkpoint files
        
    Returns:
        List of callbacks
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        ModelCheckpoint(
            filepath=str(MODELS_DIR / f'{model_name}_best.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1
        ),
        TensorBoard(
            log_dir=str(LOGS_DIR / 'tensorboard'),
            histogram_freq=1,
            write_graph=True
        )
    ]
    
    return callbacks


def train_model(
    model: models.Model,
    train_data: Tuple[np.ndarray, np.ndarray],
    val_data: Tuple[np.ndarray, np.ndarray],
    epochs: int = EPOCHS,
    batch_size: int = BATCH_SIZE,
    class_weights: dict = None,
    model_name: str = 'cassava_model'
) -> Tuple[models.Model, dict]:
    """
    Train the model on training data with validation.
    
    Args:
        model: Keras model to train
        train_data: Tuple of (X_train, y_train)
        val_data: Tuple of (X_val, y_val)
        epochs: Number of training epochs
        batch_size: Batch size
        class_weights: Dictionary of class weights for imbalanced data
        model_name: Name for saving checkpoints
        
    Returns:
        Tuple of (trained_model, history_dict)
    """
    logger.info("Starting model training...")
    logger.info(f"Training samples: {len(train_data[0])}")
    logger.info(f"Validation samples: {len(val_data[0])}")
    
    X_train, y_train = train_data
    X_val, y_val = val_data
    
    callbacks = get_training_callbacks(model_name)
    
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1
    )
    
    logger.info("✓ Training complete!")
    
    # Convert history to dictionary
    history_dict = history.history
    
    return model, history_dict


def evaluate_model(
    model: models.Model,
    test_data: Tuple[np.ndarray, np.ndarray]
) -> dict:
    """
    Evaluate model on test data.
    
    Args:
        model: Trained model
        test_data: Tuple of (X_test, y_test)
        
    Returns:
        Dictionary with evaluation metrics
    """
    logger.info("Evaluating model on test data...")
    
    X_test, y_test = test_data
    
    loss, accuracy, precision, recall = model.evaluate(X_test, y_test, verbose=0)
    
    # Get predictions
    y_pred_proba = model.predict(X_test, verbose=0)
    y_pred = np.argmax(y_pred_proba, axis=1)
    y_true = np.argmax(y_test, axis=1)
    
    # Compute metrics
    from sklearn.metrics import (
        f1_score, precision_score, recall_score,
        confusion_matrix, classification_report, roc_auc_score
    )
    
    f1 = f1_score(y_true, y_pred, average='weighted')
    precision_weighted = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    recall_weighted = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    
    # ROC-AUC (one-vs-rest)
    try:
        roc_auc = roc_auc_score(y_test, y_pred_proba, average='weighted', multi_class='ovr')
    except:
        roc_auc = 0.0
    
    conf_matrix = confusion_matrix(y_true, y_pred)
    class_report = classification_report(y_true, y_pred, output_dict=True)
    
    metrics = {
        'loss': float(loss),
        'accuracy': float(accuracy),
        'precision': float(precision_weighted),
        'recall': float(recall_weighted),
        'f1_score': float(f1),
        'roc_auc': float(roc_auc),
        'confusion_matrix': conf_matrix.tolist(),
        'classification_report': class_report
    }
    
    logger.info("=" * 60)
    logger.info("TEST SET METRICS")
    logger.info("=" * 60)
    logger.info(f"Loss:      {loss:.4f}")
    logger.info(f"Accuracy:  {accuracy:.4f}")
    logger.info(f"Precision: {precision_weighted:.4f}")
    logger.info(f"Recall:    {recall_weighted:.4f}")
    logger.info(f"F1 Score:  {f1:.4f}")
    logger.info(f"ROC-AUC:   {roc_auc:.4f}")
    logger.info("=" * 60)
    
    return metrics


def save_model(
    model: models.Model,
    model_path: str,
    format: str = 'h5'
) -> None:
    """
    Save trained model to disk.
    
    Args:
        model: Trained model
        model_path: Path to save model
        format: Format ('h5' or 'savedmodel')
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    if format == 'h5':
        model.save(model_path)
        logger.info(f"Model saved to {model_path}")
    elif format == 'savedmodel':
        model.save(model_path, save_format='tf')
        logger.info(f"Model saved to {model_path} (SavedModel format)")


def load_model(model_path: str) -> models.Model:
    """
    Load trained model from disk.
    
    Args:
        model_path: Path to model file
        
    Returns:
        Loaded model
    """
    model = tf.keras.models.load_model(model_path)
    logger.info(f"Model loaded from {model_path}")
    return model


def save_training_history(
    history: dict,
    output_path: str
) -> None:
    """
    Save training history to JSON file.
    
    Args:
        history: Training history dictionary
        output_path: Path to save JSON
    """
    # Convert numpy arrays to lists for JSON serialization
    history_serializable = {}
    for key, values in history.items():
        if isinstance(values, list):
            history_serializable[key] = [float(v) for v in values]
        else:
            history_serializable[key] = values
    
    with open(output_path, 'w') as f:
        json.dump(history_serializable, f, indent=2)
    
    logger.info(f"Training history saved to {output_path}")


def save_model_metadata(
    metrics: dict,
    model_name: str,
    version: str = '1.0',
    output_path: str = None
) -> None:
    """
    Save model metadata and metrics.
    
    Args:
        metrics: Evaluation metrics dictionary
        model_name: Name of the model
        version: Model version
        output_path: Path to save metadata
    """
    if output_path is None:
        output_path = MODELS_DIR / 'model_metadata.json'
    
    metadata = {
        'model_name': model_name,
        'version': version,
        'input_shape': INPUT_SHAPE,
        'num_classes': NUM_CLASSES,
        'metrics': metrics,
        'architecture': 'MobileNetV2 Transfer Learning',
        'learning_rate': LEARNING_RATE,
        'batch_size': BATCH_SIZE
    }
    
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Model metadata saved to {output_path}")
