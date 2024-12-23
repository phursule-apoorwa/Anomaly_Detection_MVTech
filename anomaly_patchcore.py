
from google.colab import drive
drive.mount('/content/drive')

!pip install tqdm scikit-learn

pip install tensorflow faiss-gpu

import tensorflow as tf
from tensorflow import keras
import numpy as np
import os
import time
import sys
from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

# Add the src directory to Python path
current_dir = '/content/drive/MyDrive'  # Update this path
src_dir = os.path.join(current_dir, 'src')
sys.path.append(current_dir)
sys.path.append(src_dir)

# Rest of your imports
from src.data_preprocessing import load_mvtec_data, create_data_generator
from src.model import build_model
from src.train import train_model, fit_memory_banks
from src.evaluate import evaluate_model
from src.visualize import plot_roc_pr_curves, plot_anomaly_examples, plot_anomaly_score_distribution

# Configuration
DATA_DIR = "/content/drive/MyDrive/screw"  # Update this path
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16  # Increased for faster training on Colab
EPOCHS = 30
LEARNING_RATE = 0.001

def main():
    # Check if GPU is available
    print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

    # Check if the dataset exists
    if not os.path.exists(DATA_DIR):
        raise FileNotFoundError(f"Dataset not found at {DATA_DIR}. Please check the path.")

    # Load and preprocess data
    print("Loading and preprocessing data...")
    normal_train, test_images, test_labels = load_mvtec_data(DATA_DIR, image_size=IMAGE_SIZE)
    train_dataset = create_data_generator(normal_train, batch_size=BATCH_SIZE)

    # Calculate steps_per_epoch
    steps_per_epoch = len(normal_train) // BATCH_SIZE
    print(f"Steps per epoch: {steps_per_epoch}")

    # Print debug information
    print(f"normal_train shape: {normal_train.shape}")
    print(f"test_images shape: {test_images.shape}")
    print(f"test_labels shape: {test_labels.shape}")
    print(f"train_dataset type: {type(train_dataset)}")

    # Build the model
    print("Building the model...")
    model = build_model(input_shape=IMAGE_SIZE + (3,))

    # Create optimizer
    optimizer = keras.optimizers.Adam(learning_rate=LEARNING_RATE)

    # Compile the model
    model.compile(optimizer=optimizer)

    # Initialize optimizer variables
    dummy_data = tf.zeros((1,) + IMAGE_SIZE + (3,))
    _ = model(dummy_data, training=True)
    _ = optimizer.apply_gradients(zip([tf.zeros_like(v) for v in model.trainable_variables],
                                      model.trainable_variables))

    # Train the model
    print("Training the model...")
    start_time = time.time()
    try:
        trained_model = train_model(model, train_dataset, epochs=EPOCHS, optimizer=optimizer, steps_per_epoch=steps_per_epoch)

        # Fit memory banks after training
        print("Fitting memory banks...")
        fit_memory_banks(trained_model, normal_train)
    except Exception as e:
        print(f"Error during training or fitting memory banks: {e}")
        import traceback
        traceback.print_exc()
        return

    # Evaluate the model
    print("Evaluating the model...")
    auc_roc, auc_pr, precision, recall, anomaly_scores = evaluate_model(trained_model, test_images, test_labels)

    print(f"AUC-ROC: {auc_roc:.4f}")
    print(f"AUC-PR: {auc_pr:.4f}")

    # Visualize results
    print("Generating visualizations...")
    plot_roc_pr_curves(test_labels, anomaly_scores)
    plot_anomaly_examples(test_images, test_labels, anomaly_scores)
    plot_anomaly_score_distribution(anomaly_scores, test_labels)

    # Save the model
    save_dir = os.path.join('/content/drive/MyDrive/path/to/your/project', 'saved_models')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, 'anomaly_detection_model_screw.keras')
    trained_model.save(save_path)
    print(f"Model saved to {save_path}")

if __name__ == "__main__":
    main()

import tensorflow as tf
from tensorflow import keras
import numpy as np
import os
import time
import sys
from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

# Add the src directory to Python path
current_dir = '/content/drive/MyDrive'  # Update this path
src_dir = os.path.join(current_dir, 'src')
sys.path.append(current_dir)
sys.path.append(src_dir)

# Rest of your imports
from src.data_preprocessing import load_mvtec_data, create_data_generator
from src.model import EnsemblePatchCore
from src.train import train_model, fit_memory_banks
from src.evaluate import evaluate_model
from src.visualize import plot_roc_pr_curves, plot_anomaly_examples, plot_anomaly_score_distribution

# Configuration
DATA_DIR = "/content/drive/MyDrive/screw"  # Update this path
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32  # Increased for faster training on Colab
EPOCHS = 120
LEARNING_RATE = 0.001

def main():
    # Check if GPU is available
    print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

    # Check if the dataset exists
    if not os.path.exists(DATA_DIR):
        raise FileNotFoundError(f"Dataset not found at {DATA_DIR}. Please check the path.")

    # Load and preprocess data
    print("Loading and preprocessing data...")
    normal_train, test_images, test_labels = load_mvtec_data(DATA_DIR, image_size=IMAGE_SIZE)
    train_dataset = create_data_generator(normal_train, batch_size=BATCH_SIZE)

    # Calculate steps_per_epoch
    steps_per_epoch = len(normal_train) // BATCH_SIZE
    print(f"Steps per epoch: {steps_per_epoch}")

    # Print debug information
    print(f"normal_train shape: {normal_train.shape}")
    print(f"test_images shape: {test_images.shape}")
    print(f"test_labels shape: {test_labels.shape}")
    print(f"train_dataset type: {type(train_dataset)}")

    # Build the model
    print("Building the model...")
    model = EnsemblePatchCore(input_shape=IMAGE_SIZE + (3,), scales=[1.0, 0.5])

    # Create optimizer
    optimizer = keras.optimizers.Adam(learning_rate=LEARNING_RATE)

    # Initialize optimizer variables
    dummy_data = tf.zeros((1,) + IMAGE_SIZE + (3,))
    _ = model(dummy_data, training=True)
    _ = optimizer.apply_gradients(zip([tf.zeros_like(v) for v in model.trainable_variables],
                                      model.trainable_variables))

    # Train the model
    print("Training the model...")
    start_time = time.time()
    try:
        trained_model = train_model(model, train_dataset, epochs=EPOCHS, optimizer=optimizer, steps_per_epoch=steps_per_epoch)

        # Fit memory banks after training
        print("Fitting memory banks...")
        fit_memory_banks(trained_model, normal_train)
    except Exception as e:
        print(f"Error during training or fitting memory banks: {e}")
        import traceback
        traceback.print_exc()
        return

    # Evaluate the model
    print("Evaluating the model...")
    auc_roc, auc_pr, precision, recall, anomaly_scores = evaluate_model(trained_model, test_images, test_labels)

    print(f"AUC-ROC: {auc_roc:.4f}")
    print(f"AUC-PR: {auc_pr:.4f}")

    # Visualize results
    print("Generating visualizations...")
    plot_roc_pr_curves(test_labels, anomaly_scores)
    plot_anomaly_examples(test_images, test_labels, anomaly_scores)
    plot_anomaly_score_distribution(anomaly_scores, test_labels)

    # Save the model
    save_dir = os.path.join('/content/drive/MyDrive/path/to/your/project', 'saved_models')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, 'anomaly_detection_model_screw.keras')
    trained_model.save(save_path)
    print(f"Model saved to {save_path}")

if __name__ == "__main__":
    main()
