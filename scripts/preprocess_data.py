import os
import cv2
import numpy as np
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle

class PalmistryDataPreprocessor:
    def __init__(self, raw_data_path, output_path):
        self.raw_data_path = raw_data_path
        self.output_path = output_path
        self.image_size = (224, 224)  # Resize images to consistent size
        self.label_encoder = LabelEncoder()
        
        # Palm reading attributes mapping
        self.palm_attributes = {
            'fate': 'Đường số phận - Cuộc đời bấp bênh, nhiều thay đổi',
            'head': 'Đường trí tuệ - Thần kinh vững vàng, sáng suốt',
            'heart': 'Đường cảm tình - Tình cảm rộng rãi, cởi mở, hòa đồng',
            'life': 'Đường sinh mệnh - Sức sống, sức khỏe dồi dào'
        }
        
    def load_images_and_labels(self):
        """Load images and their corresponding labels"""
        images = []
        labels = []
        
        # Check if data is in YOLO or COCO format
        if self._is_yolo_format():
            images, labels = self._load_yolo_format()
        elif self._is_coco_format():
            images, labels = self._load_coco_format()
        else:
            # Fallback: assume folder structure with class names
            images, labels = self._load_folder_structure()
            
        return np.array(images), np.array(labels)
    
    def _is_yolo_format(self):
        """Check if data is in YOLO format"""
        txt_files = [f for f in os.listdir(self.raw_data_path) if f.endswith('.txt')]
        return len(txt_files) > 0 and any('classes' in f for f in txt_files)
    
    def _is_coco_format(self):
        """Check if data is in COCO format"""
        json_files = [f for f in os.listdir(self.raw_data_path) if f.endswith('.json')]
        return len(json_files) > 0
    
    def _load_yolo_format(self):
        """Load data from YOLO format"""
        images = []
        labels = []
        
        # Load class names
        classes_file = os.path.join(self.raw_data_path, 'classes.txt')
        if os.path.exists(classes_file):
            with open(classes_file, 'r', encoding='utf-8') as f:
                class_names = [line.strip() for line in f.readlines()]
        else:
            class_names = list(self.palm_attributes.keys())
        
        # Load images and labels
        for img_file in os.listdir(self.raw_data_path):
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(self.raw_data_path, img_file)
                label_file = img_file.rsplit('.', 1)[0] + '.txt'
                label_path = os.path.join(self.raw_data_path, label_file)
                
                if os.path.exists(label_path):
                    img = cv2.imread(img_path)
                    if img is not None:
                        img = cv2.resize(img, self.image_size)
                        img = img.astype(np.float32) / 255.0
                        images.append(img)
                        
                        # Read YOLO label (assuming first class in label file)
                        with open(label_path, 'r') as f:
                            line = f.readline().strip()
                            if line:
                                class_id = int(line.split()[0])
                                labels.append(class_names[class_id])
        
        return images, labels
    
    def _load_coco_format(self):
        """Load data from COCO format"""
        images = []
        labels = []
        
        # Find COCO annotation file
        json_files = [f for f in os.listdir(self.raw_data_path) if f.endswith('.json')]
        if not json_files:
            return images, labels
            
        with open(os.path.join(self.raw_data_path, json_files[0]), 'r', encoding='utf-8') as f:
            coco_data = json.load(f)
        
        # Create category mapping
        categories = {cat['id']: cat['name'] for cat in coco_data['categories']}
        
        # Load images and annotations
        image_info = {img['id']: img for img in coco_data['images']}
        
        for annotation in coco_data['annotations']:
            image_id = annotation['image_id']
            category_id = annotation['category_id']
            
            if image_id in image_info:
                img_info = image_info[image_id]
                img_path = os.path.join(self.raw_data_path, img_info['file_name'])
                
                if os.path.exists(img_path):
                    img = cv2.imread(img_path)
                    if img is not None:
                        img = cv2.resize(img, self.image_size)
                        img = img.astype(np.float32) / 255.0
                        images.append(img)
                        labels.append(categories[category_id])
        
        return images, labels
    
    def _load_folder_structure(self):
        """Load data from folder structure (each class in separate folder)"""
        images = []
        labels = []
        
        for class_name in os.listdir(self.raw_data_path):
            class_path = os.path.join(self.raw_data_path, class_name)
            if os.path.isdir(class_path):
                for img_file in os.listdir(class_path):
                    if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        img_path = os.path.join(class_path, img_file)
                        img = cv2.imread(img_path)
                        if img is not None:
                            img = cv2.resize(img, self.image_size)
                            img = img.astype(np.float32) / 255.0
                            images.append(img)
                            labels.append(class_name)
        
        return images, labels
    
    def preprocess_data(self):
        """Main preprocessing function"""
        print("Loading images and labels...")
        images, labels = self.load_images_and_labels()
        
        if len(images) == 0:
            print("No images found! Please check your data format.")
            return
        
        print(f"Loaded {len(images)} images with {len(set(labels))} classes")
        
        # Flatten images for ANN
        images_flattened = images.reshape(len(images), -1)
        
        # Encode labels
        labels_encoded = self.label_encoder.fit_transform(labels)
        
        # Split data
        X_train, X_temp, y_train, y_temp = train_test_split(
            images_flattened, labels_encoded, test_size=0.3, random_state=42, stratify=labels_encoded
        )
        
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
        )
        
        # Create output directories
        os.makedirs(os.path.join(self.output_path, 'train'), exist_ok=True)
        os.makedirs(os.path.join(self.output_path, 'valid'), exist_ok=True)
        os.makedirs(os.path.join(self.output_path, 'test'), exist_ok=True)
        
        # Save preprocessed data
        np.save(os.path.join(self.output_path, 'train', 'X_train.npy'), X_train)
        np.save(os.path.join(self.output_path, 'train', 'y_train.npy'), y_train)
        np.save(os.path.join(self.output_path, 'valid', 'X_val.npy'), X_val)
        np.save(os.path.join(self.output_path, 'valid', 'y_val.npy'), y_val)
        np.save(os.path.join(self.output_path, 'test', 'X_test.npy'), X_test)
        np.save(os.path.join(self.output_path, 'test', 'y_test.npy'), y_test)
        
        # Save label encoder
        with open(os.path.join(self.output_path, 'label_encoder.pkl'), 'wb') as f:
            pickle.dump(self.label_encoder, f)
        
        # Save class names
        class_names = self.label_encoder.classes_
        with open(os.path.join(self.output_path, 'class_names.txt'), 'w', encoding='utf-8') as f:
            for name in class_names:
                f.write(f"{name}\n")
        
        print("Data preprocessing completed!")
        print(f"Training set: {X_train.shape[0]} samples")
        print(f"Validation set: {X_val.shape[0]} samples")
        print(f"Test set: {X_test.shape[0]} samples")
        print(f"Classes: {list(class_names)}")

if __name__ == "__main__":
    # Configure paths
    RAW_DATA_PATH = "data/raw"
    OUTPUT_PATH = "data"
    
    preprocessor = PalmistryDataPreprocessor(RAW_DATA_PATH, OUTPUT_PATH)
    preprocessor.preprocess_data()