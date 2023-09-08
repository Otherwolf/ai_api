from typing import List, Optional

import torch
from PIL import Image
import tensorflow as tf

from transformers import CLIPProcessor, CLIPModel


DEFAULT_MODEL_NAME = 'openai/clip-vit-base-patch32'


class ClassificatorModel:
    def __init__(self, device: Optional[str], model_name: Optional[str] = DEFAULT_MODEL_NAME):
        self.model_name = model_name or DEFAULT_MODEL_NAME
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.model = CLIPModel.from_pretrained(self.model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(self.model_name)

    def predict(self, file_path: str, labels: List[str]):
        image = Image.open(file_path)

        inputs = self.processor(text=labels, images=image, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        logits_per_image = outputs.logits_per_image  # this is the image-text similarity score
        probs = logits_per_image.softmax(dim=1)  # we can take the softmax to get the label probabilities
        result = self._prepare_probs(probs, labels)
        return result

    @staticmethod
    def _prepare_probs(params, categories: list):
        probs = []
        for i, single_preds in enumerate(params):
            single_probs = {}
            for j, pred in enumerate(single_preds):
                single_probs[categories[j]] = round(float(pred), 6) * 100
            probs.append(single_probs)
        return probs
