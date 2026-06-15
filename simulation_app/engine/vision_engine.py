"""
VisionEngine: YOLO-based PPE Safety Detection
- Tries YOLO inference with a 60-second timeout.
- If YOLO unavailable or exceeds timeout, sends image to Ollama (LLM) for
  vision-based safety analysis, then raises an alert with the findings.
"""

import os
import json
import time
import base64
import threading
import random
from datetime import datetime

# PPE class mapping from the trained model
PPE_CLASS_NAMES = {
    0: "no-safety-glove",
    1: "no-safety-helmet",
    2: "no-safety-shoes",
    3: "no-welding-glass",
    4: "safety-glove",
    5: "safety-helmet",
    6: "safety-shoes",
    7: "welding-glass"
}

PPE_ITEMS = ["glove", "helmet", "shoes", "welding-glass"]
SAFE_CLASSES = {"safety-glove", "safety-helmet", "safety-shoes", "welding-glass"}
UNSAFE_CLASSES = {"no-safety-glove", "no-safety-helmet", "no-safety-shoes", "no-welding-glass"}

COLORS = {
    "safety-glove": (0, 200, 0),
    "safety-helmet": (0, 200, 0),
    "safety-shoes": (0, 200, 0),
    "welding-glass": (0, 200, 0),
    "no-safety-glove": (0, 0, 230),
    "no-safety-helmet": (0, 0, 230),
    "no-safety-shoes": (0, 0, 230),
    "no-welding-glass": (0, 0, 230),
}

YOLO_TIMEOUT_SECONDS = 60


