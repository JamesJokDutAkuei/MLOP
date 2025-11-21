"""
Data Acquisition Module for Brain Tumor MRI Classification

Downloads the Brain Tumor MRI dataset from Kaggle using kagglehub.
Organizes images into train/test splits by class.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict
import shutil

try:
    import kagglehub
except ImportError:
    print("kagglehub not installed. Install with: pip install kagglehub")
    kagglehub = None

import numpy as np
from PIL import Image

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_acquisition.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
TRAIN_DIR = DATA_DIR / 'train'
TEST_DIR = DATA_DIR / 'test'

# Kaggle dataset
DATASET_NAME = 'masoudnickparvar/brain-tumor-mri-dataset'

# Class mapping
CLASS_LABELS = {
    'Glioma': 'Glioma',
    'Meningioma': 'Meningioma',
    'Pituitary': 'Pituitary',
    'No_Tumor': 'No_Tumor'
}


def setup_directories() -> None:
    """Create necessary directories for data storage."""
    logger.info("Setting up directories...")
    TRAIN_DIR.mkdir(parents=True, exist_ok=True)
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories for each class
    for class_name in CLASS_LABELS.values():
        (TRAIN_DIR / class_name).mkdir(parents=True, exist_ok=True)
        (TEST_DIR / class_name).mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Directories ready at {DATA_DIR}")


def download_dataset() -> Path:
    """
    Download Brain Tumor MRI dataset from Kaggle using kagglehub.
    
    Returns:
        Path to downloaded dataset
    """
    if kagglehub is None:
        logger.error("kagglehub not available. Install with: pip install kagglehub")
        raise ImportError("kagglehub")
    
    logger.info(f"Downloading Kaggle dataset: {DATASET_NAME}")
    logger.info("This may take 5-15 minutes depending on internet speed...")
    
    try:
        # Download latest version
        path = kagglehub.dataset_download(DATASET_NAME)
        logger.info(f"✓ Dataset downloaded to: {path}")
        return Path(path)
    except Exception as e:
        logger.error(f"Failed to download dataset: {e}")
        raise


def organize_images_from_kagglehub(raw_data_path: Path) -> Dict[str, int]:
    """
    Organize images from kagglehub download into train/test by class.
    kagglehub datasets are typically organized by class directories.
    
    Args:
        raw_data_path: Path to kagglehub downloaded data
        
    Returns:
        Statistics dictionary with counts
    """
    logger.info("Organizing images by class and split...")
    
    train_count = 0
    test_count = 0
    stats = {'train': {}, 'test': {}, 'total': 0}
    
    # Initialize counters
    for class_name in CLASS_LABELS.values():
        stats['train'][class_name] = 0
        stats['test'][class_name] = 0
    
    np.random.seed(42)
    split_ratio = 0.75  # 75% train, 25% test
    
    # Find all jpg/png files in downloaded data
    image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    
    for image_file in sorted(raw_data_path.rglob('*')):
        if image_file.suffix in image_extensions and image_file.is_file():
            try:
                # Verify it's a valid image
                Image.open(image_file).verify()
                
                # Determine class from parent directory
                class_dir = image_file.parent.name
                
                # Find matching class
                class_name = None
                for key in CLASS_LABELS.values():
                    if key.lower() == class_dir.lower():
                        class_name = key
                        break
                
                if class_name is None:
                    # Try without underscore/case sensitivity
                    class_dir_normalized = class_dir.lower().replace('_', '')
                    for key in CLASS_LABELS.values():
                        if key.lower().replace('_', '') == class_dir_normalized:
                            class_name = key
                            break
                
                if class_name is None:
                    logger.warning(f"Could not determine class for: {image_file}")
                    continue
                
                # Random train/test split
                is_train = np.random.rand() < split_ratio
                target_dir = TRAIN_DIR if is_train else TEST_DIR
                target_dir = target_dir / class_name
                
                # Copy image
                dest_path = target_dir / image_file.name
                shutil.copy2(image_file, dest_path)
                
                # Update statistics
                if is_train:
                    train_count += 1
                    stats['train'][class_name] += 1
                else:
                    test_count += 1
                    stats['test'][class_name] += 1
                
                stats['total'] += 1
                
                if stats['total'] % 500 == 0:
                    logger.info(f"Processed {stats['total']} images...")
                    
            except Exception as e:
                logger.warning(f"Failed to process image {image_file}: {e}")
                continue
    
    logger.info(f"✓ Organized {train_count} training images and {test_count} test images")
    return stats


def validate_and_save_statistics(stats: Dict) -> None:
    """
    Validate organized images and save statistics.
    
    Args:
        stats: Statistics dictionary
    """
    logger.info("Validating image organization...")
    
    # Log statistics
    logger.info("=" * 60)
    logger.info("DATASET STATISTICS")
    logger.info("=" * 60)
    logger.info("\nTraining Set:")
    for class_name, count in stats['train'].items():
        logger.info(f"  {class_name}: {count} images")
    
    logger.info("\nTest Set:")
    for class_name, count in stats['test'].items():
        logger.info(f"  {class_name}: {count} images")
    
    logger.info(f"\nTotal: {stats['total']} images")
    logger.info("=" * 60)
    
    # Save statistics
    stats_file = DATA_DIR / 'dataset_stats.json'
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    logger.info(f"✓ Statistics saved to {stats_file}")


def main():
    """Main data acquisition workflow."""
    try:
        logger.info("Starting Brain Tumor MRI dataset download...")
        
        # Setup directories
        setup_directories()
        
        # Download dataset using kagglehub
        raw_data_path = download_dataset()
        
        # Organize images by class and split
        stats = organize_images_from_kagglehub(raw_data_path)
        
        # Validate and save statistics
        validate_and_save_statistics(stats)
        
        logger.info("✓ Data acquisition complete!")
        logger.info(f"Dataset is ready in: {DATA_DIR}")
        
    except Exception as e:
        logger.error(f"✗ Data acquisition failed: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()






def load_image_data(raw_data_path: Path) -> tuple:
    """Load and organize images from raw download (legacy - not used with kagglehub)."""
    logger.info("Loading and organizing image data...")
    images = []
    labels = []
    image_paths = []
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    
    for image_file in sorted(raw_data_path.rglob('*')):
        if image_file.suffix in image_extensions and image_file.is_file():
            try:
                img = Image.open(image_file).convert('RGB')
                images.append(np.array(img))
                image_paths.append(image_file)
            except Exception as e:
                logger.warning(f"Failed to load image {image_file}: {e}")
                continue
    
    logger.info(f"Loaded {len(images)} images")
    return images, labels, image_paths

