from quickconfig.base_config import BaseConfig


class TrainingConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.add_argument(
            name="dataset_to_use",
            type=str,
            default="default",
            help="Which dataset do we want to use?",
            validation=None,
        )
        self.add_argument(
            name="use_mlflow_logger",
            type=bool,
            default=False,
            help="Should we log with mlflow?",
            validation=None,
        )
        self.add_argument(
            name="lr",
            type=float,
            default=1e-3,
            help="This is a mock integer arg",
            validation=lambda x: x >= 1e-9 and x <= 1e-2,
        )
