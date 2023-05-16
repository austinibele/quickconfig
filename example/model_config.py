from quickconfig.base_config import BaseConfig


class ModelConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.add_argument(
            name="model_type",
            type=str,
            default="retinanet",
            help="The type of model to use",
            validation=lambda x: x in ["retinanet", "patch"],
        )
