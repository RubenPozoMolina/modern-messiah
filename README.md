# modern-messiah

## Requirements

To convert the book from text to mobi and epub you need to have installed calibre

https://manual.calibre-ebook.com/index.html

To execute with a local model you need to have a gpu

## Prepare environment

### Setting up Python Virtual Environment

1. Create a virtual environment:
    ```bash
    python -m venv venv
    ```
2. Activate the virtual environment:
   - On Windows:
    ```bash
    .\venv\Scripts\activate
    ```
    - On macOS/Linux:
    ```bash
    source venv/bin/activate
    ```

3. Install required packages:
    ```bash
    pip install -r requirements.txt
    ```

Note: Make sure you have Python 3.x installed on your system before creating the virtual environment.