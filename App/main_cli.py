import os
import argparse
import cv2
from tqdm import tqdm
from detector import SensitiveDetector
from processor import ImageProcessor

def process_images(input_dir, output_dir, threshold=0.1, exclude=None):
    """
    フォルダ内の画像を順次スキャンし、センシティブな部位にモザイクをかける。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    detector = SensitiveDetector(threshold=threshold, exclude_keywords=exclude)
    processor = ImageProcessor()

    # 画像ファイルのリストを取得
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(valid_extensions)]

    print(f"Began processing {len(image_files)} images...")

    for filename in tqdm(image_files, desc="Processing"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        # 検出
        boxes = detector.detect(input_path)

        if boxes:
            print(f"\n[Detected] {filename}: {len(boxes)} sensitive regions found.")
            img = cv2.imread(input_path)
            if img is None: continue

            for box in boxes:
                x, y, w, h = map(int, box)
                print(f"  - Applying mosaic at: x={x}, y={y}, w={w}, h={h}")
                img = processor.apply_mosaic(img, x, y, w, h)
            
            cv2.imwrite(output_path, img)
        else:
            # 検出されなかった場合はそのまま保存
            img = cv2.imread(input_path)
            if img is not None:
                cv2.imwrite(output_path, img)

    print(f"Finished. Results are saved in: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AutoMosaic CLI Tool")
    parser.add_argument("--input", "-i", type=str, required=True, help="Input directory containing images")
    parser.add_argument("--output", "-o", type=str, required=True, help="Output directory for processed images")
    parser.add_argument("--threshold", "-t", type=float, default=0.2, help="Detection threshold (0.0 to 1.0)")
    parser.add_argument("--exclude", "-e", type=str, nargs='*', help="Keywords to exclude from mosaic (e.g. BREAST)")

    args = parser.parse_args()
    process_images(args.input, args.output, args.threshold, args.exclude)
