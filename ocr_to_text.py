import re
from tkinter import filedialog

import cv2
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from glob import glob

PARALLEL = True


def init_ocr(ocr, lang):
    if ocr == "easyocr":
        import easyocr

        return easyocr.Reader([lang])
    elif ocr == "tesseract":
        from pytesseract import pytesseract

        pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        return pytesseract
    else:
        raise ValueError(f"OCR {ocr} not supported")


def preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return binary_image


def get_all_text(img_path):
    texts = []
    preprocessed_image = preprocess_image(img_path)
    result = read_text(preprocessed_image, reader, ocr)
    texts.extend(result)
    return texts


def read_text(img, reader, ocr="easyocr"):
    if ocr == "easyocr":
        result = reader.readtext(img)
        texts = [r[1] for r in result]
    elif ocr == "tesseract":
        custom_config = r"--oem 3 --psm 3"  # Default configuration; adjust
        texts = reader.image_to_string(img, config=custom_config)
        texts = texts.split("\n")
        texts = [t for t in texts if t.strip() != ""]
    else:
        raise ValueError(f"OCR {ocr} not supported")

    # out = postprocess_text(texts)
    return texts

def postprocess_text(sentences):
    import re
    
    def join_hyphenated(sentences):
        """
        Joins hyphenated words that are broken across lines.
        """
        new_sentences = []
        buffer = ""
        for sentence in sentences:
            if buffer:
                sentence = buffer + sentence
                buffer = ""
            if sentence.endswith('-'):
                buffer = sentence[:-1]
            else:
                new_sentences.append(sentence)
        if buffer:
            new_sentences.append(buffer)
        return new_sentences

    def fix_quotes(sentences):
        """
        Fixes mismatched or broken quotes.
        """
        text = ' '.join(sentences)
        # Replace single straight quotes with curly quotes for speech
        text = re.sub(r'“([^”]*)”', r'“\1”', text)  # Fix curly quotes
        text = re.sub(r'"([^"]*)"', r'“\1”', text)  # Change straight quotes to curly quotes
        # Rejoin sentences split at quote boundaries
        fixed_text = text.replace('“ ', '“').replace(' ”', '”')
        return fixed_text

    # Step 1: Join hyphenated sentences
    joined_sentences = join_hyphenated(sentences)
    
    # Step 2: Fix quotes in the text
    processed_text = fix_quotes(joined_sentences)
    
    processed_text = processed_text.replace("“", "\"").replace("”", "\"" ).replace('‘', "'").replace('’', "'" )
    return processed_text

def pick_folder():
    folder = filedialog.askdirectory()
    return folder


# def get_all_text(img):
#     texts = []
#     result = read_text(img, reader, ocr)
#     for t in result:
#         # if t[-1] == "-":
#         #     t = t[:-1]
#         texts.append(t)
#     return texts


if __name__ == "__main__":

    FOLDER_WITH_IMAGES = "test"

    ocr = "tesseract"
    lang = "en"
    reader = init_ocr(ocr, lang)


    files = glob(f"{FOLDER_WITH_IMAGES}/*.png")
    files.sort()
    assert len(files) > 0, "No images found in the folder"

    all_texts = [None] * len(files)

    if PARALLEL:
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(get_all_text, file): idx for idx, file in enumerate(files)}
            for future in tqdm(as_completed(futures), total=len(files)):
                idx = futures[future]
                all_texts[idx] = future.result()
    else:
        for idx, file in enumerate(tqdm(files)):
            all_texts[idx] = get_all_text(file)

    all_texts = [t for texts in all_texts for t in texts]

    single_line_text = postprocess_text(all_texts)

    with open("output.txt", "w", encoding="utf-8") as f:
        # for text in all_texts:
        #     f.write(text + " ")
        f.write(single_line_text)

    print(f"Output saved to output.txt")
