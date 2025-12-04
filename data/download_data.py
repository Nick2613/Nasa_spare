import os
from kaggle.api.kaggle_api_extended import KaggleApi

# CONFIG
DATASET = "behrad3d/nasa-cmaps"
TARGET_PATH = "data/"
FILE_NAME = "train_FD001.txt"

def download_data():
    print(f"⬇️ Attempting to download {DATASET}...")
    try:
        api = KaggleApi()
        api.authenticate()
        api.dataset_download_files(DATASET, path=TARGET_PATH, unzip=True)
        print(f"✅ Success! Data saved to {TARGET_PATH}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure 'kaggle.json' is in your root folder (auto-spare-parts-mlops/)")

if __name__ == "__main__":
    if not os.path.exists(os.path.join(TARGET_PATH, FILE_NAME)):
        download_data()
    else:
        print("✅ Data already exists.")