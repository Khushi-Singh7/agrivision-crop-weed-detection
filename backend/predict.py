
from pathlib import Path
from ultralytics import YOLO
from PIL import Image
import tempfile
import os


class CropWeedDetector:
    def __init__(self, model_path):
        self.model_path = str(model_path)

        if not Path(self.model_path).is_file():
            raise FileNotFoundError(
                f"Trained model not found: {self.model_path}"
            )

        self.model = YOLO(self.model_path)

    def predict(
        self,
        image,
        confidence=0.25,
        iou=0.50,
        image_size=640
    ):
        image = image.convert("RGB")

        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                suffix=".jpg", delete=False
            ) as temp:
                temp_path = temp.name

            image.save(temp_path, format="JPEG")

            results = self.model.predict(
                source=temp_path,
                conf=confidence,
                iou=iou,
                imgsz=image_size,
                verbose=False
            )

            result = results[0]

            # Ultralytics returns the plotted image in BGR order.
            annotated_array = result.plot()
            annotated_image = Image.fromarray(
                annotated_array[:, :, ::-1].copy()
            )

            detections = []

            if result.boxes is not None:
                for box in result.boxes:
                    class_id = int(box.cls.item())
                    class_name = self.model.names[class_id]
                    score = float(box.conf.item())

                    coords = [
                        round(float(v), 1)
                        for v in box.xyxy[0].tolist()
                    ]

                    detections.append({
                        "class": str(class_name),
                        "confidence": score,
                        "box": coords
                    })

            return annotated_image, detections

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
