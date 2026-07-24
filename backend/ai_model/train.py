"""
train.py
--------
Trains the waste bin image classifier on a custom dataset and saves the
resulting model to ai_model/saved_model/waste_classifier.h5

HOW TO USE WITH YOUR OWN DATASET:
1. Collect photos of bins and sort them into folders:

    dataset/
        train/
            empty/        <- photos of empty bins
            half_full/    <- photos of half-full bins
            full/         <- photos of full/overflowing bins
        val/
            empty/
            half_full/
            full/

   Aim for at least 150-200 images per class for a reasonable baseline,
   and 500+ per class for production quality. Include varied lighting,
   angles, bin types, and backgrounds so the model generalizes well.

2. Run this script:
       python train.py --epochs 20 --batch_size 32

3. The trained model is saved to ai_model/saved_model/waste_classifier.h5
   and is automatically picked up by the backend on next restart.
"""

import argparse
import os
import tensorflow as tf
from model_architecture import build_model, unfreeze_for_finetuning, IMG_SIZE, CLASS_NAMES

DATASET_DIR = os.path.join(os.path.dirname(__file__), "..", "dataset")
SAVE_DIR = os.path.join(os.path.dirname(__file__), "saved_model")
MODEL_PATH = os.path.join(SAVE_DIR, "waste_classifier.h5")


def load_datasets(batch_size: int):
    """Loads train/val datasets from directory structure using Keras utilities."""
    train_ds = tf.keras.utils.image_dataset_from_directory(
        os.path.join(DATASET_DIR, "train"),
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=batch_size,
        label_mode="categorical",
        class_names=["empty", "half_full", "full"],  # order must match CLASS_NAMES
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        os.path.join(DATASET_DIR, "val"),
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=batch_size,
        label_mode="categorical",
        class_names=["empty", "half_full", "full"],
    )

    # Data augmentation to improve generalization on small datasets
    augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.1),
        tf.keras.layers.RandomZoom(0.1),
        tf.keras.layers.RandomBrightness(0.15),
    ])
    train_ds = train_ds.map(lambda x, y: (augmentation(x, training=True), y))

    # Prefetch for performance
    train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(tf.data.AUTOTUNE)
    return train_ds, val_ds


def main():
    parser = argparse.ArgumentParser(description="Train the waste bin classifier")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--finetune_epochs", type=int, default=5,
                         help="Extra epochs for fine-tuning the base model")
    args = parser.parse_args()

    os.makedirs(SAVE_DIR, exist_ok=True)

    print("Loading dataset...")
    train_ds, val_ds = load_datasets(args.batch_size)

    print("Building model...")
    model = build_model()
    model.summary()

    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint(MODEL_PATH, save_best_only=True, monitor="val_accuracy"),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3),
    ]

    print("Phase 1: training classification head...")
    model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=callbacks)

    print("Phase 2: fine-tuning base model...")
    model = unfreeze_for_finetuning(model)
    model.fit(train_ds, validation_data=val_ds, epochs=args.finetune_epochs, callbacks=callbacks)

    model.save(MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    print(f"Classes (in order): {CLASS_NAMES}")


if __name__ == "__main__":
    main()
