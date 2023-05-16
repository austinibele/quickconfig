from quickconfig.main_base import MainBase

from example.model_config import ModelConfig
from example.training_config import TrainingConfig


class MainConfig(MainBase):
    def __init__(self):
        super().__init__(prog="train.sh", description="Train a model")
        self.model = ModelConfig
        self.training = TrainingConfig
