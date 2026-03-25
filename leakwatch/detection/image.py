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
        if not self.config.enable_ocr or EasyOcrReader is None:
            return []
        if self._ocr_reader is None:
            self._ocr_reader = EasyOcrReader(list(self.config.text_detection_langs), gpu=False)

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        detections = self._ocr_reader.readtext(rgb_image)
        results: list[DetectedEntity] = []
        for bbox_points, text, confidence in detections:
            if confidence < self.config.min_confidence:
                continue
            bbox = self._bbox_from_points(bbox_points)
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
            elif self._looks_sensitive(text):
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

    def _looks_sensitive(self, text: str) -> bool:
        import re
        text = text.strip()
        if not text:
            return False

        lower_t = text.lower()
        # Non-sensitive categories
        safe_labels = {
            "name", "dob", "address", "blood group", "date of issue",
            "date of expiry", "license no.", "license no", "app store",
            "driving license", "government of india", "verified by digilocker",
            "tap to zoom", "present address", "permanent address",
            "authorization", "to drive", "s/w/d"
        }
        
        if lower_t in safe_labels:
            return False
            
        # Short uppercase text (e.g., LMV, MCWG)
        if len(text) <= 8 and text.isupper() and text.isalpha():
            return False

        # Titles and common words - very short text
        if len(text) < 4 and text.isalpha():
            return False

        # Date pattern: YYYY-MM-DD, DD/MM/YYYY
        if re.search(r'\b\d{2,4}[-/]\d{2}[-/]\d{2,4}\b', text):
            return True

        # Alphanumeric identifiers (ID-like): contains digits + letters
        digits = sum(c.isdigit() for c in text)
        alphas = sum(c.isalpha() for c in text)
        if digits >= 2 and alphas >= 1 and len(text) >= 6:
            return True

        # Phone / ID numbers: lots of digits
        if digits >= 6:
            return True

        # Long text (address-like)
        if len(text) > 15 and ' ' in text:
            return True

        # Name-like pattern (Title Case or UPPERCASE 2+ words)
        words = text.split()
        if len(words) >= 2:
            if all(w.istitle() or w.isupper() for w in words if w.isalpha()):
                return True

        return False

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
