from typing import List

from PIL import Image

from transformers import CLIPProcessor, CLIPModel


class ClassificatorModel:
    def __init__(self):
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def predict(self, file_path: str, labels: List[str]):
        image = Image.open(file_path)

        inputs = self.processor(text=labels, images=image, return_tensors="pt", padding=True)

        outputs = self.model(**inputs)
        logits_per_image = outputs.logits_per_image  # this is the image-text similarity score
        probs = logits_per_image.softmax(dim=1)  # we can take the softmax to get the label probabilities
        result = self._prepare_probs(probs, labels)
        return result

    def _prepare_probs(self, params, categories: list):
        probs = []
        for i, single_preds in enumerate(params):
            single_probs = {}
            for j, pred in enumerate(single_preds):
                single_probs[categories[j]] = round(float(pred), 6) * 100
            probs.append(single_probs)
        return probs
