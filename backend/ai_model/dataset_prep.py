"""
dataset_prep.py
----------------
Utility script to split a flat folder of labeled images into the
train/val directory structure expected by train.py.

Usage:
    python dataset_prep.py --source raw_images --split 0.8

Expected input structure (raw_images/):
    raw_images/
        empty/
            img1.jpg, img2.jpg, ...
        half_full/
            img1.jpg, ...
        full/
            img1.jpg, ...

Output:
    dataset/train/<class>/...   (80% of images, by default)
    dataset/val/<class>/...     (20% of images, by default)
"""

import argparse
import os
import random
import shutil

CLASSES = ["empty", "half_full", "full"]


def split_dataset(source_dir: str, dest_dir: str, split_ratio: float, seed: int = 42):
    random.seed(seed)
    for class_name in CLASSES:
        src_class_dir = os.path.join(source_dir, class_name)
        if not os.path.isdir(src_class_dir):
            print(f"Warning: {src_class_dir} not found, skipping.")
            continue

        images = [f for f in os.listdir(src_class_dir)
                  if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        random.shuffle(images)

        split_idx = int(len(images) * split_ratio)
        train_files, val_files = images[:split_idx], images[split_idx:]

        for subset, files in [("train", train_files), ("val", val_files)]:
            out_dir = os.path.join(dest_dir, subset, class_name)
            os.makedirs(out_dir, exist_ok=True)
            for f in files:
                shutil.copy2(os.path.join(src_class_dir, f), os.path.join(out_dir, f))

        print(f"{class_name}: {len(train_files)} train / {len(val_files)} val images")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Path to raw labeled images folder")
    parser.add_argument("--dest", default=os.path.join(os.path.dirname(__file__), "..", "dataset"))
    parser.add_argument("--split", type=float, default=0.8, help="Train split ratio")
    args = parser.parse_args()

    split_dataset(args.source, args.dest, args.split)
    print("Dataset split complete.")
