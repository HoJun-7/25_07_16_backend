import os

# ✅ 삭제할 대상 디렉토리들 (상대경로 기준 또는 절대경로로 수정 가능)
TARGET_DIRS = [
    os.path.join("result", "disease_model", "masks"),
    os.path.join("result", "hygiene_model", "masks"),
    os.path.join("result", "original", "images"),
    os.path.join("result", "tooth_number", "masks")
]

# ✅ 삭제할 확장자 (이미지 파일 확장자들)
IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff']

def delete_images_from_folders():
    total_deleted = 0
    for folder in TARGET_DIRS:
        if not os.path.exists(folder):
            print(f"❌ 디렉토리 없음: {folder}")
            continue

        deleted_count = 0
        for filename in os.listdir(folder):
            if any(filename.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                file_path = os.path.join(folder, filename)
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"⚠️ 삭제 실패: {file_path} - {e}")
        print(f"✅ {folder} 에서 삭제된 이미지 수: {deleted_count}")
        total_deleted += deleted_count

    print(f"\n🗑️ 전체 삭제된 이미지 수: {total_deleted}")

if __name__ == "__main__":
    delete_images_from_folders()
