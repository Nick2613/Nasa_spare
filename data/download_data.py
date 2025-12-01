import os
import zipfile
from kaggle.api.kaggle_api_extended import KaggleApi

# Configuration
DATASET_SLUG = "behrad3d/nasa-cmaps" # The ID of the dataset on Kaggle
DOWNLOAD_PATH = "data/"
TARGET_FILE = "train_FD001.txt"

def setup_kaggle_auth():
    """
    Moves kaggle.json to the correct location so the API can find it.
    """
    kaggle_json_path = "kaggle.json"
    
    # Check if user uploaded kaggle.json to root
    if os.path.exists(kaggle_json_path):
        print("🔑 Found kaggle.json. Setting up authentication...")
        
        # Create the .kaggle directory which the API expects
        home = os.path.expanduser("~")
        kaggle_dir = os.path.join(home, ".kaggle")
        if not os.path.exists(kaggle_dir):
            os.makedirs(kaggle_dir)
            
        # Move the file there
        destination = os.path.join(kaggle_dir, "kaggle.json")
        # We read and write instead of move to avoid cross-device link errors
        with open(kaggle_json_path, 'r') as f:
            data = f.read()
        with open(destination, 'w') as f:
            f.write(data)
            
        # Set permissions (required by Kaggle)
        os.chmod(destination, 0o600)
        print("✅ Authentication setup complete.")
        return True
    
    # Check if environment variables are set (Alternative method)
    elif os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
        print("🔑 Found Environment Variables. Authentication ready.")
        return True
        
    else:
        print("❌ ERROR: 'kaggle.json' not found in root folder.")
        print("Please download it from Kaggle Settings -> Create New Token")
        print("And upload it to your project folder.")
        return False

def download_and_extract():
    api = KaggleApi()
    api.authenticate()

    print(f"⬇️  Downloading dataset: {DATASET_SLUG}...")
    try:
        api.dataset_download_files(DATASET_SLUG, path=DOWNLOAD_PATH, unzip=True)
        print("✅ Download and extraction complete.")
        
        # Verification
        if os.path.exists(os.path.join(DOWNLOAD_PATH, TARGET_FILE)):
            print(f"🎉 Success! {TARGET_FILE} is ready for use.")
        else:
            print(f"⚠️ Warning: Dataset downloaded, but {TARGET_FILE} not found. Check the folder.")
            
    except Exception as e:
        print(f"❌ Failed to download: {e}")

if __name__ == "__main__":
    if setup_kaggle_auth():
        download_and_extract()