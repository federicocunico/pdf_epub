# Convert pdf to text using OCR

Custom tools for trying to convert pdf to text using OCR.

## Requirements

```
conda create --name ocr python=3.8
```

### For easyocr (optional)

```
pip install torch torchvision
```
or
```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### For pytesseract
```bash
sudo apt-get install tesseract-ocr
```

```bash
pip install pytesseract
```

Windows: `choco install tesseract`
Linux: `apt-get install tesseract-ocr`


### General requirements
```
pip install pyautogui Pillow fpdf2 imagehash Pillow keyboard
```


## Running 
First of all, run `get_images.py` 
Then, run `ocr_to_text.py` setting the correct folder name in the code.