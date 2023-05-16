class BaseConfig:
    """
    BaseConfig is a class for managing configuration arguments and subconfigs. It allows for
    adding arguments, adding subconfigs as attributes, locking and freezing configurations, and exporting
    the configuration as a dictionary.
    """

    locked = False  # Lock flag
    frozen = False  # Freeze flag
    # Reserved attribute names cannot be used as argument names
    reserved_attributes = [
        "arg_dict",
        "help_dict",
        "locked",
        "frozen",
        "add_argument",
        "to_dict",
        "reserved_attributes",
    ]

    def __init__(self):
        """
        Initialize BaseConfig with empty arg_dict and help_dict.
        """
        self.arg_dict = {}  # Dictionary to hold argument information
        self.help_dict = {}  # Dictionary to hold help information

    def add_argument(self, name, type, default, help, validation=None):
        """
        Adds an argument to the configuration.

        Args:
            name (str): The name of the argument.
            type (type): The type of the argument.
            default (any): The default value of the argument.
            help (str): The help text for the argument.
            validation (function, optional): A validation function for the argument. Defaults to None.

        Raises:
            TypeError: If the default value does not match the type defined.
            ValueError: If the default value does not meet validation criteria.
        """
        if not isinstance(default, type) and default is not None and default != "none":
            raise TypeError(
                f"You defined the type for the argument {name} as {type}, however the default value has type {default.__class__}"
            )

        if validation is not None and default is not None and default != "none":
            if not validation(default):
                raise ValueError(
                    f"The default value for the argument {name} does not meet defined validation criteria."
                )

        setattr(self, name, default)

        self.arg_dict[name] = {"type": type, "validation": validation}
        self.help_dict[name] = help

    def __setattr__(self, key, value):
        """
        Sets the value of an attribute (config argument)

        Args:
            key (str): The name of the attribute.
            value (any): The value of the attribute.

        Raises:
            Exception: If trying to set a reserved attribute.
            TypeError: If trying to set or change an attribute when frozen.
            TypeError: If trying to set a new attribute when locked.
        """
        if key in self.reserved_attributes and self.locked and key != "frozen":
            raise Exception(
                f"'arg_dict' and 'help_dict' are reserved attributes and cannot be set."
            )
        if self.frozen:
            raise TypeError(
                "This Config has been frozen and attributes can no longer be set or changed"
            )
        if self.locked and not hasattr(self, key):
            raise TypeError("New attributes can no longer be set on this config")
        object.__setattr__(self, key, value)

    def to_dict(self):
        """
        Exports the configuration as a dictionary.

        Returns:
            dict: A dictionary representation of the configuration.
        """
        _dict = {}
        for k in self.arg_dict.keys():
            v = self.__getattribute__(k)
            _dict[k] = v
        return _dict
