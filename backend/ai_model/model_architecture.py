"""
model_architecture.py
----------------------
Defines the CNN architecture used to classify waste bin images into:
    0 -> Empty
    1 -> Half Full
    2 -> Full

Uses transfer learning on MobileNetV2 (lightweight, fast, works well on
small custom datasets, and is suitable for edge/low-cost deployment
such as Raspberry Pi cameras monitoring real bins).
"""

import tensorflow as tf
from tensorflow.keras import layers, models

IMG_SIZE = 224
NUM_CLASSES = 3
CLASS_NAMES = ["Empty", "Half Full", "Full"]


def build_model(input_size: int = IMG_SIZE, num_classes: int = NUM_CLASSES) -> tf.keras.Model:
    """
    Builds a transfer-learning model using MobileNetV2 as a frozen base
    with a custom classification head on top.

    Returns:
        A compiled tf.keras.Model ready for training.
    """
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(input_size, input_size, 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False  # freeze base for initial training (fine-tune later if desired)

    inputs = layers.Input(shape=(input_size, input_size, 3))
    # MobileNetV2 expects pixel values scaled to [-1, 1]
    x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = models.Model(inputs, outputs, name="waste_bin_classifier")

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def unfreeze_for_finetuning(model: tf.keras.Model, num_layers_to_unfreeze: int = 30):
    """
    Optional step-2 fine-tuning: unfreeze the last N layers of the base
    model and recompile with a lower learning rate. Call this after the
    initial training phase has plateaued for a small accuracy boost.
    """
    base_model = model.layers[2]  # the MobileNetV2 layer inside our model
    base_model.trainable = True
    for layer in base_model.layers[:-num_layers_to_unfreeze]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model
