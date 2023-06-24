import json
import statistics
import os

MAX_TIME = 720.0
MIN_TIME = 0.0
MIN_QUARTER = 1
MAX_QUARTER = 4


class Data:
    def __init__(self, title: str, network: str) -> None:
        self.path_to_unprocessed_data = f"statvu-data/{title}.7z"
        self.path_to_processed_data_zipped = f"statvu-plus-plus/{title}.{network}/{title}.{network}.7z"
        self.path_to_processed_data_unzipped = f"statvu-plus-plus/{title}.{network}/{title}.{network}.json"
        self.path_to_timestamps = f"statvu-plus-plus/{title}.{network}/timestamps.json"

    def post_process(self) -> bool:
        json_path = self.path_to_timestamps
        with open(json_path, 'r') as file:
            data = json.load(file)
            # 1. Apply statistical smooting to remove outliers.
            # modified_data = self.smooth_results(data=data)
            # 2. Inerpolate between clock values.
            modified_data = self.interpolate(data=data)
        os.remove(path=self.path_to_timestamps)
        with open(self.path_to_timestamps, 'w') as file:
            json.dump(modified_data, file, indent=4)
        return True

    def interpolate(self, data):
        modified_data = {}
        modified_times = {}
        frame_count = 0  # Maximum interpolation is one second

        for frame, time in data.items():
            quarter, remaining = time
            key = (quarter, remaining)

            # Remove garbage results
            if remaining > MAX_TIME or remaining < MIN_TIME or int(quarter) > MAX_QUARTER or int(quarter) < MIN_QUARTER:
                pass
            else:
                if key in modified_times:
                    if remaining != 0.0 and frame_count < 24:
                        modified_times[key] -= 0.04
                        modified_data[frame] = [
                            quarter, round(modified_times[key], 2)]
                        frame_count += 1
                    else:
                        modified_data[frame] = time
                else:
                    modified_times[key] = remaining
                    modified_data[frame] = time
                    frame_count = 0
        return modified_data

    def smooth_results(self, data):
        time_values = [entry[1] for entry in data.values()]
        # Calculate the mean and standard deviation of time values
        mean_value = statistics.mean(time_values)
        std_dev = statistics.stdev(time_values)
        # Filter out entries with time values deviating significantly from the mean
        filtered_data = {
            frame: values for frame, values in data.items() if abs(values[1] - mean_value) <= 2 * std_dev
        }
        return filtered_data
