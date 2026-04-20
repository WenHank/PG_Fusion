import kagglehub
import shutil
import os

# 1. Define your project data path
# We use '..' if the script is inside the 'scripts/' folder
TARGET_DIR = os.path.join(os.getcwd(), "data")


def fetch_and_move_data():
    # Ensure the directory exists
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        print(f"Created directory: {TARGET_DIR}")

    # 2. Download from Kaggle
    print("Downloading dataset from Kaggle...")
    downloaded_path = kagglehub.dataset_download(
        "dillonmyrick/bike-store-sample-database"
    )

    print(f"Temporary path: {downloaded_path}")

    # 3. Move files to your local 'data' folder
    files = os.listdir(downloaded_path)
    for f in files:
        src_path = os.path.join(downloaded_path, f)
        dst_path = os.path.join(TARGET_DIR, f)

        # We use move (or copy) to get it into your project folder
        shutil.copy2(src_path, dst_path)
        print(f"Moved: {f} -> {TARGET_DIR}")

    print("\n✅ Success! All CSV files are now in your /data folder.")


if __name__ == "__main__":
    fetch_and_move_data()
