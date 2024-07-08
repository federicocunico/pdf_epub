from tkinter import filedialog
import easyocr
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from glob import glob

reader = easyocr.Reader(["en"])  # this needs to run only once to load the model into memory


def pick_folder():
    folder = filedialog.askdirectory()
    return folder


def get_all_text(img):
    texts = []
    result = reader.readtext(img)
    for r in result:
        t = r[1]

        # if t[-1] == "-":
        #     t = t[:-1]

        texts.append(t)
    return texts


dst = "test"

files = glob(f"{dst}/*.png")
files.sort()
assert len(files) > 0, "No images found in the folder"

all_texts = [None] * len(files)

with ThreadPoolExecutor() as executor:
    futures = {executor.submit(get_all_text, file): idx for idx, file in enumerate(files)}
    for future in tqdm(as_completed(futures), total=len(files)):
        idx = futures[future]
        all_texts[idx] = future.result()

# todo: merge lines based on final - character

all_texts = [t for texts in all_texts for t in texts]

print(all_texts)
