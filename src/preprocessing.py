"""
Preprocessing Module for Brain Tumor MRI Images

Handles image loading, normalization, augmentation, and dataset preparation.
"""

import os
import logging
from pathlib import Path
from typing import Tuple, List
import numpy as np

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from PIL import Image

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
RANDOM_SEED = 42

# Class labels
CLASS_LABELS = {
    'CBSD': 0,
    'CGM': 1,
    'CMD': 2,
    'Healthy': 3,
    'Unknown': 4
}

INVERSE_CLASS_LABELS = {v: k for k, v in CLASS_LABELS.items()}


def load_and_preprocess_image(
    image_path: str,
    target_size: Tuple[int, int] = IMAGE_SIZE
) -> np.ndarray:
    """
    Load and preprocess a single image.
    
    Args:
        image_path: Path to image file
        target_size: Target image size (height, width)
        
    Returns:
        Preprocessed image array
    """
    try:
        # Load image
        img = Image.open(image_path).convert('RGB')
        
        # Resize
        img = img.resize(target_size, Image.LANCZOS)
        
        # Convert to array
        img_array = np.array(img, dtype=np.float32)
        
        # Normalize to [0, 1]
        img_array = img_array / 255.0
        
        return img_array
        
    except Exception as e:
        logger.error(f"Failed to load image {image_path}: {e}")
        return None


