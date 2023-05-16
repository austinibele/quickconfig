import sys
import json
import os
from datetime import datetime
from .session_saver import SessionSaver
from .base_config import BaseConfig


class MainBase:
    """
    The MainBase class is responsible for managing configurations and sessions in the system.
    It has methods to build, save, load and freeze configurations. It determines the save directory and experiment name.
    It performs the logic to override default arguments with file-based configs or command-line arguments.
    """

    __frozen = False
    __dont_save = False
    __eval = False
    reserved_attributes = [
        "reserved_attributes",
        "build",
        "to_dict",
        "prog",
        "description",
    ]

    def __init__(self, prog, description):
        """
        Initialize the MainBase instance.

        Args:
            prog (str): The program name.
            description (str): The program description.
        """
        self.prog = prog
        self.description = description

    def build(self, dont_save=False):
        """
        Build the configuration. Create the save directory and save the config if indicated.

        Args:
            dont_save (bool): If True, the configuration will not be saved. Defaults to False.
        """
        self.__dont_save = dont_save

        cmd_args = sys.argv[1:]
        cmd_args, save_dir, experiment_name = self.__set_save_dir_experiment_name(
            cmd_args
        )
        self.__set_defaults()
        cmd_args = self.__display_help(cmd_args=cmd_args)
        self.__override_defaults(cmd_args=cmd_args)
        self.__load_checkpoint_config_if_indicated()
        if (
            self.__eval and save_dir == "results"
        ):  # if we're running eval and the save_dir hasn't been customized/overridden
            save_dir = "eval_results"
        self.__freeze_configs()
        if not self.__dont_save:
            save_dir = self.__create_save_dir(
                save_dir=save_dir, experiment_name=experiment_name
            )
            self.__save_configs(save_dir=save_dir)
            self.save_dir = save_dir
        else:
            self.save_dir = None
        self.frozen = True

    def __load_checkpoint_config_if_indicated(self):
        """
        Load a checkpoint configuration if specified.
        """
        if len(self.__subconfigs) == 1 and self.__subconfigs[0] == "evaluation":
            subcfg = getattr(self, self.__subconfigs[0])
            config_path = getattr(subcfg, "checkpoint")
            config_path = config_path.rsplit("/", 1)[0]
            config_path = os.path.join(config_path, "config.json")
            config = self.__load_json(config_path=config_path)
            config = self.__load_subconfigs_from_filepath(config=config)
            for k in config.keys():
                setattr(self, k, BaseConfig())
                self.__subconfigs.append(k)
            self.__assure_no_additional_keys(config=config)
            self.__override_with_filebased_args(config=config, assure_in_dir=False)
            self.__eval = True
        else:
            pass

    def to_dict(self):
        """
        Converts the configuration to a dictionary. The dictionary will be nested if subconfigs are present.

        Returns:
            dict: The configuration represented as a dictionary.
        """
        _dict = {}
        for cfg in self.__subconfigs:
            _dict[cfg] = {}
            val = getattr(self, cfg)
            for k in val.help_dict.keys():
                arg_val = getattr(val, k)
                _dict[cfg][k] = arg_val
        return _dict

    def __create_save_dir(self, save_dir, experiment_name):
        """
        Create a save directory using the SessionSaver.

        Args:
            save_dir (str): The base save directory.
            experiment_name (str): The experiment name.

        Returns:
            str: The newly created save directory.
        """
        save_dir, run_id = SessionSaver.configure_save_dir_and_run_id(
            model_save_dir=save_dir, experiment_name=experiment_name
        )
        return save_dir

    def __save_configs(self, save_dir):
        """
        Saves the configurations in a JSON file in the save directory.

        Args:
            save_dir (str): The directory where the configuration and any model/experiment data is saved.
        """
        config_to_save = self.to_dict()
        with open(os.path.join(save_dir, "config.json"), "w") as fp:
            json.dump(config_to_save, fp, indent=4, separators=(",", ": "))

    def __set_save_dir_experiment_name(self, cmd_args):
        """
        Extracts the save directory and experiment name from the command-line arguments and uses them to set
        the save_dir and experiment_name.

        Args:
            cmd_args (list): List of command line arguments.

        Returns:
            tuple: A tuple containing the new arguments, save directory, and experiment name.
        """
        save_dir = "results"
        experiment_name = datetime.today().strftime("%Y-%m-%d")
        new_args = []
        for arg in cmd_args:
            if "save_dir" in arg:
                save_dir = arg
            elif "experiment_name" in arg:
                experiment_name = arg
            else:
                new_args.append(arg)
        save_dir = save_dir.rsplit("=", 1)[-1]
        experiment_name = experiment_name.rsplit("=", 1)[-1]
        return new_args, save_dir, experiment_name

    def __display_help(self, cmd_args):
        """
        Displays the help message if '--h' or '--help' is detected as a command-line argument.

        Args:
            cmd_args (list): List of command line arguments.

        Returns:
            list: List of command line arguments.
        """
        if "--h" in cmd_args or "--help" in cmd_args:
            try:
                cmd_args.remove("--h")
            except:
                cmd_args.remove("--help")

            print(f"Usage:  {self.prog}  [OPTIONS] [OVERRIDE ARGS]")
            print("")
            print("Provide options in the form: {option}={value}")
            print("")
            print("Options:")
            print(
                "option: config                  description: Path to a filebased config (will override defaults)"
            )
            print(
                "option: save_dir                description: Parent directory for which to store experimental results"
            )
            print(
                "option: experiment_name         description: The name of the experiment. Results will be saved in directory save_dir/experiment_name"
            )
            print("")
            print("")
            print("")
            print(
                "To override a value use form {arg}={val}. For example, 'model.model_type=transformer'"
            )
            print(
                "Values provided in the command line will override defaults and file-based values"
            )
            print("")
            print("Args:")
            space = " "
            for cfg in self.__subconfigs:
                val = getattr(self, cfg)
                for k, v in val.help_dict.items():
                    type = str(val.arg_dict[k]["type"])
                    k = cfg + "." + k
                    print(
                        f"arg: {k}",
                        space * (35 - len(k)) + f"type: {type}",
                        space * (20 - len(type)) + f"description: {v}",
                    )
        return cmd_args

    def __set_defaults(self):
        """
        Set class attributes to be default argument values.
        """
        attrs = dir(self)
        self.__subconfigs = [
            a for a in attrs if "__" not in a and a not in self.reserved_attributes
        ]
        for cfg in self.__subconfigs:
            val = getattr(self, cfg)
            setattr(self, cfg, val())
            val = getattr(self, cfg)
            val.locked = True

    def __override_defaults(self, cmd_args):
        """
        Overrides the default configuration/attributes with command line arguments.

        Args:
            cmd_args (list): List of command line arguments.
        """
        config_path = self.__determine_config_path(cmd_args=cmd_args)
        if config_path == "":
            print(
                "No filebased config was defined. Only code-based defaults will be used instead."
            )
        else:
            config = self.__load_json(config_path=config_path)
            config = self.__load_subconfigs_from_filepath(config=config)
            self.__assure_no_additional_keys(config=config)
            self.__override_with_filebased_args(config=config)
        self.__override_with_cmdline_args(cmd_args=cmd_args)

    def __load_subconfigs_from_filepath(self, config):
        """
        Load sub-configurations from a file path.

        Args:
            config (dict): The base configuration.

        Returns:
            dict: The configuration with loaded sub-configurations.
        """
        new_config = {}
        for k, v in config.items():
            try:
                if ".json" in v[-5:]:
                    new_config[k] = self.__load_json(v)
                else:
                    new_config[k] = v
            except:
                new_config[k] = v
        return new_config

    def __determine_config_path(self, cmd_args):
        """
        Determine the path of the configuration file from the command-line arguments.

        Args:
            cmd_args (list): List of command line arguments.

        Returns:
            str: The path to the configuration file.
        """
        config_path = ""
        for arg in cmd_args:
            if "config=" in arg:
                config_path = arg.split("config=")[-1]
        return config_path

    def __load_json(self, config_path):
        """
        Loads a JSON file config.

        Args:
            config_path (str): The path to the configuration file.
            to the JSON file.

        Returns:
            dict: The loaded JSON data.
        """

        with open(config_path, "r") as f:
            config = json.load(f)
        return config

    def __assure_no_additional_keys(self, config):
        """
        Ensures that no additional keys are in the configuration.

        Args:
            config (dict): The configuration.

        Raises:
            ValueError: If there are additional keys in the configuration.
        """
        for key in list(config.keys()):
            if key not in self.__subconfigs:
                raise ValueError(
                    f"The emmbeded config with name '{key}' was not specified in ConfigMain. Make sure to specify all embedded configs within ConfigMain."
                )

    def __override_individual_subconfig(
        self, subcfg_name, subconfig, assure_in_dir=True
    ):
        """
        Method to override individual sub-configurations.

        Args:
            subcfg_name (str): The name of the sub-configuration.
            subconfig (dict): The sub-configuration to override.
            assure_in_dir (bool, optional): If True, validation is performed to ensure that the argument already exists in the sub-configuration exists.
            Defaults to True.

        Raises:
            ValueError: If the argument is not defined in the sub-configuration defaults.
        """
        for arg_name, val in subconfig.items():
            subcfg = getattr(self, subcfg_name)
            if (
                assure_in_dir
            ):  # When loading the config from a persisted file, we are not validating.
                if arg_name not in dir(subcfg):
                    raise ValueError(
                        f"The argument '{arg_name}' is not defined in the {subcfg_name} defaults config class. Did you mean to include '{subcfg_name}.{arg_name}={val}' in the file-based config or was that an accident?"
                    )
                val = self.__validate_arg(subcfg_name, subcfg, arg_name, val)
            else:
                subcfg.arg_dict[
                    arg_name
                ] = None  # Add arg name to arg_dict so it can be returned with to_dict() method
            setattr(subcfg, arg_name, val)

    def __override_with_filebased_args(self, config, assure_in_dir=True):
        """
        Override the configuration with file-based arguments.

        Args:
            config (dict): The configuration.
            assure_in_dir (bool, optional): If True, validation is performed to ensure that the argument already exists in the sub-configuration exists.
            Defaults to True.
        """
        for subcfg_name in config.keys():
            self.__override_individual_subconfig(
                subcfg_name=subcfg_name,
                subconfig=config[subcfg_name],
                assure_in_dir=assure_in_dir,
            )

    def __override_with_cmdline_args(self, cmd_args, assure_in_dir=True):
        """
        Overrides the configuration with command line arguments.

        Args:
            cmd_args (list): List of command line arguments.
            assure_in_dir (bool, optional): If True, validation is performed to ensure that the argument already exists in the sub-configuration exists.
            Defaults to True.
        Raises:
            Exception: If the argument is not valid.
            ValueError: If the argument is not defined in the sub-configuration defaults.
        """
        for arg in cmd_args:
            name, val = arg.split("=", 1)
            if name == "config":
                continue
            if "." not in name:
                if name in self.__subconfigs:
                    subconfig = self.__load_json(config_path=val)
                    self.__override_individual_subconfig(
                        subcfg_name=name, subconfig=subconfig
                    )
                else:
                    raise Exception(
                        f"The argument '{name}' is not valid. Please double check the argument name."
                    )
            else:
                subcfg_name, arg_name = name.split(".")

                subcfg = getattr(self, subcfg_name)
                if (
                    assure_in_dir
                ):  # When loading the config from a persisted file, we are not validating.
                    if arg_name not in dir(subcfg):
                        raise ValueError(
                            f"The argument '{arg_name}' is not defined in the '{subcfg_name}' defaults config class. Please check argument name. Valid arguments for the '{subcfg_name}' subconfig include: \
                                {list(subcfg.arg_dict.keys())}"
                        )
                    val = self.__validate_arg(subcfg_name, subcfg, arg_name, val)

                setattr(subcfg, arg_name, val)

    def __validate_arg(self, subcfg_name, subcfg, arg_name, val):
        """
        Validates an argument in a sub-configuration.

        Args:
            subcfg_name (str): The name of the sub-configuration.
            subcfg (dict): The sub-configuration.
            arg_name (str): The argument name.
            val (any): The argument value.

        Returns:
            any: The validated argument value.

        Raises:
            TypeError: If the argument value cannot be converted to the desired type.
            ValueError: If the argument value does not meet the validation criteria.
        """
        desired_type = subcfg.arg_dict[arg_name]["type"]
        try:
            val = desired_type(val)
        except Exception:
            raise TypeError(
                f"The parameter {subcfg_name}.{arg_name} with value '{val}' cannot be converted to type {desired_type.__name__}."
            )
        validation = subcfg.arg_dict[arg_name]["validation"]
        if validation is not None:
            if not validation(val):
                raise ValueError(
                    f"The file-based value for the parameter {subcfg_name}.{arg_name} does not meet defined validation creiteria."
                )
        return val

    def __freeze_configs(self):
        """
        Freezes all sub-configurations.
        """
        for cfg in self.__subconfigs:
            val = getattr(self, cfg)
            val.frozen = True

    def __setattr__(self, key, value):
        """
        Sets an attribute in the MainBase instance.

        Args:
            key (str): The attribute key.
            value (any): The attribute value.

        Raises:
            TypeError: If the MainBase instance is frozen and no attributes can be set or changed.
        """
        if self.__frozen:
            raise TypeError(
                "This Config has been frozen and attributes can no longer be set or changed"
            )
        object.__setattr__(self, key, value)
