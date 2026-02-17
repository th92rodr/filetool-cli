#!/usr/bin/env python3

###############################################################
### PROJECT: PDF Compressor and Metadata Remover CLI
### SCRIPT: pdftool
### VERSION: v1.0
### DESCRIPTION:
### A script to make compressing pdf files more easily by automating Ghostscript commands.
### ############################################################

import argparse
import os, re, subprocess, sys
from pathlib import Path
from pypdf import PdfReader, PdfWriter


COMPRESSION_LEVELS = {
    "screen",
    "ebook",
    "printer",
    "prepress",
    "default",
}


def strip_pdf_metadata(input_path: str, output_path: str) -> None:
    """
    Remove all metadata (Title, Author, Metadata streams, etc.) from a PDF.

    Args:
        input_path (str): Path to the input PDF file.
        output_path (str): Path to save the output PDF without metadata.
    """

    reader = PdfReader(input_path)
    writer = PdfWriter()

    # Copy only the pages
    for page in reader.pages:
        writer.add_page(page)

    # Remove classic document info dictionary (/Info)
    writer._info = None

    # Remove XMP metadata
    writer.add_metadata({})

    # Remove /Metadata stream if present
    if "/Metadata" in writer._root_object:
        del writer._root_object["/Metadata"]

    # Write the clean PDF
    with open(output_path, "wb") as out_file:
        writer.write(out_file)


def compress_pdf(input_path: str, output_path: str, quality: str = "ebook") -> None:
    """
    Compress a PDF using Ghostscript.

    Args:
        input_path (str): Input PDF path.
        output_path (str): Output compressed PDF path.
        quality (str): One of screen, ebook, printer, prepress, default.
    """

    gs_command = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.6",
        f"-dPDFSETTINGS=/{quality}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path,
    ]

    try:
        subprocess.run(gs_command, check=True)
    except subprocess.CalledProcessError:
        print(" ❌ \033[1;35mGhostscript compression failed.\033[0m", file=sys.stderr)
        sys.exit(1)


def process_file(input_file: str, output_file: str, compression: str, delete_original: bool = False) -> None:
    """
    Args:
        input_file (str): Path to the input PDF file.
        output_file (str): Path to save the output PDF file.
        compression (str): Compression level.
        delete_original (bool): Whether to delete the original PDF file after successful processing.
    """

    temp_file = "__temp.pdf"

    try:
        compress_pdf(input_path=input_file, output_path=temp_file, quality=compression)
        strip_pdf_metadata(input_path=temp_file, output_path=output_file)

        # Only delete original file if output exists and flag is set
        if delete_original and os.path.isfile(output_file):
            os.remove(input_file)

    finally:
        # Delete temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)


def single_file_mode(args) -> None:
    input_file = args.input
    output_file = args.output if args.output else f"{Path(input_file).stem}_compressed.pdf"

    compression = args.compression
    delete_original = args.delete_original
    force = args.force
    verbose = args.verbose

    validate_compression_level(compression=compression)
    validate_args_single_file(input_file=input_file, output_file=output_file, force=force)

    log(verbose=verbose,
        message=f"\n 🚀 \033[1;37m Processing:\033[1;32m  {Path(input_file).name}\033[0m")

    input_size = str(os.path.getsize(input_file) / 1000000)

    process_file(input_file=input_file, output_file=output_file, compression=compression, delete_original=delete_original)

    output_size = str(os.path.getsize(output_file) / 1000000)

    log(verbose=verbose,
        message=f" ✅ \033[1;37m Compression completed:\n\033[1;32m   Input file size: {input_size} MB\n   Output file size: {output_size} MB\033[0m")


def batch_file_mode(args) -> None:
    input_folder = Path(args.input_folder)
    output_folder = Path(args.output_folder) if args.output_folder else Path(f"{input_folder}_compressed")

    compression = args.compression
    delete_original = args.delete_original
    recursive = args.recursive
    verbose = args.verbose

    validate_compression_level(compression=compression)
    validate_args_batch_file(input_folder=input_folder)

    pattern = "**/*.pdf" if recursive else "*.pdf"
    pdf_files = list(input_folder.glob(pattern=pattern, case_sensitive=False))

    if not pdf_files:
        print(" ❌ \033[1;35mNo PDF files found in the input folder.\033[0m")
        return

    output_folder.mkdir(parents=True, exist_ok=True)

    for pdf in pdf_files:
        relative_path = pdf.relative_to(input_folder)
        output_file = output_folder / relative_path

        output_file.parent.mkdir(parents=True, exist_ok=True)

        log(verbose=verbose,
            message=f"\n 🚀 \033[1;37m Processing:\033[1;32m  {pdf.name}\033[0m")

        input_size = str(os.path.getsize(pdf) / 1000000)

        process_file(input_file=pdf, output_file=output_file, compression=compression, delete_original=delete_original)

        output_size = str(os.path.getsize(output_file) / 1000000)

        log(verbose=verbose,
            message=f" ✅ \033[1;37m Compression completed:\n\033[1;32m   Input file size: {input_size} MB\n   Output file size: {output_size} MB\033[0m")

    log(verbose=verbose,
        message=f"\n\033[1;37m  Batch compression completed.\033[1;32m {len(pdf_files)}\033[1;37m files processed and saved at:\033[1;32m {output_folder}/\033[0m")


