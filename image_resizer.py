#!/usr/bin/env python3

from PIL import Image
import argparse
from pathlib import Path


class CommandLineParser:
    INPUT_RAW_IMAGE_DIR = "raw_images"
    OUTPUT_RESIZE_IMAGE_DIR = "resized_images"

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(
            description="Script to resize images in a directory and save as JPG"
        )
        parser.add_argument(
            "-d", "--directory", type=str, default=None, help="Directory containing images"
        )
        parser.add_argument(
            "-s", "--size", type=str, required=True, help="Resize size, format: widthxheight"
        )
        args = parser.parse_args()

        if args.directory is None:
            args.directory = Path(__file__).resolve().parent

        args.size = CommandLineParser.get_image_size(args.size)

        return args

    @staticmethod
    def get_image_size(size_str):
        try:
            width, height = map(int, size_str.split("x"))
            return width, height
        except ValueError:
            raise ValueError(
                "Size should be specified in '[width]x[height]' format. Example: -s 640x480"
            )


class ImageResizer:
    def __init__(self, image_path, output_size):
        self.image_path = image_path
        self.output_size = output_size

    def resize_image(self):
        with Image.open(self.image_path) as image:
            # Calculate the scaling factor and resize the image
            scale = min(self.output_size[0] / image.size[0], self.output_size[1] / image.size[1])
            new_size = (int(image.size[0] * scale), int(image.size[1] * scale))
            resized_image = image.resize(new_size, Image.Resampling.LANCZOS)

            # Create new image with desired size and black background
            new_image = Image.new("RGB", self.output_size, (0, 0, 0))

            # Calculate padding
            pad_x = (self.output_size[0] - new_size[0]) // 2
            pad_y = (self.output_size[1] - new_size[1]) // 2

            # Paste the resized image onto the new image
            new_image.paste(resized_image, (pad_x, pad_y))

            return new_image


class Application:
    SUPPORTED_FORMATS = {".jpg", ".bmp", ".png"}

    def __init__(self, args):
        self.args = args
        self.input_directory_path = Path(args.directory) / CommandLineParser.INPUT_RAW_IMAGE_DIR
        self.output_directory_path = (
            Path(args.directory) / CommandLineParser.OUTPUT_RESIZE_IMAGE_DIR
        )

    def log_info_about_arguments(self):
        print("Arguments:")
        print(f"  Image file: {self.get_short_path(self.input_directory_path)}")
        print(f"  Image size: {self.args.size}")

    def log_info_about_output_files(self):
        print("\nOutput files:")
        print(f"  Resized image: {self.get_short_path(self.output_directory_path)}")

    @staticmethod
    def get_short_path(full_path):
        """Returns the last two parts of the path to shorten the display."""
        path = Path(full_path)
        return Path(path.parts[-2], path.name).as_posix()

    def run(self):
        try:
            self.output_directory_path.mkdir(parents=True, exist_ok=True)

            # Log info
            self.log_info_about_arguments()
            self.log_info_about_output_files()

            for image_file in self.input_directory_path.glob("*"):
                if image_file.suffix.lower() in self.SUPPORTED_FORMATS:
                    self.resize_and_save_image(image_file)

        except Exception as e:
            print(f"Error: {e}")

    def resize_and_save_image(self, image_path):
        resizer = ImageResizer(str(image_path), self.args.size)
        resized_image = resizer.resize_image()

        output_file_path = self.output_directory_path / f"{image_path.stem}.jpg"
        resized_image.save(output_file_path, format="JPEG")


def main():
    args = CommandLineParser.parse_arguments()
    app = Application(args)
    app.run()


if __name__ == "__main__":
    main()