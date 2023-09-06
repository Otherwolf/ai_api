import inspect
import os

import torch
from PIL import Image

from .model import preprocess, load_model
from transformers import CLIPModel, CLIPProcessor


class AestheticModel:
    def __init__(self):
        self.model_name = "laion/CLIP-ViT-H-14-laion2B-s32B-b79K"
        # self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = 'cpu'

        model = CLIPModel.from_pretrained(self.model_name)
        self.vision_model = model.vision_model
        self.vision_model.to(self.device)
        del model
        self.clip_processor = CLIPProcessor.from_pretrained(self.model_name)

        base_path = os.path.dirname(inspect.getfile(AestheticModel)).replace('\\', '/') + '/'
        self.rating_model = load_model(base_path + "aesthetics_scorer_rating_openclip_vit_h_14.pth")\
            .to(self.device)
        self.artifacts_model = load_model(base_path + "aesthetics_scorer_artifacts_openclip_vit_h_14.pth")\
            .to(self.device)

    def predict(self, image_path: str):
        image = Image.open(image_path)
        inputs = self.clip_processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            vision_output = self.vision_model(**inputs)

        pooled_output = vision_output.pooler_output
        embedding = preprocess(pooled_output)

        with torch.no_grad():
            rating = self.rating_model(embedding)
            artifact = self.artifacts_model(embedding)

        return {
            'rating': rating.detach().cpu().item(),
            'artifacts': artifact.detach().cpu().item()
        }


if __name__ == '__main__':
    image_path = "e3d1b2b9eab9873731c701f345a3c0dd.jpeg"
