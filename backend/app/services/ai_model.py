"""
ai_model.py
-----------
Loads the trained TensorFlow model and exposes a simple predict()
function used by the API routers.

IMPORTANT (out-of-the-box behavior):
This project ships WITHOUT a pre-trained .h5 file because trained model
weights depend on your own dataset (see ai_model/train.py + the README
"Training the Model" section). On first run, if no trained model is
found at MODEL_PATH, this module automatically falls back to a
lightweight heuristic classifier (based on pixel-brightness / edge
density) so the full application is runnable end-to-end immediately.

Once you train a real model (python ai_model/train.py), drop the
resulting waste_classifier.h5 into ai_model/saved_model/ and restart
the server -- it will be loaded automatically and the heuristic
fallback will no longer be used.
"""

import os
import numpy as np
from PIL import Image
import logging

from app.config import settings

logger = logging.getLogger("ai_model")

CLASS_NAMES = ["Empty", "Half Full", "Full"]

_model = None
_model_loaded_from_file = False


def _try_load_tf_model():
    """Attempts to load a trained Keras model from disk. Returns None on failure."""
    global _model_loaded_from_file
    model_path = settings.MODEL_PATH
    if not os.path.exists(model_path):
        logger.warning(
            f"No trained model found at '{model_path}'. "
            "Using heuristic fallback classifier. See ai_model/train.py to train a real model."
        )
        return None
    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(model_path)
        _model_loaded_from_file = True
        logger.info(f"Loaded trained model from {model_path}")
        return model
    except Exception as e:
        logger.error(f"Failed to load model at {model_path}: {e}")
        return None


def get_model():
    """Lazily loads and caches the model (singleton pattern)."""
    global _model
    if _model is None:
        _model = _try_load_tf_model()
    return _model


def _heuristic_predict(image: Image.Image):
    """
    Fallback classifier used only when no trained model file is present.
    Estimates 'fullness' using a simple heuristic: darker / busier images
    (more visual clutter, less visible empty bin interior) are scored as
    more full. This is NOT a substitute for a trained model -- it exists
    purely so the application is demoable before training data is collected.
    """
    img = image.convert("L").resize((128, 128))  # grayscale
    arr = np.asarray(img, dtype=np.float32) / 255.0

    # Edge density as a proxy for clutter/fullness
    gy, gx = np.gradient(arr)
    edge_density = np.mean(np.sqrt(gx ** 2 + gy ** 2))

    # Normalize edge density into a pseudo "fullness score" 0-1
    fullness_score = float(np.clip(edge_density * 6.0, 0, 1))

    if fullness_score < 0.33:
        idx = 0  # Empty
        confidence = 0.55 + (0.33 - fullness_score)
    elif fullness_score < 0.66:
        idx = 1  # Half Full
        confidence = 0.55 + (0.15 - abs(fullness_score - 0.5)) * 0.5
    else:
        idx = 2  # Full
        confidence = 0.55 + (fullness_score - 0.66)

    confidence = float(np.clip(confidence, 0.5, 0.95))
    return CLASS_NAMES[idx], confidence


def _tf_predict(model, image: Image.Image):
    """Runs inference using the real trained TensorFlow model."""
    import tensorflow as tf
    size = settings.MODEL_INPUT_SIZE
    img = image.convert("RGB").resize((size, size))
    arr = np.asarray(img, dtype=np.float32)
    arr = np.expand_dims(arr, axis=0)

    preds = model.predict(arr, verbose=0)[0]
    idx = int(np.argmax(preds))
    confidence = float(preds[idx])
    return CLASS_NAMES[idx], confidence


def predict_image(image_path: str):
    """
    Main entry point used by the API layer.

    Args:
        image_path: path to the uploaded image on disk

    Returns:
        (prediction: str, confidence: float)
    """
    image = Image.open(image_path)
    model = get_model()

    if model is not None:
        return _tf_predict(model, image)
    return _heuristic_predict(image)


def is_using_trained_model() -> bool:
    """Lets API/health endpoints report whether real AI or the fallback is active."""
    get_model()
    return _model_loaded_from_file
