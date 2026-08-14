from app.ai.providers.fashionclip import FashionCLIPProvider

class MarqoFashionCLIPProvider(FashionCLIPProvider):
    def __init__(self):
        super().__init__(model_name="Marqo/marqo-fashionCLIP")
