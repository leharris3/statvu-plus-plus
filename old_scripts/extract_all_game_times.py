import json
import cv2
from PIL import Image
import pytesseract
import sys
import re

ROIS = {
    "TNT": [840, 215, 608, 24]
}


def map_clock_to_timestamps(video_path, roi):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    timestamps = {}

    roi_frame_index = 0
    width_start = roi[0]
    width_offset = roi[1]
    height_start = roi[2]
    height_offset = roi[3]

    capture = cv2.VideoCapture(video_path)
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

    print("Processing frames:")
    for frame_index in range(total_frames):
        # print(timestamps)
        ret, frame = capture.read()
        if not ret:
            break

        frame_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        roi = frame_image[height_start: height_start +
                          height_offset, width_start: width_start + width_offset]

        # Preprocessing
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        roi_gray = cv2.GaussianBlur(roi_gray, (5, 5), 0)
        _, roi_threshold = cv2.threshold(
            roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # roi_pil = Image.fromarray(roi_threshold)

        # Perform OCR
        result = pytesseract.image_to_string(roi_threshold, config='--psm 6')

        quarter = None
        time_seconds = None

        text = result.split()
        pattern = r'^[0-9.:]+$'
        filtered_text = [word for word in text if re.match(pattern, word)]
        print(filtered_text)

        if quarter is not None and time_seconds is not None:
            timestamps[frame_index] = [quarter, time_seconds]

        if frame_index == roi_frame_index:
            roi_image = Image.fromarray(roi)
            roi_image.save('roi_frame.jpg')

        # progress = (frame_index + 1) / total_frames
        # progress_bar = "[" + "#" * \
        #     int(progress * 20) + " " * (20 - int(progress * 20)) + "]"
        # sys.stdout.write("\r{} {:.2f}%".format(progress_bar, progress * 100))
        # sys.stdout.flush()

    capture.release()
    print("\nProcessing completed.")
    return timestamps


def convert_time_to_seconds(time_str):
    if ':' in time_str:
        time_parts = time_str.split(':')
        minutes = int(time_parts[0])
        seconds = float(time_parts[1])
    elif '.' in time_str:
        seconds = float(time_str)
        minutes = 0
    else:
        raise ValueError("Invalid time format")

    return minutes * 60 + seconds


def extract_time(video):
    game = video[0]
    width_start = video[1]
    width_offset = video[2]
    height_start = video[3]
    height_offset = video[4]
    roi = [width_start, width_offset, height_start, height_offset]

    in_path = '2016.NBA.Raw.Video.Replays/' + game + '/' + game + '.mp4'
    out_path = '2016.NBA.Raw.Video.Replays/' + game + '/' + game + '.json'
    timestamps = map_clock_to_timestamps(in_path, roi)
    # Save result as JSON
    with open(out_path, 'w') as f:
        json.dump(timestamps, f)

    print("Result saved as", out_path)


# videos = [
#     ["01.14.2016.LAL.at.GSW", 840, 215, 608, 24],
#     ["01.22.2016.IND.at.GSW_short", 825, 123, 575, 30],
#     ["10.28.2015.CLE.at.MEM", 820, 183, 586, 38],
#     ["10.31.2015.GSW.at.NOP", 820, 183, 586, 38],
#     ["11.11.2015.GSW.at.MEM", 820, 183, 586, 38],
#     ["11.14.2015.BKN.at.GSW", 1020, 112, 623, 28],
#     ["11.17.2015.TOR.at.GSW", 1020, 112, 623, 28],
#     ["11.20.2015.CHI.at.GSW", 825, 123, 575, 30],
#     ["11.22.2015.GSW.at.DEN", 825, 123, 575, 30],
#     ["12.05.2015.GSW.at.TOR", 988, 147, 621, 22],
#     ["12.12.2015.GSW.at.MIL", 1020, 112, 623, 28],
#     ["12.16.2015.PHX.at.GSW", 825, 123, 575, 30],
#     ["12.17.2015.OKC.at.CLE", 825, 123, 575, 30],
#     ["12.23.2015.NYK.at.CLE", 820, 183, 586, 38]
# ]
