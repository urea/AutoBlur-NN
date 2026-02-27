from nudenet import NudeDetector

class SensitiveDetector:
    def __init__(self, threshold=0.1, exclude_keywords=None):
        self.detector = NudeDetector()
        self.threshold = threshold
        # 検出対象とするキーワード（性器関連に特化）
        self.sensitive_keywords = [
            "GENITALIA",
            "VAGINA",
            "PENIS",
            "ANUS",
        ]
        self.exclude_keywords = exclude_keywords if exclude_keywords else []

    def detect(self, image_path):
        """
        画像からセンシティブな部位を検出し、その座標(box)のリストを返す。
        日本語パス対応のため、完全に英数字のみの一時ファイル経由で処理する。
        """
        import os
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()
        ext = os.path.splitext(image_path)[1]
        temp_img_path = os.path.join(temp_dir, f"detect_img{ext}")
        
        try:
            # 元画像を一時ファイルへコピー（パスが日本語でもこれなら通る）
            shutil.copy2(image_path, temp_img_path)
            # NudeNetには一時パス（英数字のみ）を渡す
            results = self.detector.detect(temp_img_path)
        except Exception as e:
            print(f"Detection Error: {e}")
            results = None
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

        sensitive_boxes = []
        if results is None:
            return []
        
        for res in results:
            label = res['label'] if 'label' in res else res.get('class', "")
            score = res['score']
            
            if score >= self.threshold:
                # 1. 除外キーワードのいずれかが含まれているかチェック
                if any(ex.lower() in label.lower() for ex in self.exclude_keywords):
                    continue

                # 2. センシティブキーワードのいずれかが含まれているかチェック
                is_sensitive = any(kw.lower() in label.lower() for kw in self.sensitive_keywords)
                
                # 3. 特定の固定除外（お腹、顔、足、脇などはセンシティブ部位とみなさない）
                exclude_list = ["FACE", "COVERED", "BELLY", "FEET", "ARMPIT"]
                if any(ex in label.upper() for ex in exclude_list):
                    is_sensitive = False
                
                if is_sensitive:
                    sensitive_boxes.append(res['box'])
        
        return sensitive_boxes
