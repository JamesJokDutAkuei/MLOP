import tensorflow as tf
from pathlib import Path

SRC = Path('models/brain_tumor_model_best.h5')
DST = Path('models/brain_tumor_model_best.tflite')

if not SRC.exists():
    raise FileNotFoundError(f"Missing source model: {SRC}")

print(f"Loading {SRC}...")
model = tf.keras.models.load_model(SRC)

print("Converting to TFLite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
# Optional: enable default optimizations to reduce size
# converter.optimizations = [tf.lite.Optimize.DEFAULT]
# Optional: use float16 to shrink further (ensure acceptable accuracy)
# converter.target_spec.supported_types = [tf.float16]

tflite_model = converter.convert()

DST.write_bytes(tflite_model)
print(f"Wrote {DST} ({DST.stat().st_size/1024:.1f} KB)")
