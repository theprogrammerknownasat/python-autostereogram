import os
import numpy
import moviepy.editor as mp
import subprocess
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import importlib.util
from PIL import Image
import cv2
import shutil
import argparse


class VideoProcessor:
    def __init__(self, config):
        self.split_input_file = config.get('split_input_file')
        self.split_audio = config.get('split_audio')
        self.invert = config.get('invert')
        self.remove = config.get('remove')
        self.convert_to_grayscale = config.get('convert_to_grayscale')
        self.input_video = config.get('input_video')
        self.convert = config.get('convert_to_autostereogram')

        # Create input and output directories
        os.makedirs('input', exist_ok=True)
        os.makedirs('output', exist_ok=True)

        # Check if numpy is available
        if importlib.util.find_spec("numpy") is None:
            raise ImportError("numpy is required to run magicpy.py but is not installed.")

    def extract_audio(self, video):
        print("Extracting audio from video...")
        if self.split_audio:
            audio = video.audio
            audio.write_audiofile('audio.wav')
        else:
            print("Skipping audio extraction...")

    def save_frame(self, i, frame):
        frame_image = mp.ImageClip(frame)
        if self.convert_to_grayscale:
            frame_image = frame_image.fx(mp.vfx.blackwhite)
        frame_image.save_frame(f'input/frame_{i:04d}.png')

    def extract_frames(self, video):
        print("Extracting frames from video...")
        if self.split_input_file:
            frames = list(video.iter_frames())
            num_threads = os.cpu_count()
            print(f"Using {num_threads} threads for extracting frames.")
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                list(tqdm(executor.map(lambda i: self.save_frame(i, frames[i]), range(len(frames))), total=len(frames),
                          desc="Extracting frames"))
        else:
            print("Skipping frame extraction...")

    def convert_frame(self, frame_file):
        input_path = os.path.join('input', frame_file)
        output_path = os.path.join('output', frame_file)
        subprocess.run(
            ['python', 'magicpy.py', input_path, '-o', output_path, '-p 15'] if not self.invert else ['python',
                                                                                                      'magicpy.py',
                                                                                                      input_path,
                                                                                                      '-o', output_path,
                                                                                                      '-i', '-p 15'],
            check=True)

    def convert_frames(self):
        print("Converting frames to autostereograms...")
        if self.convert:
            print("Converting frames to autostereograms...")
            frame_files = [f for f in os.listdir('input') if f.endswith('.png')]
            num_threads = os.cpu_count()
            print(f"Using {num_threads} threads for converting frames.")
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                list(tqdm(executor.map(self.convert_frame, frame_files), total=len(frame_files), desc="Converting frames"))
        else:
            print("Skipping frame conversion...")

        frame_files = [f for f in os.listdir('input') if f.endswith('.png')]
        if not frame_files:
            raise ValueError("No files found in conversion output. Is conversion disabled?")

    def verify_frames(self):
        output_png_files = [f for f in os.listdir('output') if f.endswith('.png')]
        valid_frame_files = []
        for frame_file in output_png_files:
            try:
                with Image.open(os.path.join('output', frame_file)) as img:
                    img.verify()  # Verify that it is, in fact, an image
                    valid_frame_files.append(os.path.join('output', frame_file).replace('\\', '/'))
            except (IOError, SyntaxError) as e:
                print(f"Invalid image file {frame_file}: {e}")

        if not valid_frame_files:
            raise ValueError("No valid frame files found to create the video.")
        return valid_frame_files

    @staticmethod
    def assemble_video(valid_frame_files, video):
        frame = cv2.imread(valid_frame_files[0])
        height, width, layers = frame.shape
        video_out = cv2.VideoWriter('output_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), video.fps, (width, height))

        for frame_file in valid_frame_files:
            frame = cv2.imread(frame_file)
            video_out.write(frame)

        video_out.release()

    def add_audio(self):
        final_video = mp.VideoFileClip('output_video.mp4')
        final_video = final_video.set_audio(mp.AudioFileClip('audio.wav'))
        final_video.write_videofile(f'{self.input_video.split(".mp4")[0]}_final_output.mp4', codec='libx264')

    def clean_up(self):
        if self.remove:
            shutil.rmtree('input')
            shutil.rmtree('output')
            if os.path.exists('audio.wav'):
                os.remove('audio.wav')
            if os.path.exists('output_video.mp4'):
                os.remove('output_video.mp4')

    def process_video(self):
        video = mp.VideoFileClip(self.input_video)
        self.extract_audio(video)
        self.extract_frames(video)
        self.convert_frames()
        valid_frame_files = self.verify_frames()
        self.assemble_video(valid_frame_files, video)
        self.add_audio()
        self.clean_up()


class Config:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Video to autostereogram converter")
        self.parser.add_argument("--split_input_file", action="store_true", help="Split input file into frames",
                                 default=True)
        self.parser.add_argument("--split_audio", action="store_true", help="Split audio from video", default=True)
        self.parser.add_argument("--convert_to_autostereogram", action="store_true", help="Convert input to output", default=True)
        self.parser.add_argument("-i", "--invert", action="store_true", help="Invert depth map", default=False)
        self.parser.add_argument("--remove", action="store_true", help="Remove intermediate files", default=True)
        self.parser.add_argument("--convert_to_grayscale", action="store_true", help="Convert frames to grayscale",
                                 default=False)
        self.parser.add_argument("input_video", type=str, help="Path to the input video file")
        self.args = self.parser.parse_args()

    def get(self, option):
        return getattr(self.args, option)


if __name__ == "__main__":
    config = Config()
    processor = VideoProcessor(config)
    processor.process_video()
