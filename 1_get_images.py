import numpy as np
import pyautogui
import time
from PIL import Image, ImageTk
import os
from fpdf import FPDF
import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
import keyboard
import shutil


def image_compare(image_1, image_2):
    if isinstance(image_1, str):
        image_1 = Image.open(image_1)
    if isinstance(image_2, str):
        image_2 = Image.open(image_2)
    arr1 = np.array(image_1)
    arr2 = np.array(image_2)
    if arr1.shape != arr2.shape:
        return False
    maxdiff = np.max(np.abs(arr1 - arr2))
    return maxdiff == 0


def get_folder_name():
    root = tk.Tk()
    root.withdraw()  # Nasconde la finestra principale
    folder_name = simpledialog.askstring(
        "Input", "Nome della cartella di destinazione:", parent=root
    )
    return folder_name


def select_bbox(image_path):
    class BoundingBoxSelector:
        def __init__(self, root, image_path):
            self.root = root
            self.image_path = image_path
            self.image = Image.open(image_path)
            self.canvas = tk.Canvas(root, width=self.image.width, height=self.image.height)
            self.canvas.pack()
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            self.rect = None
            self.start_x = None
            self.start_y = None
            self.bbox = None
            self.canvas.bind("<ButtonPress-1>", self.on_button_press)
            self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
            self.done = False

        def on_button_press(self, event):
            self.start_x = event.x
            self.start_y = event.y
            self.rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y, outline="red"
            )

        def on_mouse_drag(self, event):
            cur_x, cur_y = (event.x, event.y)
            self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

        def on_button_release(self, event):
            end_x, end_y = (event.x, event.y)
            self.bbox = (self.start_x, self.start_y, end_x, end_y)
            self.done = True
            self.root.quit()

        def get_bbox(self):
            self.root.mainloop()
            return self.bbox

    # root = tk.Tk()
    root = tk.Toplevel()
    selector = BoundingBoxSelector(root, image_path)
    bbox = selector.get_bbox()
    root.destroy()
    return bbox


def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result


def take_screenshot_and_crop(n, folder_name, bbox1, bbox2):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    fulls = []
    for i in range(n):
        # Take screenshot
        screenshot = pyautogui.screenshot()

        # Convert screenshot to hash

        # Compare with previous hash
        if len(fulls) > 0 and image_compare(screenshot, fulls[-1]):
            print("Screenshots are identical, stopping...")
            break

        # Update previous hash

        # Save full screenshot
        screenshot_path = os.path.join(folder_name, f"full_screenshot_{i}.png")
        screenshot.save(screenshot_path)
        fulls.append(screenshot_path)

        # Crop and save the first bbox
        crop1 = screenshot.crop(bbox1)
        crop1_path = os.path.join(folder_name, f"{str(i*2).zfill(6)}.png")
        crop1.save(crop1_path)

        # Crop and save the second bbox
        crop2 = screenshot.crop(bbox2)
        crop2_path = os.path.join(folder_name, f"{str(i*2+1).zfill(6)}.png")
        crop2.save(crop2_path)

        # # read both, and pad with white if necessary (not resize)
        # img1 = Image.open(crop1_path)
        # img2 = Image.open(crop2_path)
        # # use add_margin
        # if img1.size[1] > img2.size[1]:
        #     img2 = add_margin(img2, 0, 0, img1.size[1] - img2.size[1], 0, (255, 255, 255))
        # elif img2.size[1] > img1.size[1]:
        #     img1 = add_margin(img1, 0, 0, img2.size[1] - img1.size[1], 0, (255, 255, 255))
        # # save them back
        # img1.save(crop1_path)
        # img2.save(crop2_path)

        # Press Page Down
        pyautogui.press("pagedown")

        # Check for 'Q' key press to quit
        if keyboard.is_pressed("q"):
            print("Exit requested, stopping...")
            break

        time.sleep(0.05)  # Wait for a second before taking the next screenshot

    [os.remove(full) for full in fulls]  # Delete full screenshots


def create_pdf_from_images(folder_name, pdf_name):
    pdf = FPDF()
    images = [img for img in os.listdir(folder_name) if img.endswith(".png")]
    images.sort(key=lambda x: int(x.split(".")[0]))  # Sort images numerically

    for image in images:
        image_path = os.path.join(folder_name, image)
        cover = Image.open(image_path)
        width, height = cover.size

        # Convert pixel in mm with 1px=0.264583 mm
        width, height = float(width * 0.264583), float(height * 0.264583)

        pdf.add_page(format=(width, height))

        pdf.image(image_path, 0, 0, width, height)

    pdf.output(pdf_name, "F")


if __name__ == "__main__":
    N = 2000  # Number of times to take screenshots and page down
    folder_name = get_folder_name()
    if not folder_name:
        print("Folder name not provided. Exiting.")
        exit()

    if os.path.isdir(folder_name):
        # ask if the user wants to overwrite the folder
        if not messagebox.askyesno(
            "Warning", "Folder already exists. Do you want to overwrite it?"
        ):

            print("Folder already exists. Exiting.")
            exit()
        else:
            # delete the folder and create a new one

            shutil.rmtree(folder_name)
            os.makedirs(folder_name)

    time.sleep(1)
    # Take an initial screenshot to allow the user to select bounding boxes
    initial_screenshot_path = "initial_screenshot.png"
    initial_screenshot = pyautogui.screenshot()
    initial_screenshot.save(initial_screenshot_path)

    bbox1 = select_bbox(initial_screenshot_path)
    if not bbox1:
        print("First bounding box not selected. Exiting.")
        exit()
    messagebox.showinfo("Info", "Seleziona la seconda regione")

    bbox2 = select_bbox(initial_screenshot_path)
    if not bbox2:
        print("Second bounding box not selected. Exiting.")
        exit()

    time.sleep(1)

    pdf_name = f"{folder_name}.pdf"

    take_screenshot_and_crop(N, folder_name, bbox1, bbox2)
    create_pdf_from_images(folder_name, pdf_name)
    print(f"PDF created successfully: {pdf_name}")

    # Delete the folder with images
    # shutil.rmtree(folder_name)
    # print(f"Deleted folder: {folder_name}")
