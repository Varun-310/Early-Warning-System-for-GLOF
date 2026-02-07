import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout # type: ignore
from tensorflow.keras.preprocessing.image import ImageDataGenerator # type: ignore
from sklearn.model_selection import train_test_split

# Load and preprocess the dataset
def load_images_from_folder(folder_path, label, img_size=(128, 128)):
    images = []
    labels = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tif')):
            image = tf.keras.utils.load_img(file_path, target_size=img_size)
            image = tf.keras.utils.img_to_array(image) / 255.0
            images.append(image)
            labels.append(label)
    return np.array(images), np.array(labels)

# Paths to folders
pre_glof_folder = "data\processed_during-glof"
during_glof_folder = "data\processed_pre-glof"
post_glof_folder = "data\processed_post-glof"

# Load data
pre_glof_images, pre_glof_labels = load_images_from_folder(pre_glof_folder, label=0)
during_glof_images, during_glof_labels = load_images_from_folder(during_glof_folder, label=1)
post_glof_images, post_glof_labels = load_images_from_folder(post_glof_folder, label=2)

# Combine data
all_images = np.vstack((pre_glof_images, during_glof_images, post_glof_images))
all_labels = np.hstack((pre_glof_labels, during_glof_labels, post_glof_labels))

# Split data into training, validation, and test sets
X_train, X_temp, y_train, y_temp = train_test_split(all_images, all_labels, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Define the CNN model
model = Sequential([
    # Convolutional and Pooling layers
    Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 3)),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),

    # Flatten and Dense layers
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(3, activation='softmax')  # Adjust output layer for 3 classes
])

# Compile the model
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Data augmentation
datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True
)

# Train the model
history = model.fit(
    datagen.flow(X_train, y_train, batch_size=32),
    validation_data=(X_val, y_val),
    epochs=20,
    verbose=1
)

# Evaluate the model on test data
test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"Test Accuracy: {test_accuracy:.2f}")

# Save the model
model.save("glof_cnn_model.h5")
