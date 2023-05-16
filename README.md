<br>

# **quickconfig: A Simple yet Feature-rich Configuration Management System**

<br>

# **First Step: Define the Default Config Parameters**

## **Defining the Default Config**
- The default configuration (i.e. all parameters and values ) must be defined in code, similar to ArgParse.
- Each project requires a **Main Config** as well as 1 or more **Sub-Configs**
- The **Example/** directory in this repo demonstrates how to configure quickconfig with two sub-configs ('model' and 'training').
  - ModelConfig and TrainingConfig (sub-configs) inherit from BaseConfig. The subconfigs are where default arguments, types, and validation are defined.
  - MainConfig inherits from MainBase. The different sub-configs are defined in the `__init__` method.


## **Type and Value Validation**
- Arguments, types, defaults, help, and validation are defined in code similarly to ArgParser.
  - Example:
    ```
    self.add_argument(
        name="lr",
        type=float,
        default=1e-3,
        help="This is a mock integer arg",
        validation=lambda x: x >= 1e-9 and x <= 1e-2
    )
    ```

- Type validation is performed for all parameters. Type is a required field.
- Value validation is defined in the code using lambda functions.
  - Example: `validation=lambda x: x >= 1e-9 and x <= 1e-2`

<br>
<br>

# **Features**

## **Config Auto-Saving**
- A copy of the configuration used to start the experiment is automatically saved in the **output directory**.
    - By default, the output directory is **results/YYYY-MM-DD/<run_number>**, where:
        - **Save Dir** = **results**
        - **Experiment Name** = **YYYY-MM-DD**
        - **<run_number>** = The **N-th run** of the experiment (integer)
            - ex. 1st run = **results/YYYY-MM-DD/1**
            - ex. 1nd run = **results/YYYY-MM-DD/2** 
    - The config is saved at **results/YYYY-MM-DD/<run_number>/config.json**
  - The **Save Dir** and **Experiment Name** can be overridden by the file-based config (json/yml) or by command-line arguments.

<br>

## **Overriding Default Values**
- **Parameter values can be defined in three places**:
  1. In code: This is where defaults, types, and validation are defined.
  2. In file-based configs (e.g., JSON) with an embedded structure.
  3. In the command line.
<br>
<br>
- **File-based configs override default code-based** parameter values.
<br>

    - **Example**: The "lr" parameter defined in the example above under the **Type and Value Validation** section can be overriden from a file-based config as follows:
    <br>
    <br>
    **Contents of config.json**
        ```
        {"training": {"lr": 1e-4}}
        ```
<br>

- Parameter values passed in the **command line override both file-based and code-based** parameter values.

    - **Example:** The **lr** (learning rate) and **num_epochs** in the **training** subconfig can be overriden from the command-line like so:
        ```
        python -m src.main training.lr=1e-4 training.num_epochs=100
        ```

<br>

## **Reserved Command-Line Arguments**
- Three reserved command-line arguments allow you to specify the **path** to a **file-based config**, as well as to change the **Save Dir** and **Experiemnt Name**.

**config:** Specifies the path to a file-based config (overrides defaults).
```python
>> python -m src.main config=example/example_configs/filebased_config.json
```
**save_dir:** Parent directory for storing experimental results.
```python
>> python -m src.main save_dir=my_results
```
**experiment_name:** Name of the experiment. Results and config will be saved in the directory save_dir/experiment_name.
```python
>> python -m src.main experiment_name=my_first_experiment
```

<br>
<br>

# **Usage**

## **How to Use (Part 1)**
- File-based configs are optional.
- If using a file-based config, you must provide the config path as follows:
    - python -m src.main config=filebased_configs/config.json
- Override arguments in the command line by specifying the sub-config and argument, along with the new value, as shown in the following examples:
    - python -m src.main sub_config.argument_name=new_value
    - python -m src.main training.lr=1e-5

<br>

## **How to Use (Part 2)**
- To build a config object in your session, follow these steps:
```python
if __name__ == "__main__":
    config = MainConfig()
    config.build()

    session = MySession(config)
```

- Running config.build() builds and freezes the config.
    - No attributes in the config object can be mutated.
    - Occasionally, this may present a problem, such as when using PyTorch Lightning's save_hparams() method on initialization. To return a mutable config in dictionary form, use config.to_dict().
- 'config' is the main config, and subconfigs (embedded) can be accessed as attributes of config.
    - For example, config.training refers to the training config and config.model refers to the model config.
- The created save_dir, where config.json is resaved, can be accessed using config.save_dir.
- Arguments of subconfigs can be accessed as follows: config.model.layer_size.
- Calling config.subconfig.to_dict() will return a dictionary of the subconfig arguments.
- Calling config.to_dict() will return a nested dictionary containing all subconfigs.

<br>

## **Usage Examples**
- More sage examples are demonstrated in the tests located at tests/test.py.