import sys
import json
from typing import Dict, Any, List, Union


def print_progress(progress: float) -> None:
    progress_bar = "[" + "#" * \
        int(progress * 20) + " " * (20 - int(progress * 20)) + "]"
    sys.stdout.write("\r{} {:.2f}%".format(progress_bar, progress * 100))
    sys.stdout.flush()


def map_timestamps_to_statvu(timestamps_path: str, statvu_path: str) -> None:
    timestamp_data_path: str = timestamps_path
    timestamp_data_raw = open(timestamp_data_path)
    statvu_data_path: str = statvu_path
    statvu_data_raw = open(statvu_data_path)

    # load the data
    statvu_data: Dict[str, Any] = json.load(statvu_data_raw)
    timestamp_data: Dict[str, Union[int, List[Union[int, float]]]] = json.load(
        timestamp_data_raw)

    statvu_data["video_path"] = statvu_data_path.strip('.json') + '.mp4'

    for event in statvu_data['events']:
        for moment in event['moments']:
            quarter: str = str(moment[0])
            time: int = moment[2]

            key_exact: str = quarter + " " + str(time)
            key_one = quarter + " " + str(time - .01)
            key_two = quarter + " " + str(time - .02)
            key_three = quarter + " " + str(time - .03)
            key_four = quarter + " " + str(time + .01)
            key_five = quarter + " " + str(time + .02)
            key_six = quarter + " " + str(time + .03)

            if key_exact in timestamp_data:
                moment.append(timestamp_data[key_exact])
            elif key_one in timestamp_data:
                moment.append(timestamp_data[key_one])
            elif key_two in timestamp_data:
                moment.append(timestamp_data[key_two])
            elif key_three in timestamp_data:
                moment.append(timestamp_data[key_three])
            elif key_four in timestamp_data:
                moment.append(timestamp_data[key_four])
            elif key_five in timestamp_data:
                moment.append(timestamp_data[key_five])
            elif key_six in timestamp_data:
                moment.append(timestamp_data[key_six])
            else:
                moment.append(-1)

    out_path: str = statvu_data_path.strip('.json') + "_plus.json"
    with open(out_path, 'w') as f:
        json.dump(statvu_data, f)
