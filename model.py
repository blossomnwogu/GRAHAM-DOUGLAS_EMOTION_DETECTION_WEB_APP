import tensorflow as tf
from tensorflow.keras import layers, Sequential
import numpy as np

def create_emotion_model():
    """Create a simple CNN model for emotion detection"""
    model = Sequential([
        layers.Conv2D(32, (3,3), activation='relu', input_shape=(48, 48, 1)),
        layers.MaxPooling2D(2,2),
        layers.Conv2D(64, (3,3), activation='relu'),
        layers.MaxPooling2D(2,2),
        layers.Conv2D(128, (3,3), activation='relu'),
        layers.MaxPooling2D(2,2),
        layers.Flatten(),
        layers.Dense(512, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(7, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def train_demo_model():
    """Create and save a demo model structure"""
    model = create_emotion_model()
    model.save('emotion_model.h5')
    print("Demo model created and saved as emotion_model.h5")
    print("Note: This model has random weights. For real use, train with emotion dataset.")

if __name__ == "__main__":
    train_demo_model()