import os
import urllib.request
import zipfile
from pathlib import Path


def download_file(url: str, dest: str):
    print(f"Downloading {url}...")
    urllib.request.urlretrieve(url, dest)
    print(f"Downloaded to {dest}")


def extract_zip(zip_path: str, extract_to: str):
    print(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Extracted to {extract_to}")
    os.remove(zip_path)
    print(f"Removed {zip_path}")


def download_yolo_model():
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    
    print("YOLOv8 models are automatically downloaded by ultralytics library.")
    print("The first time you run the application, it will download the model.")
    print("Model will be saved to your home directory under .ultralytics/")


def download_vosk_model():
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    
    vosk_model_path = model_dir / "vosk-model-small-en-us-0.15"
    
    if vosk_model_path.exists():
        print(f"Vosk model already exists at {vosk_model_path}")
        return
    
    print("Downloading Vosk wake word model...")
    model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    zip_path = model_dir / "vosk-model-small-en-us-0.15.zip"
    
    try:
        download_file(model_url, str(zip_path))
        extract_zip(str(zip_path), str(model_dir))
        print("Vosk model downloaded successfully!")
    except Exception as e:
        print(f"Error downloading Vosk model: {e}")
        print("You can download it manually from: https://alphacephei.com/vosk/models/")
        print("Extract it to models/vosk-model-small-en-us-0.15/")


if __name__ == "__main__":
    print("=== AURA Model Download Script ===")
    print()
    
    download_yolo_model()
    print()
    download_vosk_model()
    
    print()
    print("Model download complete!")
    print("Note: YOLOv8 model will be downloaded automatically on first use.")

