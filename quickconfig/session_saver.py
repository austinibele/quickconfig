import os
import time
import random


class SessionSaver:
    """
    The SessionSaver class is responsible for creating and managing directories
    where model run data is stored during experiments.
    """

    @classmethod
    def configure_save_dir_and_run_id(cls, model_save_dir, experiment_name):
        """
        Configures the directory where the model data will be saved during the run
        of a particular experiment and assigns a unique run_id for each new run.

        Parameters:
        -----------
        model_save_dir : str
            The directory where all models are saved.

        experiment_name : str
            The name of the current experiment.

        Returns:
        --------
        save_dir : str
            The directory where the model data for the current run will be saved.

        run_id : int
            The unique identifier for the current run.
        """
        save_dir = os.path.join(model_save_dir, experiment_name)

        # Check if the save_dir exists, if not create it.
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Sleep for a random time to avoid race conditions in parallel executions.
        time.sleep(random.random())

        # List all directories in the save_dir.
        current_dirs = [x[0] for x in os.walk(save_dir)]

        # If there are no directories, this is the first run.
        if len(current_dirs) == 1:
            save_dir = os.path.join(save_dir, "1")
            run_id = 1
            os.makedirs(save_dir)
            print("Experiment directory empty, starting run_id 1")

        else:
            # If there are directories, find the maximum run_id and increment it for the new run.
            current_dirs = [x[0] for x in os.walk(save_dir)]
            current_dirs = [
                int(d.split("/")[-1])
                for d in current_dirs
                if d.split("/")[-1].isnumeric()
            ]

            run_id = max(current_dirs) + 1
            save_dir = os.path.join(save_dir, str(run_id))

            print("***********************************")
            print(f"Setting save path for run {run_id}")
            print("***********************************")
            print(f"Save path = {save_dir}")
            print("***********************************")

            # Create the directory for the new run.
            os.makedirs(save_dir)

        return save_dir, run_id
