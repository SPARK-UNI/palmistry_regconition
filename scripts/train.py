import os
import numpy as np
import pickle
import json
from tensorflow import keras
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import matplotlib.pyplot as plt

# Configure GPU settings
def setup_gpu():
    print("Setting up GPU configuration...")
    print("TF:", tf.__version__)
    print("Built with CUDA:", tf.test.is_built_with_cuda())
    print("CUDA available (runtime):", tf.test.is_built_with_gpu_support())
    print("Physical devices:", tf.config.list_physical_devices())
    gpus = tf.config.list_physical_devices('GPU')
    if not gpus:
        print(">> No GPU visible to TensorFlow.")
        return False
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f">> Using GPU: {gpus}")
        return True
    except RuntimeError as e:
        print("GPU setup error:", e)
        return False


class PalmistryANNTrainer:
    def __init__(self, data_path, output_path):
        self.data_path = data_path
        self.output_path = output_path
        self.model = None
        
        # Palm reading attributes with detailed descriptions
        self.palm_attributes = {
            'fate': {
                'name': 'Đường Số Phận',
                'description': 'Cuộc đời bấp bênh, nhiều thay đổi, có nhiều cơ hội nhưng cần biết nắm bắt',
                'characteristics': ['Thay đổi nhiều', 'Bấp bênh', 'Cần kiên trì']
            },
            'head': {
                'name': 'Đường Trí Tuệ',
                'description': 'Thần kinh vững vàng, sáng suốt, ít bệnh tật, có khả năng tư duy tốt',
                'characteristics': ['Sáng suốt', 'Vững vàng', 'Ít bệnh tật']
            },
            'heart': {
                'name': 'Đường Cảm Tình',
                'description': 'Tình cảm rộng rãi, cởi mở, hòa đồng, có lòng nhân từ và hảo tâm',
                'characteristics': ['Cởi mở', 'Hòa đồng', 'Nhân từ']
            },
            'life': {
                'name': 'Đường Sinh Mệnh',
                'description': 'Sức sống dồi dào, sức khỏe tốt, độ lượng hào phóng, tự tin',
                'characteristics': ['Sức khỏe tốt', 'Hào phóng', 'Tự tin']
            }
        }
    
    def load_data(self):
        """Load preprocessed data"""
        print("Loading preprocessed data...")
        
        X_train = np.load(os.path.join(self.data_path, 'train', 'X_train.npy'))
        y_train = np.load(os.path.join(self.data_path, 'train', 'y_train.npy'))
        X_val = np.load(os.path.join(self.data_path, 'valid', 'X_val.npy'))
        y_val = np.load(os.path.join(self.data_path, 'valid', 'y_val.npy'))
        
        # Load label encoder
        with open(os.path.join(self.data_path, 'label_encoder.pkl'), 'rb') as f:
            self.label_encoder = pickle.load(f)
        
        self.num_classes = len(self.label_encoder.classes_)
        
        # Convert labels to categorical
        y_train_cat = to_categorical(y_train, self.num_classes)
        y_val_cat = to_categorical(y_val, self.num_classes)
        
        print(f"Training data shape: {X_train.shape}")
        print(f"Validation data shape: {X_val.shape}")
        print(f"Number of classes: {self.num_classes}")
        print(f"Classes: {list(self.label_encoder.classes_)}")
        
        return X_train, y_train_cat, X_val, y_val_cat
    
    def create_model(self, input_shape):
        """Create ANN model with only Dense layers"""
        model = Sequential([
            # Input layer
            Dense(512, activation='relu', input_shape=input_shape, name='dense_1'),
            
            # Hidden layers
            Dense(256, activation='relu', name='dense_2'),
            Dense(128, activation='relu', name='dense_3'),
            Dense(64, activation='relu', name='dense_4'),
            Dense(32, activation='relu', name='dense_5'),
            
            # Output layer
            Dense(self.num_classes, activation='softmax', name='output')
        ])
        
        return model
    
    def compile_model(self, model):
        """Compile the model"""
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train_model(self, X_train, y_train, X_val, y_val, epochs=100):
        """Train the model"""
        print("Creating and compiling model...")
        
        # Create model
        input_shape = (X_train.shape[1],)
        self.model = self.create_model(input_shape)
        self.model = self.compile_model(self.model)
        
        # Print model summary
        print("\nModel Architecture:")
        self.model.summary()
        
        # Setup callbacks
        os.makedirs(self.output_path, exist_ok=True)
        
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            ModelCheckpoint(
                filepath=os.path.join(self.output_path, 'best_model.h5'),
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            )
        ]
        
        print("\nStarting training...")
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=32,
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def save_model_artifacts(self):
        """Save model and related files"""
        print("Saving model artifacts...")
        
        # Save final model
        self.model.save(os.path.join(self.output_path, 'model.h5'))
        
        # Create labels.txt file
        labels_path = os.path.join(self.output_path, 'labels.txt')
        with open(labels_path, 'w', encoding='utf-8') as f:
            for label in self.label_encoder.classes_:
                f.write(f"{label}\n")
        
        # Create attr_config.json file
        attr_config = {
            'model_info': {
                'model_type': 'ANN',
                'input_shape': [224, 224, 3],
                'num_classes': self.num_classes,
                'classes': list(self.label_encoder.classes_)
            },
            'palm_attributes': self.palm_attributes,
            'preprocessing': {
                'image_size': [224, 224],
                'normalization': 'divide_by_255',
                'flatten': True
            }
        }
        
        attr_config_path = os.path.join(self.output_path, 'attr_config.json')
        with open(attr_config_path, 'w', encoding='utf-8') as f:
            json.dump(attr_config, f, ensure_ascii=False, indent=4)
        
        print(f"Model saved to: {os.path.join(self.output_path, 'model.h5')}")
        print(f"Labels saved to: {labels_path}")
        print(f"Config saved to: {attr_config_path}")
    
    def plot_training_history(self, history):
        """Plot training history"""
        plt.figure(figsize=(12, 4))
        
        # Plot accuracy
        plt.subplot(1, 2, 1)
        plt.plot(history.history['accuracy'], label='Training Accuracy')
        plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
        plt.title('Model Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        
        # Plot loss
        plt.subplot(1, 2, 2)
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_path, 'training_history.png'))
        plt.show()
    
    def evaluate_model(self):
        """Evaluate model on test set"""
        if os.path.exists(os.path.join(self.data_path, 'test', 'X_test.npy')):
            print("Evaluating on test set...")
            
            X_test = np.load(os.path.join(self.data_path, 'test', 'X_test.npy'))
            y_test = np.load(os.path.join(self.data_path, 'test', 'y_test.npy'))
            y_test_cat = to_categorical(y_test, self.num_classes)
            
            test_loss, test_accuracy = self.model.evaluate(X_test, y_test_cat, verbose=1)
            print(f"Test Accuracy: {test_accuracy:.4f}")
            print(f"Test Loss: {test_loss:.4f}")
            
            return test_accuracy, test_loss
        else:
            print("No test data found.")
            return None, None

def main():
    # Configure paths
    DATA_PATH = "data"
    OUTPUT_PATH = "model"
    
    # Initialize trainer
    trainer = PalmistryANNTrainer(DATA_PATH, OUTPUT_PATH)
    
    try:
        # Load data
        X_train, y_train, X_val, y_val = trainer.load_data()
        
        # Train model
        history = trainer.train_model(X_train, y_train, X_val, y_val, epochs=100)
        
        # Save model artifacts
        trainer.save_model_artifacts()
        
        # Plot training history
        trainer.plot_training_history(history)
        
        # Evaluate model
        trainer.evaluate_model()
        
        print("\nTraining completed successfully!")
        print("Files generated:")
        print("- model/model.h5")
        print("- model/labels.txt") 
        print("- model/attr_config.json")
        
    except Exception as e:
        print(f"Error during training: {str(e)}")
        raise

if __name__ == "__main__":
    main()