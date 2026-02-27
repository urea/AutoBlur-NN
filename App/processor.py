import cv2
import numpy as np

class ImageProcessor:
    @staticmethod
    def apply_mosaic(image, x, y, w, h, size=15, scale=1.0):
        """
        指定された矩形範囲に楕円形のモザイクを適用し、境界をぼかす。
        """
        if scale < 1.0:
            new_w = int(w * scale)
            new_h = int(h * scale)
            x = x + (w - new_w) // 2
            y = y + (h - new_h) // 2
            w, h = new_w, new_h

        h_img, w_img = image.shape[:2]
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(w_img, x + w), min(h_img, y + h)

        if x1 >= x2 or y1 >= y2: return image

        # 1. モザイク済みの領域を作成
        roi = image[y1:y2, x1:x2].copy()
        rw, rh = x2 - x1, y2 - y1
        roi_small = cv2.resize(roi, (max(1, rw // size), max(1, rh // size)), interpolation=cv2.INTER_LINEAR)
        roi_mosaic = cv2.resize(roi_small, (rw, rh), interpolation=cv2.INTER_NEAREST)

        # 2. 楕円マスクの作成（フェザー付き）
        mask = np.zeros((rh, rw), dtype=np.float32)
        cv2.ellipse(mask, (rw // 2, rh // 2), (rw // 2, rh // 2), 0, 0, 360, 1.0, -1)
        mask = cv2.GaussianBlur(mask, (15, 15), 0) # 境界をぼかす

        # 3. 合成
        for c in range(3):
            image[y1:y2, x1:x2, c] = image[y1:y2, x1:x2, c] * (1 - mask) + roi_mosaic[:, :, c] * mask
        
        return image

    @staticmethod
    def apply_blur(image, x, y, w, h, strength=51, scale=1.0):
        """
        指定された矩形範囲に楕円形のぼかしを適用し、境界をぼかす。
        """
        if scale < 1.0:
            new_w = int(w * scale)
            new_h = int(h * scale)
            x = x + (w - new_w) // 2
            y = y + (h - new_h) // 2
            w, h = new_w, new_h

        h_img, w_img = image.shape[:2]
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(w_img, x + w), min(h_img, y + h)

        if x1 >= x2 or y1 >= y2: return image

        # 1. ぼかし済みの領域を作成
        roi = image[y1:y2, x1:x2].copy()
        rw, rh = x2 - x1, y2 - y1
        if strength % 2 == 0: strength += 1
        roi_blur = cv2.GaussianBlur(roi, (strength, strength), 0)

        # 2. 楕円マスクの作成（フェザー付き）
        mask = np.zeros((rh, rw), dtype=np.float32)
        cv2.ellipse(mask, (rw // 2, rh // 2), (rw // 2, rh // 2), 0, 0, 360, 1.0, -1)
        mask = cv2.GaussianBlur(mask, (15, 15), 0)

        # 3. 合成
        for c in range(3):
            image[y1:y2, x1:x2, c] = image[y1:y2, x1:x2, c] * (1 - mask) + roi_blur[:, :, c] * mask
            
        return image