def load_dataset_from_directory(
    data_dir: Path,
    target_size: Tuple[int, int] = IMAGE_SIZE
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Load all images from directory structure organized by class.
    
    Args:
        data_dir: Path to directory containing class subdirectories
        target_size: Target image size
        
    Returns:
        Tuple of (images, labels, file_paths)
    """
    logger.info(f"Loading dataset from {data_dir}")
    
    images = []
    labels = []
    file_paths = []
    
    for class_idx, (class_name, class_label) in enumerate(CLASS_LABELS.items()):
        class_dir = data_dir / class_name
        
        if not class_dir.exists():
            logger.warning(f"Class directory not found: {class_dir}")
            continue
        
        # Load all images in class directory
        image_files = list(class_dir.glob('*.jpg')) + list(class_dir.glob('*.png'))
        logger.info(f"Loading {len(image_files)} images from class: {class_name}")
        
        for image_file in image_files:
            img_array = load_and_preprocess_image(str(image_file), target_size)
            
            if img_array is not None:
                images.append(img_array)
                labels.append(class_label)
                file_paths.append(str(image_file))
    
    images = np.array(images)
    labels = np.array(labels)
    
    logger.info(f"Loaded {len(images)} images total")
    logger.info(f"Images shape: {images.shape}")
    logger.info(f"Labels shape: {labels.shape}")
    
    return images, labels, file_paths


def create_train_val_test_split(
    images: np.ndarray,
    labels: np.ndarray,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_seed: int = RANDOM_SEED
) -> Tuple[Tuple, Tuple, Tuple]:
    """
    Split dataset into train, validation, and test sets.
    
    Args:
        images: Array of images
        labels: Array of labels
        train_ratio: Training set ratio
        val_ratio: Validation set ratio
        test_ratio: Test set ratio
        random_seed: Random seed for reproducibility
        
    Returns:
        Tuple of (train_data, val_data, test_data)
        Each containing (images, labels)
    """
    logger.info(f"Creating train/val/test split: {train_ratio}/{val_ratio}/{test_ratio}")
    
    # First split: train+val vs test
    X_temp, X_test, y_temp, y_test = train_test_split(
        images, labels,
        test_size=test_ratio,
        random_state=random_seed,
        stratify=labels
    )
    
    # Second split: train vs val
    val_size = val_ratio / (train_ratio + val_ratio)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp,
        test_size=val_size,
        random_state=random_seed,
        stratify=y_temp
    )
    
    logger.info(f"Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")
    
    return (X_train, y_train), (X_val, y_val), (X_test, y_test)


def create_data_augmentation(
    horizontal_flip: bool = True,
    vertical_flip: bool = False,
    rotation_range: int = 20,
    zoom_range: float = 0.2,
    brightness_range: List[float] = [0.8, 1.2],
    shear_range: float = 0.1,
    fill_mode: str = 'nearest'
) -> ImageDataGenerator:
    """
    Create image data augmentation generator.
    
    Args:
        horizontal_flip: Enable horizontal flip
        vertical_flip: Enable vertical flip
        rotation_range: Rotation range in degrees
        zoom_range: Zoom range
        brightness_range: Brightness range
        shear_range: Shear range
        fill_mode: Fill mode for new pixels
        
    Returns:
        ImageDataGenerator instance
    """
    logger.info("Creating data augmentation generator")
    
    augmentation = ImageDataGenerator(
        horizontal_flip=horizontal_flip,
        vertical_flip=vertical_flip,
        rotation_range=rotation_range,
        zoom_range=zoom_range,
        brightness_range=brightness_range,
        shear_range=shear_range,
        fill_mode=fill_mode,
        rescale=1.0 / 255.0  # Normalization
    )
    
    return augmentation


def normalize_images(
    images: np.ndarray,
    mean: List[float] = [0.485, 0.456, 0.406],
    std: List[float] = [0.229, 0.224, 0.225]
) -> np.ndarray:
    """
    Normalize images using ImageNet statistics.
    
    Args:
        images: Array of images (RGB, values 0-1)
        mean: Mean values for each channel
        std: Standard deviation values for each channel
        
    Returns:
        Normalized images
    """
    logger.info("Normalizing images with ImageNet statistics")
    
    # Convert to numpy array if needed
    images = np.array(images)
    
    # Apply normalization per channel
    for i in range(3):
        images[:, :, :, i] = (images[:, :, :, i] - mean[i]) / std[i]
    
    return images


def one_hot_encode_labels(
    labels: np.ndarray,
    num_classes: int = len(CLASS_LABELS)
) -> np.ndarray:
    """
    Convert labels to one-hot encoded format.
    
    Args:
        labels: Array of class indices
        num_classes: Number of classes
        
    Returns:
        One-hot encoded labels
    """
    return tf.keras.utils.to_categorical(labels, num_classes=num_classes)


def create_tf_dataset(
    images: np.ndarray,
    labels: np.ndarray,
    batch_size: int = BATCH_SIZE,
    augment: bool = False,
    shuffle: bool = True
) -> tf.data.Dataset:
    """
    Create TensorFlow dataset from images and labels.
    
    Args:
        images: Array of images
        labels: Array of labels (one-hot encoded)
        batch_size: Batch size
        augment: Enable augmentation
        shuffle: Enable shuffling
        
    Returns:
        tf.data.Dataset instance
    """
    # Create dataset from tensors
    dataset = tf.data.Dataset.from_tensor_slices((images, labels))
    
    if shuffle:
        dataset = dataset.shuffle(buffer_size=len(images))
    
    if augment:
        # Apply augmentation
        def augment_fn(image, label):
            # Random rotation
            image = tf.image.rot90(image, k=tf.random.uniform([], 0, 4, dtype=tf.int32))
            # Random horizontal flip
            image = tf.image.random_flip_left_right(image)
            # Random brightness
            image = tf.image.random_brightness(image, 0.2)
            return image, label
        
        dataset = dataset.map(augment_fn, num_parallel_calls=tf.data.AUTOTUNE)
    
    # Batch
    dataset = dataset.batch(batch_size)
    dataset = dataset.prefetch(tf.data.AUTOTUNE)
    
    return dataset


def get_class_weights(labels: np.ndarray) -> dict:
    """
    Calculate class weights for imbalanced datasets.
    
    Args:
        labels: Array of class indices
        
    Returns:
        Dictionary mapping class index to weight
    """
    from sklearn.utils.class_weight import compute_class_weight
    
    class_weights = compute_class_weight(
        'balanced',
        classes=np.unique(labels),
        y=labels
    )
    
    class_weight_dict = {i: w for i, w in enumerate(class_weights)}
    
    logger.info("Class weights:")
    for class_idx, class_name in INVERSE_CLASS_LABELS.items():
        logger.info(f"  {class_name}: {class_weight_dict[class_idx]:.4f}")
    
    return class_weight_dict


def get_image_statistics(
    images: np.ndarray,
    labels: np.ndarray
) -> dict:
    """
    Compute image statistics for visualization.
    
    Args:
        images: Array of images
        labels: Array of labels
        
    Returns:
        Dictionary with statistics
    """
    logger.info("Computing image statistics...")
    
    stats = {
        'total_images': len(images),
        'image_shape': images[0].shape if len(images) > 0 else None,
        'value_range': (float(images.min()), float(images.max())),
        'mean_brightness': float(np.mean(images)),
        'std_brightness': float(np.std(images)),
        'class_distribution': {},
        'class_brightness_stats': {}
    }
    
    # Class distribution
    unique, counts = np.unique(labels, return_counts=True)
    for class_idx, count in zip(unique, counts):
        class_name = INVERSE_CLASS_LABELS.get(class_idx, 'Unknown')
        stats['class_distribution'][class_name] = int(count)
    
    # Per-class brightness
    for class_idx in np.unique(labels):
        class_images = images[labels == class_idx]
        class_name = INVERSE_CLASS_LABELS.get(class_idx, 'Unknown')
        stats['class_brightness_stats'][class_name] = {
            'mean': float(np.mean(class_images)),
            'std': float(np.std(class_images)),
            'min': float(np.min(class_images)),
            'max': float(np.max(class_images))
        }
    
    return stats
