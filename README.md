# filetool-cli

A simple CLI toolkit to compress PDF and image files while removing metadata. Supports batch processing, recursive folder scanning, and customizable compression levels. Powered by Python and Ghostscript.

Supports:

- ✅ PDF compression with Ghostscript
- ✅ Image compression using Pillow
- ✅ Metadata removal from PDFs and images
- ✅ Batch processing of multiple files or entire folders
- ✅ Recursive folder scanning
- ✅ Customizable compression levels
- ✅ Verbose or silent execution

---

## 🎯 Features

- 📄 **PDF Tool (`pdftool`)**

  - Compress PDF files at different quality levels using Ghostscript
  - Remove all metadata (Title, Author, Info dictionary, XMP, Metadata streams)
  - Handle case-insensitive file extensions (`.pdf`, `.PDF`, `.pDf`, …)
  - **Batch mode**
    - Automatically create the output folder if it doesn’t exist
    - If no output folder is specified, defaults to: `<input_folder_name>_compressed`
    - In recursive mode: preserve folder structure, keep filenames/extensions, skip non-PDF files safely
  - **Single file mode**
    - If no output file is specified, defaults to: `<input_file_name>_compressed.<extension>`
    - If the output file already exists, asks for confirmation before overwriting

- 🖼️ **Image Tool (`imgtool`)**

  - Compress JPG images with adjustable quality (1–95)
  - Strip all metadata (EXIF, GPS, camera info, copyright)
  - Optional image resizing by width/height
  - Handle case-insensitive file extensions (`.jpg`, `.jpeg`, `.JPG`, `.JPEG`, …)
  - **Batch mode**
    - Automatically create the output folder if it doesn’t exist
    - If no output folder is specified, defaults to: `<input_folder_name>_compressed`
    - In recursive mode: preserve folder structure, keep filenames/extensions, skip non-image files safely
  - **Single file mode**
    - If no output file is specified, defaults to: `<input_file_name>_compressed.<extension>`
    - If the output file already exists, asks for confirmation before overwriting

---

## 🧭 Installation

- **Python 3.12.3**
- **Ghostscript 9.55.0**

### 1. Clone the repository:

```bash
git clone git@github.com:th92rodr/filetool-cli.git
cd filetool-cli
```

### 2. Create a python virtual environment:

```bash
python3 -m virtualenv venv
source venv/bin/activate
```

### 3. Install dependencies:

```bash
pip install -r requirements.txt
```

### 4. Install Ghostscript (required for PDF compression):

- On Ubuntu/Debian:

```bash
sudo apt install ghostscript
```

- On macOS:

```bash
brew install ghostscript
```

The current version being used is: **Ghostscript 9.55.0**

You can check your Ghostscript version with:

```bash
gs --version
```

---

## 🕹️ Usage

### 🔹 PDF Tool

```bash
python pdftool.py --input input.pdf --output output.pdf --compression ebook --verbose
```

#### ✅ Compression Levels

| Option   | Description                          | DPI      | File Size |
| -------- | ------------------------------------ | -------- | --------- |
| screen   | Lowest quality, smallest size        | 72 dpi   | Tiny      |
| ebook    | Medium quality for e-books           | 150 dpi  | Small     |
| printer  | High quality for printing            | 300 dpi  | Larger    |
| prepress | Maximum quality for professional use | 300+ dpi | Largest   |
| default  | Similar to `screen`                  | ~72 dpi  | Small     |

#### 🔧 Command-Line Options

| Argument              | Description                                            |
| --------------------- | ------------------------------------------------------ |
| `-i, --input`         | Input PDF file path                                    |
| `-o, --output`        | Output PDF file path                                   |
| `-I, --input-folder`  | Input folder (for batch mode)                          |
| `-O, --output-folder` | Output folder (for batch mode)                         |
| `-c, --compression`   | Compression level (`screen`, `ebook`, ...)             |
| `--delete-original`   | Delete original PDF files after successful compression |
| `-f, --force`         | Overwrite output files without confirmation            |
| `-r, --recursive`     | Process subfolders (only with input-folder)            |
| `-v, --verbose`       | Print detailed output                                  |
| `-h, --help`          | Show all command-line options                          |

#### ✅ Examples

- Compress a PDF with medium quality:

```bash
python pdftool.py -i input.pdf -o output.pdf -c ebook
```

- Compress all PDFs in a folder recursively:

```bash
python pdftool.py -I ./pdfs -O ./compressed -r -c printer
```

---

### 🔹 Image Tool

```bash
python imgtool.py --input input.jpg --output output.jpg --quality 75 --verbose
```

#### 🔧 Command-Line Options

| Argument              | Description                                            |
| --------------------- | ------------------------------------------------------ |
| `-i, --input`         | Input image file path                                  |
| `-o, --output`        | Output image file path                                 |
| `-I, --input-folder`  | Input folder (for batch mode)                          |
| `-O, --output-folder` | Output folder (for batch mode)                         |
| `-q, --quality`       | JPG quality (default 85, range 1-95)                   |
| `--max-width`         | Max width to resize (optional)                         |
| `--max-height`        | Max height to resize (optional)                        |
| `--delete-original`   | Delete original JPG files after successful compression |
| `-f, --force`         | Overwrite output files without confirmation            |
| `-r, --recursive`     | Process subfolders (only with input-folder)            |
| `-v, --verbose`       | Print detailed output                                  |
| `-h, --help`          | Show all command-line options                          |

#### ✅ Examples

- Compress a JPG image with quality 70:

```bash
python imgtool.py -i input.jpg -o output.jpg -q 70
```

- Compress all JPG images in a folder recursively:

```bash
python imgtool.py -I ./images -O ./compressed -r -q 70
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE.md).

---

## Author

[**@th92rodr**](https://github.com/th92rodr)
