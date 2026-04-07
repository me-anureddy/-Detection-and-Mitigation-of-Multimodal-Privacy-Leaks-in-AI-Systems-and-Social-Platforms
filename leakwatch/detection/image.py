"""Image privacy detection module."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence, Tuple, TYPE_CHECKING

import cv2
import numpy as np

try:  # EasyOCR is optional; the code degrades gracefully without it.
    import easyocr
except ImportError:  # pragma: no cover
    easyocr = None

from ..utils.config import ImageConfig
from ..utils.types import BoundingBox, DetectedEntity, Modality

if TYPE_CHECKING:  # pragma: no cover
    from .text import TextDetector

if easyocr:
    EasyOcrReader = easyocr.Reader
else:  # pragma: no cover
    EasyOcrReader = None  # type: ignore


class ImageDetector:
    """Detect faces and sensitive text regions inside images."""

    def __init__(
        self,
        config: ImageConfig,
        text_labels: Sequence[str] | None = None,
        text_detector: "TextDetector | None" = None,
    ) -> None:
        self.config = config
        self.text_labels = tuple(text_labels or ("scene_text",))
        self._text_detector = text_detector
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self._face_cascade = cv2.CascadeClassifier(cascade_path)
        self._ocr_reader = None

    def detect(self, path: Path) -> List[DetectedEntity]:
        image = cv2.imread(str(path))
        if image is None:
            raise FileNotFoundError(f"Unable to load image: {path}")

        entities: list[DetectedEntity] = []
        entities.extend(self._detect_faces(image))
        entities.extend(self._detect_text(image))
        return entities

    # --- Internal helpers --------------------------------------------
    def _detect_faces(self, image: np.ndarray) -> Iterable[DetectedEntity]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        for (x, y, w, h) in faces:
            yield DetectedEntity(
                modality=Modality.IMAGE,
                label="face",
                confidence=0.9,
                bbox=BoundingBox(x=int(x), y=int(y), width=int(w), height=int(h)),
                mitigation="blur",
            )

    def _detect_text(self, image: np.ndarray) -> Iterable[DetectedEntity]:
        results: list[DetectedEntity] = []

        # 1. QR Code
        results.extend(self._detect_qr(image))

        if not self.config.enable_ocr or EasyOcrReader is None:
            return results
            
        if self._ocr_reader is None:
            self._ocr_reader = EasyOcrReader(list(self.config.text_detection_langs), gpu=False)

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        raw_detections = self._ocr_reader.readtext(rgb_image)
        
        boxes = []
        for bbox_points, text, confidence in raw_detections:
            if confidence < self.config.min_confidence:
                continue
            xs = [p[0] for p in bbox_points]
            ys = [p[1] for p in bbox_points]
            boxes.append({
                'pts': bbox_points,
                'text': text.strip(),
                'conf': confidence,
                'x_min': min(xs),
                'x_max': max(xs),
                'y_min': min(ys),
                'y_max': max(ys)
            })

        # 1. Sort OCR detections left-to-right
        boxes.sort(key=lambda b: (b['y_min'] // 15, b['x_min']))

        # 2. Merge nearby numeric text blocks
        merged_detections = []
        i = 0
        while i < len(boxes):
            curr = boxes[i]
            
            def is_numeric(s):
                d = sum(c.isdigit() for c in s)
                return d > 0 and d / max(len(s.replace(" ", "")), 1) > 0.5

            if is_numeric(curr['text']):
                merged_text = curr['text']
                merged_pts = list(curr['pts'])
                merged_conf = curr['conf']
                last_box = curr
                j = i + 1
                while j < len(boxes):
                    nxt = boxes[j]
                    same_line = abs(last_box['y_min'] - nxt['y_min']) < 25
                    close_x = (nxt['x_min'] - last_box['x_max']) < 80
                    if same_line and close_x and is_numeric(nxt['text']):
                        # 3. Combine into single string
                        merged_text += " " + nxt['text']
                        merged_pts.extend(nxt['pts'])
                        merged_conf = min(merged_conf, nxt['conf'])
                        last_box = nxt
                        j += 1
                    else:
                        break
                
                merged_detections.append({
                    'pts': merged_pts,
                    'text': merged_text,
                    'conf': merged_conf
                })
                i = j
            else:
                merged_detections.append({
                    'pts': curr['pts'],
                    'text': curr['text'],
                    'conf': curr['conf']
                })
                i += 1

        mark_next_sensitive = False

        for item in merged_detections:
            bbox_points = item['pts']
            text = item['text']
            confidence = item['conf']
            bbox = self._bbox_from_points(bbox_points)

            if self._is_safe_text(text):
                mark_next_sensitive = False
                continue

            # 3. MRZ Detection
            if self._is_mrz(text):
                results.append(self._create_entity(text, float(confidence), bbox))
                mark_next_sensitive = False
                continue

            # 4. NER Detection (spaCy)
            nested_entities = self._text_detector.detect(text) if self._text_detector else []
            if nested_entities:
                for nested in nested_entities:
                    results.append(
                        nested.model_copy(
                            update={
                                "modality": Modality.IMAGE,
                                "bbox": bbox,
                                "confidence": float(confidence),
                            }
                        )
                    )
<<<<<<< Updated upstream
            else:
                results.append(
                    DetectedEntity(
                        modality=Modality.IMAGE,
                        label=self.text_labels[0],
                        confidence=float(confidence),
                        text=text,
                        bbox=bbox,
                        mitigation="blur",
                    )
                )
        return results

=======
                mark_next_sensitive = False
                continue

            # 5. Regex / Pattern Detection
            if self._looks_sensitive(text):
                results.append(self._create_entity(text, float(confidence), bbox))
                mark_next_sensitive = False
                continue

            # 6. Layout Detection
            if self._is_label(text):
                mark_next_sensitive = True
                continue

            if mark_next_sensitive:
                results.append(self._create_entity(text, float(confidence), bbox))
                mark_next_sensitive = False
                continue

        return results

    def _create_entity(self, text: str, confidence: float, bbox: BoundingBox) -> DetectedEntity:
        return DetectedEntity(
            modality=Modality.IMAGE,
            label=self.text_labels[0],
            confidence=confidence,
            text=text,
            bbox=bbox,
            mitigation="blur",
        )

    def _detect_qr(self, image: np.ndarray) -> List[DetectedEntity]:
        detector = cv2.QRCodeDetector()
        entities = []
        try:
            retval, decoded_info, points, _ = detector.detectAndDecodeMulti(image)
            if points is not None:
                for box_pts in points:
                    entities.append(
                        DetectedEntity(
                            modality=Modality.IMAGE,
                            label="qr_code",
                            confidence=0.99,
                            text="qr_code",
                            bbox=self._bbox_from_points(box_pts),
                            mitigation="blur",
                        )
                    )
        except Exception:
            pass
        return entities

    def _is_mrz(self, text: str) -> bool:
        if "<" not in text:
            return False
        letters = sum(c.isalpha() and c.isupper() for c in text)
        brackets = sum(c == '<' for c in text)
        digits = sum(c.isdigit() for c in text)
        total = letters + brackets + digits
        return total > 15 and brackets >= 2

    def _split_inline_label(self, text: str) -> bool:
        if ":" in text:
            parts = text.split(":", 1)
            lbl = parts[0].strip()
            if self._is_label(lbl) or len(lbl) < 15:
                return len(parts[1].strip()) > 0
        return False

    def _is_label(self, text: str) -> bool:
        t = text.strip()
        if len(t) >= 30:
            return False
        if any(c.isdigit() for c in t):
            return False
        if t.endswith(":"):
            return True
        known_labels = {
            "name", "father", "mother", "husband", "wife", "dob", "address", 
            "gender", "blood group", "issue date", "expiry date", "license no", 
            "id no", "passport no", "pan", "aadhar", "date of birth", "surname", "given name"
        }
        if t.lower() in known_labels:
            return True
        if len(t.split()) == 1 and (t.isupper() or t.istitle()) and len(t) < 15:
            pass
        return False

    def _is_safe_text(self, text: str) -> bool:
        lower_t = text.strip().lower()
        safe_exact = {
            "name", "dob", "address", "gender", "blood group", "date of issue",
            "date of expiry", "license no.", "license no", "app store",
            "driving license", "government of india", "verified by digilocker",
            "tap to zoom", "present address", "permanent address",
            "authorization", "to drive", "s/w/d", "signature"
        }
        if lower_t in safe_exact:
            return True
        if "aadhaar" in lower_t and len(lower_t.split()) < 4:
            return True
        return False

    def _looks_sensitive(self, text: str) -> bool:
        import re
        text = text.strip()
        if not text:
            return False

        if len(text) <= 8 and text.isalpha():
            return False
        if len(text) < 4 and text.isalpha():
            return False

        # Aadhaar Number Regex
        if re.search(r"\b\d{4}\s?\d{4}\s?\d{4}\b", text):
            return True
        if re.search(r"\b\d{12}\b", text):
            return True

        if re.search(r'\b\d{2,4}[-/]\d{2}[-/]\d{2,4}\b', text):
            return True

        digits = sum(c.isdigit() for c in text)
        alphas = sum(c.isalpha() for c in text)
        if digits >= 2 and alphas >= 1 and len(text) >= 6:
            return True
        if digits >= 6:
            return True

        if "@" in text and "." in text:
            return True

        if len(text) > 15 and ' ' in text and any(c.isdigit() for c in text):
            return True

        words = text.split()
        if len(words) >= 2:
            if all((w.istitle() or w.isupper()) for w in words if w.isalpha()):
                return True

        return False

>>>>>>> Stashed changes
    @staticmethod
    def _bbox_from_points(points: Sequence[Tuple[float, float]]) -> BoundingBox:
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        return BoundingBox(
            x=int(x_min),
            y=int(y_min),
            width=int(x_max - x_min),
            height=int(y_max - y_min),
        )