def validate_compression_level(compression: str) -> None:
    # Check if the compression level is valid
    if compression not in COMPRESSION_LEVELS:
        print(f" ❌ \033[1;35mInvalid compression level:\033[1;36m {compression}\033[0m", file=sys.stderr)
        sys.exit(2)


def validate_args_single_file(input_file: str, output_file: str, force: bool = False) -> None:
    # Check if the input file exists
    if not os.path.isfile(input_file):
        print(f" ❌ \033[1;35mInput file does not exist:\033[1;36m {input_file}\033[0m", file=sys.stderr)
        sys.exit(2)

    # Check if the input file is a .pdf file
    if not input_file.lower().endswith(".pdf"):
        print(f" ❌ \033[1;35mInput file needs to be a .pdf file:\033[1;36m {input_file}\033[0m", file=sys.stderr)
        sys.exit(2)

    # Check if the input file name is safe
    if re.search("[|;`><{}#*]", input_file):
        print(f" ❌ \033[1;35mInput file \033[1;36m\"{input_file}\"\033[1;35m contains invalid characters:\033[1;36m [ | ; ` > < {{ }} # *]\033[0m", file=sys.stderr)
        sys.exit(2)

    # Check if the output file name is safe
    if re.search('[|;`><{}#*]', output_file):
        print(f" ❌ \033[1;35mOutput file \033[1;36m\"{output_file}\"\033[1;35m contains invalid characters:\033[1;36m [ | ; ` > < {{ }} # *]\033[0m", file=sys.stderr)
        sys.exit(2)

    # Check if the output file is a .pdf file
    if not output_file.lower().endswith(".pdf") and not force:
        ask = f" ❔ \033[1;31mOutput file \033[1;36m\"{output_file}\"\033[1;31m does not end with \".pdf\". Are you sure you want to continue?\033[1;36m (y/n)\033[0m "
        confirm = input(ask)
        if confirm.lower() not in ("yes", "y"):
            sys.exit(2)

    # Check to make sure the user really wants to overwrite the existing file with the new output file
    if os.path.isfile(output_file) and not force:
        ask = f" ❔ \033[1;31mOutput file \033[1;36m\"{output_file}\"\033[1;31m already exists. Are you sure you want to overwrite it?\033[1;36m (y/n)\033[0m "
        confirm = input(ask)
        if confirm.lower() not in ("yes", "y"):
            sys.exit(2)


def validate_args_batch_file(input_folder: str) -> None:
    # Check if the input folder exists
    if not os.path.isdir(input_folder):
        print(f" ❌ \033[1;35mInput folder does not exist:\033[1;36m {input_folder}\033[0m", file=sys.stderr)
        sys.exit(2)


def log(message: str, verbose: bool) -> None:
    if verbose:
        print(message)


def main():
    parser = argparse.ArgumentParser(
        description="Compress PDF files and remove metadata. Supports single file or batch folder processing.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-i", "--input", help="Input PDF file path")
    input_group.add_argument("-I", "--input-folder", help="Input folder containing PDF files")

    output_group = parser.add_mutually_exclusive_group(required=False)
    output_group.add_argument("-o", "--output", help="Output PDF file path")
    output_group.add_argument("-O", "--output-folder", help="Output folder for batch mode")

    parser.add_argument(
        "-c",
        "--compression",
        type=str,
        default="ebook",
        help=(
            "Compression Level:\n"
            "Option     Description                              Quality     File Size\n"
            "---------  ---------------------------------------  ----------  ---------\n"
            "screen     Lowest quality, smallest size            72 dpi      Tiny\n"
            "ebook      Medium quality for e-books               150 dpi     Small\n"
            "printer    High quality for printing                300 dpi     Larger\n"
            "prepress   Maximum quality for professional use     300 dpi+    Largest\n"
            "default    Similar to screen                        ~72 dpi     Small\n"
        ),
    )

    parser.add_argument("--delete-original", action="store_true", help="Delete original PDF files after successful compression")
    parser.add_argument("-f", "--force", action="store_true", help="Overwrite output files without confirmation")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively process subfolders (only with --input-folder)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Batch Mode
    if args.input_folder:
        batch_file_mode(args=args)

    # Single File Mode
    else:
        single_file_mode(args=args)


if __name__ == "__main__":
    main()