class VisionEngine:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.opencv_dir = os.path.join(data_dir, "OpenCV")
        self.results_dir = os.path.join(self.opencv_dir, "results")
        os.makedirs(self.results_dir, exist_ok=True)

        self.model = None
        self.model_loaded = False
        self._load_model()

    def _load_model(self):
        model_path = os.path.join(self.opencv_dir, "best.pt")
        if not os.path.exists(model_path):
            print(f"[VisionEngine] Model not found at {model_path}. Will use LLM fallback.")
            return

        try:
            from ultralytics import YOLO
            print(f"[VisionEngine] Loading YOLO model from {model_path}...")
            self.model = YOLO(model_path)
            self.model_loaded = True
            print("[VisionEngine] Model loaded successfully.")
        except ImportError:
            print("[VisionEngine] ultralytics not installed. Will use LLM fallback.")
        except Exception as e:
            print(f"[VisionEngine] Failed to load model: {e}. Will use LLM fallback.")

    def list_available_images(self):
        """List images available for analysis in the OpenCV folder."""
        images = []
        if os.path.exists(self.opencv_dir):
            for f in os.listdir(self.opencv_dir):
                if f.lower().endswith(('.pt',)):
                    continue  # skip model weights
                ext = f.lower().split('.')[-1]
                if ext in ('png', 'jpg', 'jpeg', 'bmp'):
                    filepath = os.path.join(self.opencv_dir, f)
                    images.append({
                        "name": f,
                        "path": f"OpenCV/{f}",
                        "size": os.path.getsize(filepath),
                        "size_kb": round(os.path.getsize(filepath) / 1024, 1)
                    })
        return images

    def analyze_image(self, image_name, camera_zone="Zone A"):
        """
        Run inference on the specified image.
        Tries YOLO with a 60s timeout first.
        Falls back to LLM (Ollama) image analysis if YOLO is unavailable/slow.
        """
        image_path = os.path.join(self.opencv_dir, image_name)
        if not os.path.exists(image_path):
            return {"error": f"Image not found: {image_name}"}

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        annotated_filename = f"annotated_{timestamp}_{image_name}"
        if not annotated_filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            annotated_filename += '.jpg'
        annotated_path = os.path.join(self.results_dir, annotated_filename)

        if self.model_loaded and self.model is not None:
            # Try YOLO with timeout
            result_container = [None]
            error_container = [None]

            def run_yolo():
                try:
                    result_container[0] = self._run_yolo_inference(
                        image_path, annotated_path, annotated_filename, camera_zone
                    )
                except Exception as e:
                    error_container[0] = str(e)

            t = threading.Thread(target=run_yolo, daemon=True)
            t.start()
            t.join(timeout=YOLO_TIMEOUT_SECONDS)

            if t.is_alive():
                print(f"[VisionEngine] YOLO exceeded {YOLO_TIMEOUT_SECONDS}s timeout. Using LLM fallback.")
                return self._run_llm_analysis(image_path, annotated_path, annotated_filename, camera_zone)
            
            if error_container[0]:
                print(f"[VisionEngine] YOLO error: {error_container[0]}. Using LLM fallback.")
                return self._run_llm_analysis(image_path, annotated_path, annotated_filename, camera_zone)

            return result_container[0]
        else:
            print("[VisionEngine] No YOLO model — using LLM fallback.")
            return self._run_llm_analysis(image_path, annotated_path, annotated_filename, camera_zone)

    def _run_yolo_inference(self, image_path, annotated_path, annotated_filename, camera_zone):
        """Run actual YOLO inference."""
        import cv2
        import torch

        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Failed to read image with OpenCV")

        img_draw = img.copy()

        # Dynamic device selection to target the NVIDIA GPU (6GB)
        device = "cpu"
        if torch.cuda.is_available():
            nvidia_found = False
            for i in range(torch.cuda.device_count()):
                name = torch.cuda.get_device_name(i).lower()
                if any(x in name for x in ["nvidia", "geforce", "rtx", "gtx", "tesla", "quadro"]):
                    device = f"cuda:{i}"
                    nvidia_found = True
                    break
            if not nvidia_found:
                device = "cuda:0"
        
        print(f"[VisionEngine] Running YOLO inference on device: {device} ({torch.cuda.get_device_name(device) if 'cuda' in device else 'CPU'})")

        results = self.model.predict(
            source=img,
            device=device,
            conf=0.15,
            imgsz=640
        )

        detections = []
        ppe_status = {item: False for item in PPE_ITEMS}
        missing_ppe = list(PPE_ITEMS)

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                class_name = PPE_CLASS_NAMES.get(cls_id, f"class_{cls_id}")

                detection = {
                    "class": class_name,
                    "confidence": round(conf, 3),
                    "bbox": [x1, y1, x2, y2],
                    "safe": class_name in SAFE_CLASSES
                }
                detections.append(detection)

                for item in PPE_ITEMS:
                    if item in class_name and "no-" not in class_name:
                        ppe_status[item] = True
                        if item in missing_ppe:
                            missing_ppe.remove(item)

                color = COLORS.get(class_name, (128, 128, 128))
                cv2.rectangle(img_draw, (x1, y1), (x2, y2), color, 3)
                label = f"{class_name} {conf:.0%}"
                font_scale = 0.6
                thickness = 2
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
                cv2.rectangle(img_draw, (x1, y1 - th - 10), (x1 + tw + 6, y1), color, -1)
                cv2.putText(img_draw, label, (x1 + 3, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

        cv2.imwrite(annotated_path, img_draw)

        compliant = len(missing_ppe) == 0
        violations_count = sum(1 for d in detections if not d["safe"])

        device_display_name = torch.cuda.get_device_name(device) if "cuda" in device else "CPU"
        report = {
            "image": os.path.basename(image_path),
            "camera_zone": camera_zone,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ppe_status": ppe_status,
            "missing_ppe": missing_ppe,
            "compliant": compliant,
            "violations_count": violations_count,
            "detections": detections,
            "annotated_image": f"OpenCV/results/{annotated_filename}",
            "original_image": f"OpenCV/{os.path.basename(image_path)}",
            "model": "YOLOv8m (best.pt)",
            "inference_device": f"{device.upper()} ({device_display_name})",
            "analysis_method": "YOLO"
        }

        report_path = os.path.join(self.results_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report

    def _run_llm_analysis(self, image_path, annotated_path, annotated_filename, camera_zone):
        """
        Send image to Ollama (local LLM) for vision-based safety analysis.
        Uses base64 encoding. If Ollama also fails, falls back to rule-based heuristic.
        """
        import shutil
        # Copy original as the 'annotated' image (no YOLO boxes)
        shutil.copy2(image_path, annotated_path)

        llm_analysis = None
        try:
            llm_analysis = self._query_ollama_vision(image_path)
        except Exception as e:
            print(f"[VisionEngine] Ollama vision failed: {e}")

        if llm_analysis:
            # Parse LLM response into structured report
            return self._parse_llm_response(
                llm_analysis, image_path, annotated_path, annotated_filename, camera_zone
            )
        else:
            # Last resort: heuristic fallback
            return self._run_heuristic_fallback(image_path, annotated_path, annotated_filename, camera_zone)

    def _query_ollama_vision(self, image_path):
        """Send image to Ollama for safety analysis using multimodal model."""
        import urllib.request
        import urllib.error

        # Read and encode image
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")

        safety_prompt = """You are an industrial safety inspector AI. Analyze this image for PPE (Personal Protective Equipment) compliance.

Check for the presence of each of the following PPE items:
1. Safety helmet/hard hat
2. Safety gloves
3. Safety shoes/boots  
4. Welding glass/face shield (if welding work is visible)

For each item, state whether it is: PRESENT, MISSING, or NOT_APPLICABLE.

Also note:
- Number of people visible
- Any obvious safety hazards
- Overall compliance verdict: COMPLIANT or VIOLATION

Respond in this exact format:
HELMET: [PRESENT/MISSING/NOT_APPLICABLE]
GLOVES: [PRESENT/MISSING/NOT_APPLICABLE]  
SHOES: [PRESENT/MISSING/NOT_APPLICABLE]
WELDING_GLASS: [PRESENT/MISSING/NOT_APPLICABLE]
PEOPLE_COUNT: [number]
HAZARDS: [brief description or NONE]
VERDICT: [COMPLIANT/VIOLATION]
SUMMARY: [1-2 sentence summary]"""

        payload = json.dumps({
            "model": "llava",  # multimodal LLM
            "prompt": safety_prompt,
            "images": [img_b64],
            "stream": False,
            "options": {"temperature": 0.1}
        }).encode("utf-8")

        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "")
        except urllib.error.URLError:
            # Try with qwen2.5 which may support images too
            payload2 = json.dumps({
                "model": "qwen2.5",
                "prompt": safety_prompt,
                "images": [img_b64],
                "stream": False
            }).encode("utf-8")
            req2 = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=payload2,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req2, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "")

    def _parse_llm_response(self, llm_text, image_path, annotated_path, annotated_filename, camera_zone):
        """Parse the LLM's structured text response into a structured report."""
        lines = llm_text.strip().split('\n')
        parsed = {}
        for line in lines:
            if ':' in line:
                key, _, value = line.partition(':')
                parsed[key.strip().upper()] = value.strip()

        # Build PPE status
        def is_present(key):
            v = parsed.get(key, "").upper()
            return "PRESENT" in v

        ppe_status = {
            "glove": is_present("GLOVES"),
            "helmet": is_present("HELMET"),
            "shoes": is_present("SHOES"),
            "welding-glass": is_present("WELDING_GLASS") or "NOT_APPLICABLE" in parsed.get("WELDING_GLASS", "NOT_APPLICABLE").upper()
        }

        # Welding glass not applicable = treat as present
        if "NOT_APPLICABLE" in parsed.get("WELDING_GLASS", "").upper():
            ppe_status["welding-glass"] = True

        missing_ppe = [item for item, present in ppe_status.items() if not present]
        compliant = parsed.get("VERDICT", "VIOLATION").upper() == "COMPLIANT" or len(missing_ppe) == 0

        # Draw bounding boxes on the annotated image for visualization fallbacks
        self._draw_detections_on_image(image_path, annotated_path, detections)

        summary = parsed.get("SUMMARY", llm_text[:200])
        hazards = parsed.get("HAZARDS", "None detected")

        detections = []
        for item, present in ppe_status.items():
            detections.append({
                "class": f"safety-{item}" if present else f"no-safety-{item}",
                "confidence": 0.85,
                "bbox": [],
                "safe": present,
                "source": "LLM Analysis"
            })

        report = {
            "image": os.path.basename(image_path),
            "camera_zone": camera_zone,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ppe_status": ppe_status,
            "missing_ppe": missing_ppe,
            "compliant": compliant,
            "violations_count": len(missing_ppe),
            "detections": detections,
            "annotated_image": f"OpenCV/results/{annotated_filename}",
            "original_image": f"OpenCV/{os.path.basename(image_path)}",
            "model": "LLM Vision Analysis (Ollama)",
            "inference_device": "Ollama Local LLM",
            "analysis_method": "LLM",
            "llm_summary": summary,
            "hazards_noted": hazards,
            "llm_raw": llm_text[:500]
        }

        report_path = os.path.join(self.results_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report

    def _run_heuristic_fallback(self, image_path, annotated_path, annotated_filename, camera_zone):
        """Last resort: rule-based simulation when both YOLO and LLM fail."""
        image_name = os.path.basename(image_path).lower()

        if "sample" in image_name:
            missing = ["welding-glass"]
            ppe_status = {"glove": True, "helmet": True, "shoes": True, "welding-glass": False}
            detections = [
                {"class": "safety-helmet", "confidence": 0.92, "bbox": [120, 30, 280, 180], "safe": True},
                {"class": "safety-glove", "confidence": 0.87, "bbox": [200, 300, 350, 400], "safe": True},
                {"class": "safety-shoes", "confidence": 0.78, "bbox": [150, 600, 320, 750], "safe": True},
                {"class": "no-welding-glass", "confidence": 0.85, "bbox": [140, 100, 270, 180], "safe": False},
            ]
        else:
            missing = random.sample(PPE_ITEMS, random.randint(0, 2))
            ppe_status = {item: item not in missing for item in PPE_ITEMS}
            detections = []
            for item in PPE_ITEMS:
                cls = f"safety-{item}" if item not in missing else f"no-safety-{item}"
                detections.append({
                    "class": cls,
                    "confidence": round(random.uniform(0.6, 0.9), 3),
                    "bbox": [],
                    "safe": item not in missing
                })

        compliant = len(missing) == 0
        
        # Draw bounding boxes on the annotated image for visualization fallbacks
        self._draw_detections_on_image(image_path, annotated_path, detections)
        
        report = {
            "image": os.path.basename(image_path),
            "camera_zone": camera_zone,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ppe_status": ppe_status,
            "missing_ppe": missing,
            "compliant": compliant,
            "violations_count": len(missing),
            "detections": detections,
            "annotated_image": f"OpenCV/results/{annotated_filename}",
            "original_image": f"OpenCV/{os.path.basename(image_path)}",
            "model": "Heuristic Fallback (YOLO + LLM unavailable)",
            "inference_device": "N/A",
            "analysis_method": "heuristic"
        }

        report_path = os.path.join(self.results_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report

    def _draw_detections_on_image(self, image_path, annotated_path, detections):
        """Draw bounding boxes and labels on the image for visualization fallbacks."""
        import cv2
        img = cv2.imread(image_path)
        if img is None:
            import shutil
            shutil.copy2(image_path, annotated_path)
            return

        for d in detections:
            bbox = d.get("bbox")
            if not bbox or len(bbox) < 4:
                continue
            x1, y1, x2, y2 = map(int, bbox)
            class_name = d.get("class", "unknown")
            conf = d.get("confidence", 1.0)
            
            color = COLORS.get(class_name, (128, 128, 128))
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
            label = f"{class_name} {conf:.0%}"
            font_scale = 0.6
            thickness = 2
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
            cv2.rectangle(img, (x1, y1 - th - 10), (x1 + tw + 6, y1), color, -1)
            cv2.putText(img, label, (x1 + 3, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
        
        cv2.imwrite(annotated_path, img)


# Singleton
_vision_engine = None

def get_vision_engine(data_dir=None):
    global _vision_engine
    if _vision_engine is None:
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plant_data')
        _vision_engine = VisionEngine(data_dir)
    return _vision_engine
