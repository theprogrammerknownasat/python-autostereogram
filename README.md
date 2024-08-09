# Video to Autostereogram Converter

> [!IMPORTANT]
> This repository is based on a codebase that I did not originally write. Most of the generation code is borrowed from [synesthesiam's magicpy](https://github.com/synesthesiam/magicpy)

This project converts a video into a series of autostereograms (MagicEye images) and reassembles them into a final video. It also supports optional grayscale conversion of coloured video. 

## Requirements

- Python 3.X
- `numpy`
- `moviepy`
- `PIL` (Pillow)
- `opencv-python`
- `tqdm`

## Installation

Install the required Python packages using pip:

```sh
pip install numpy moviepy pillow opencv-python tqdm
```

## Usage
> [!CAUTION]
> This program will include artifacts in most of the videos. If you know how to fix this, PLEASE submit a pull request. I have tried way too long to fix this but to no avail.

Run main.py with the correct arguments.

Arguements possible:
```sh
positional arguments:
  input_video           Path to the input video file

options:
  -h, --help            show this help message and exit
  --split_input_file    Split input file into frames
  --split_audio         Split audio from video
  --convert_to_autostereogram
                        Convert input to output
  -i, --invert          Invert depth map
  --remove              Remove intermediate files
  --convert_to_grayscale
                        Convert frames to grayscale
```

Example:
```sh
python main.py input.mp4 -i
```
This will convert the input file while inverting it.

```sh
python main.py input.mp4 --convert_to_autostereogram --split_audio
```
This will disable conversion and splitting of audio, only attempting to create the final video and split the initial video into frames.

## Lisence

This project is licensed under the MIT License.

