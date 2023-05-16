import sys
import pytest
import io

from example.main_config import MainConfig


def test_no_filebased_config():
    sys.argv = [None]
    config = MainConfig()
    config.build(dont_save=True)
    assert config.model.model_type == "retinanet"
    assert isinstance(config.model.model_type, str)

    assert config.training.dataset_to_use == "default"
    assert isinstance(config.training.dataset_to_use, str)

    assert config.training.use_mlflow_logger == False
    assert isinstance(config.training.use_mlflow_logger, bool)

    assert config.training.lr == 1e-3
    assert isinstance(config.training.lr, float)


def test_valid_filebased_config():
    sys.argv = [
        None,
        "config=example/example_configs/filebased_config.json",
        "save_dir=my_results",
        "experiment_name=my_first_experiment",
    ]
    config = MainConfig()
    config.build(dont_save=True)
    assert config.model.model_type == "patch"
    assert isinstance(config.model.model_type, str)

    assert config.training.dataset_to_use == "rayleigh_dataset"
    assert isinstance(config.training.dataset_to_use, str)

    assert config.training.use_mlflow_logger == False
    assert isinstance(config.training.use_mlflow_logger, bool)

    assert config.training.lr == 1e-4
    assert isinstance(config.training.lr, float)


def test_invalid_filebased_config():
    sys.argv = [None, "config=example/example_configs/filebased_config_invalid.json"]
    with pytest.raises(Exception):
        config = MainConfig()
        config.build(dont_save=True)


def test_valid_cmdline_override():
    sys.argv = [
        None,
        "config=example/example_configs/filebased_config.json",
        "training.lr=1e-8",
    ]
    config = MainConfig()
    config.build(dont_save=True)
    assert config.model.model_type == "patch"
    assert isinstance(config.model.model_type, str)

    assert config.training.dataset_to_use == "rayleigh_dataset"
    assert isinstance(config.training.dataset_to_use, str)

    assert config.training.use_mlflow_logger == False
    assert isinstance(config.training.use_mlflow_logger, bool)

    assert config.training.lr == 1e-8
    assert isinstance(config.training.lr, float)


def test_invalid_cmdline_override_0():
    sys.argv = [
        None,
        "config=example/example_configs/filebased_config.json",
        "training.lr=learning_rate",
    ]
    with pytest.raises(Exception):
        config = MainConfig()
        config.build(dont_save=True)


def test_invalid_cmdline_override_1():
    sys.argv = [
        None,
        "config=example/example_configs/filebased_config.json",
        "training.lr=10",
    ]
    with pytest.raises(Exception):
        config = MainConfig()
        config.build(dont_save=True)


def test_invalid_cmdline_override_2():
    sys.argv = [
        None,
        "config=example/example_configs/filebased_config.json",
        "model.model_type=bad_model_type",
    ]
    with pytest.raises(Exception):
        config = MainConfig()
        config.build(dont_save=True)


def test_configs_immutable():
    sys.argv = [None]
    config = MainConfig()
    config.build(dont_save=True)

    with pytest.raises(Exception):
        config.model.model_type = "different_model_type"

    with pytest.raises(Exception):
        config.training.lr = 1e-5


def test_help_message():
    sys.argv = [None, "--h"]
    config = MainConfig()

    capturedOutput = io.StringIO()
    sys.stdout = capturedOutput

    config.build(dont_save=True)

    sys.stdout = sys.__stdout__
    text = capturedOutput.getvalue()
    print(text)
    assert len(text) > 100


@pytest.mark.skip(reason="saves files to disk")
def test_default_save_config():
    sys.argv = [None]
    config = MainConfig()
    config.build()


@pytest.mark.skip(reason="saves files to disk")
def test_save_config_user_defined_dir():
    sys.argv = [None, "save_dir=my_results", "experiment_name=my_first_experiment"]
    config = MainConfig()
    config.build()


def test_subconfig_to_dict():
    sys.argv = [None]
    config = MainConfig()
    config.build(dont_save=True)

    model = config.model.to_dict()
    assert isinstance(model, dict)
    assert model["model_type"] == "retinanet"

    training = config.training.to_dict()
    assert isinstance(training, dict)


def test_main_config_to_dict():
    sys.argv = [None]
    config = MainConfig()
    config.build(dont_save=True)

    _dict = config.to_dict()
    assert list(_dict.keys()) == ["model", "training"]
    assert _dict["model"]["model_type"] == "retinanet"


@pytest.mark.skip(reason="saves files to disk")
def test_save_dir_is_attr():
    sys.argv = [None]
    config = MainConfig()
    config.build(dont_save=False)
    save_dir = config.save_dir
    assert "results/" in save_dir


def test_subconfigs_defined_by_path():
    sys.argv = [None, "config=example/example_configs/subconfigs_defined_by_path.json"]
    config = MainConfig()
    config.build(dont_save=True)

    assert config.model.model_type == "patch"
    assert isinstance(config.model.model_type, str)

    assert config.training.dataset_to_use == "rayleigh_dataset"
    assert isinstance(config.training.dataset_to_use, str)

    assert config.training.use_mlflow_logger == False
    assert isinstance(config.training.use_mlflow_logger, bool)

    assert config.training.lr == 1e-4
    assert isinstance(config.training.lr, float)


def test_override_subconfig_with_path_cmd():
    sys.argv = [
        None,
        "config=example/example_configs/filebased_config.json",
        "model=example/example_configs/model_2.json",
    ]
    config = MainConfig()
    config.build(dont_save=True)
    assert config.model.model_type == "retinanet"
    assert isinstance(config.model.model_type, str)

    assert config.training.dataset_to_use == "rayleigh_dataset"
    assert isinstance(config.training.dataset_to_use, str)

    assert config.training.use_mlflow_logger == False
    assert isinstance(config.training.use_mlflow_logger, bool)

    assert config.training.lr == 1e-4
    assert isinstance(config.training.lr, float)


if __name__ == "__main__":
    test_no_filebased_config()
    test_valid_filebased_config()
    test_invalid_filebased_config()
    test_valid_cmdline_override()
    test_invalid_cmdline_override_0()
    test_invalid_cmdline_override_1()
    test_invalid_cmdline_override_2()
    test_configs_immutable()
    test_help_message()
    test_default_save_config()
    test_save_config_user_defined_dir()
    test_subconfig_to_dict()
    test_main_config_to_dict()
    test_save_dir_is_attr()
    test_subconfigs_defined_by_path()
    test_override_subconfig_with_path_cmd()
