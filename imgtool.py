#!/usr/bin/env python3

###############################################################
### PROJECT: Image Compressor and Metadata Remover CLI
### SCRIPT: imgtool
### VERSION: v1.0
### DESCRIPTION:
### A script to make compressing image files more easily.
### ############################################################

import argparse
import os, sys
from PIL import Image
from pathlib import Path


def compress_image(
    input_file: str,
    output_file: str,
    quality: int = 85,
    max_width: int = None,
    max_height: int = None,
) -> None:
    """
    Remove all metadata (EXIF, GPS, camera info, copyright) and compress a JPG image.

    Args:
        input_file (str): Input image path.
        output_file (str): Output image path.
        quality (int): JPG quality (1-95). Lower = more compression.
        max_width (int): Optional max width.
        max_height (int): Optional max height.
    """

    try:
        # Open image without loading EXIF
        with Image.open(input_file) as img:
            # Convert to RGB to avoid issues with PNG or other formats
            img = img.convert("RGB")

            # Resize if requested
            if max_width or max_height:
                img.thumbnail((max_width or img.width, max_height or img.height))

            # Save without metadata
            img.save(
                output_file,
                format="JPEG",
                quality=quality,
                optimize=True,
                progressive=True,
            )

    except Exception as e:
        print(f" ❌ \033[1;35mError processing \033[1;36m{input_file}\033[1;35m:\033[1;36m {e}\033[0m", file=sys.stderr)
        sys.exit(1)


def validate_quality(quality: int) -> bool:
    # Check if the quality is valid
    if quality not in range(1, 95):
        print(f" ❌ \033[1;35mInvalid quality value:\033[1;36m {quality}\033[0m")
        return False
    return True


def validate_recursive(args) -> bool:
    # Check if the recursive is being in batch mode
    if args.recursive and not args.input_folder:
        print(" ❌ \033[1;35mThe \033[1;36m--recursive\033[1;35m flag is only valid when using \033[1;36m--input-folder\033[0m")
        return False
    return True


def validate_args_single_file(input_file: str, output_file: str) -> bool:
    # Check if the input file exists
    if not os.path.isfile(input_file):
        print(f" ❌ \033[1;35mInput file does not exist:\033[1;36m {input_file}\033[0m")
        return False

    # Check if the input file is a .jpg file
    if not input_file.lower().endswith((".jpg", ".jpeg")):
        print(f" ❌ \033[1;35mInput file needs to be a (.jpg, .jpeg) file:\033[1;36m {input_file}\033[0m")
        return False

    # Check if the output file is a .jpg file
    if not output_file.lower().endswith((".jpg", ".jpeg")):
        ask = f" ❔ \033[1;31mOutput file \033[1;36m\"{output_file}\"\033[1;31m does not end with (\".jpg\", \".jpeg\"). Are you sure you want to continue?\033[1;36m (y/n)\033[0m "
        confirm = input(ask)
        if confirm == "No" or confirm == "no" or confirm == "N" or confirm == "n":
            return False
        elif confirm != "Yes" and confirm != "yes" and confirm != "Y" and confirm != "y":
            return False

    # Check to make sure the user really wants to overwrite the existing file with the new output file
    if os.path.isfile(output_file):
        ask = f" ❔ \033[1;31mOutput file \033[1;36m\"{output_file}\"\033[1;31m already exists. Are you sure you want to overwrite it?\033[1;36m (y/n)\033[0m "
        confirm = input(ask)
        if confirm == "No" or confirm == "no" or confirm == "N" or confirm == "n":
            return False
        elif confirm != "Yes" and confirm != "yes" and confirm != "Y" and confirm != "y":
            return False

    return True


def validate_args_batch(input_folder: str) -> bool:
    # Check if the input folder exists
    if not os.path.isdir(input_folder):
        print(f" ❌ \033[1;35mInput folder does not exist:\033[1;36m {input_folder}\033[0m")
        return False
    return True


def log(message: str, verbose: bool) -> None:
    if verbose:
        print(message)


def main():
    parser = argparse.ArgumentParser(description="Compress JPG images and remove metadata. Supports single file or batch folder processing.")

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-i", "--input", help="Input JPG file path")
    input_group.add_argument("-I", "--input-folder", help="Input folder containing JPG files")

    output_group = parser.add_mutually_exclusive_group(required=False)
    output_group.add_argument("-o", "--output", help="Output JPG file path")
    output_group.add_argument("-O", "--output-folder", help="Output folder for batch mode")

    parser.add_argument("-q", "--quality", type=int, default=85, help="JPG quality (1-95, default 85)")
    parser.add_argument("--max-width", type=int, default=None, help="Optional max width to resize")
    parser.add_argument("--max-height", type=int, default=None, help="Optional max height to resize")

    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively process subfolders (only with --input-folder)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    quality = args.quality
    verbose = args.verbose

    if not validate_quality(quality) or not validate_recursive(args):
        return

    # Batch Mode
    if args.input_folder:
        input_folder = Path(args.input_folder)
        output_folder = Path(args.output_folder) if args.output_folder else Path(f"{input_folder}_compressed")
        recursive = args.recursive

        if not validate_args_batch(input_folder):
            return

        extensions = [".jpg", ".jpeg"]
        jpg_files = [
            f for f in (input_folder.rglob("*") if recursive else input_folder.glob("*"))
            if f.suffix.lower() in extensions
        ]

        if not jpg_files:
            print(" ❌ \033[1;35mNo JPG files found in the input folder.\033[0m")
            return

        output_folder.mkdir(parents=True, exist_ok=True)

        for jpg in jpg_files:
            relative_path = jpg.relative_to(input_folder)
            output_file = output_folder / relative_path

            output_file.parent.mkdir(parents=True, exist_ok=True)

            log(verbose=verbose,
                message=f"\n 🚀 \033[1;37m Processing:\033[1;32m  {jpg.name}\033[0m")

            compress_image(
                input_file=jpg,
                output_file=output_file,
                quality=args.quality,
                max_width=args.max_width,
                max_height=args.max_height,
            )

            input_size = str(os.path.getsize(jpg) / 1000000)
            output_size = str(os.path.getsize(output_file) / 1000000)
            log(verbose=verbose,
                message=f" ✅ \033[1;37m Compression completed:\n\033[1;32m   Input file size: {input_size} MB\n   Output file size: {output_size} MB\033[0m")

        log(verbose=verbose,
            message=f"\n\033[1;37m  Batch compression completed.\033[1;32m {len(jpg_files)}\033[1;37m files processed and saved at:\033[1;32m {output_folder}/\033[0m")

    # Single File Mode
    else:
        input_file = args.input
        output_file = args.output if args.output else f"{Path(input_file).stem}_compressed{Path(input_file).suffix}"

        if not validate_args_single_file(input_file=input_file, output_file=output_file):
            return

        log(verbose=verbose,
            message=f"\n 🚀 \033[1;37m Processing:\033[1;32m  {Path(input_file).name}\033[0m")

        compress_image(
            input_file=input_file,
            output_file=output_file,
            quality=args.quality,
            max_width=args.max_width,
            max_height=args.max_height,
        )

        input_size = str(os.path.getsize(input_file) / 1000000)
        output_size = str(os.path.getsize(output_file) / 1000000)
        log(verbose=verbose,
            message=f" ✅ \033[1;37m Compression completed:\n\033[1;32m   Input file size: {input_size} MB\n   Output file size: {output_size} MB\033[0m")


if __name__ == "__main__":
    main()
