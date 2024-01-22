import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import TK_normalization_image as tni

class ImageSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Selector")

        # Variables
        self.image_path = None
        self.selection_coordinates = None
        self.dark_spots_coordinates = None
        self.threshold_value = tk.DoubleVar(value=50.0)  # Initial threshold value

        # GUI components
        self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=10)

        self.main_canvas = tk.Canvas(root)                              # Main canvas
        self.main_canvas.pack(expand=tk.YES, fill=tk.BOTH)
        self.main_canvas.bind("<ButtonPress-1>", self.on_press)
        self.main_canvas.bind("<B1-Motion>", self.on_drag)
        self.main_canvas.bind("<ButtonRelease-1>", self.on_release)

        self.selection_label = tk.Label(root, text="Selection Coordinates:")
        self.selection_label.pack()

        self.selection_display = tk.Label(root, text="")
        self.selection_display.pack()

        self.selected_canvas = tk.Canvas(root, width=100, height=100)  # Canvas for selected region
        self.selected_canvas.pack()

        self.threshold_scale_label = tk.Label(root, text="Threshold:")
        self.threshold_scale_label.pack()

        self.threshold_scale = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.threshold_value, command=self.find_dark_spots)
        self.threshold_scale.pack()

        self.negative_canvas = tk.Canvas(root, width=100, height=100)  # Canvas for Negative
        self.negative_canvas.pack()

        self.find_dark_spots_button = tk.Button(root, text="Find Dark Spots", command=self.find_dark_spots)
        self.find_dark_spots_button.pack(pady=10)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if file_path:
            self.image_path = file_path
            self.display_image()

    def display_image(self):
        image = Image.open(self.image_path)
        self.mini_image = tni.main_resize(image, 600)
        self.image_tk = ImageTk.PhotoImage(self.mini_image)
        self.main_canvas.config(width=self.image_tk.width(), height=self.image_tk.height())
        self.main_canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)

    def on_press(self, event):
        self.start_x = self.main_canvas.canvasx(event.x)
        self.start_y = self.main_canvas.canvasy(event.y)

    def on_drag(self, event):
        cur_x = self.main_canvas.canvasx(event.x)
        cur_y = self.main_canvas.canvasy(event.y)
        self.main_canvas.delete("selection_rectangle")
        self.main_canvas.create_rectangle(self.start_x, self.start_y, cur_x, cur_y, outline="red", tags="selection_rectangle")

    def on_release(self, event):
        end_x = self.main_canvas.canvasx(event.x)
        end_y = self.main_canvas.canvasy(event.y)
        self.selection_coordinates = (self.start_x, self.start_y, end_x, end_y)
        self.display_selection()

    def display_selection(self):
        if self.selection_coordinates:
            self.selection_display.config(text=f"Selection Coordinates: {self.selection_coordinates}")

            # Extract the selected region from the original image
            #selected_image = Image.open(self.image_path).crop(self.selection_coordinates)
            selected_image = self.mini_image.crop(self.selection_coordinates)
            selected_image_tk = ImageTk.PhotoImage(selected_image)

            # Display the selected region in the second canvas
            self.selected_canvas.config(width=selected_image_tk.width(), height=selected_image_tk.height())
            self.selected_canvas.create_image(0, 0, anchor=tk.NW, image=selected_image_tk)
            self.selected_canvas.image = selected_image_tk  # Keep a reference to avoid garbage collection issues

            self.selected_canvas.width = selected_image_tk.width()
            self.selected_canvas.height = selected_image_tk.height()

       # Update dark spots when the selection changes
        self.find_dark_spots()

    def find_dark_spots(self, _=None):
        if self.image_path and self.selection_coordinates:
            # Read the entire image
            full_image = cv2.imread(self.image_path)

            # Convert the selected region to grayscale
            selected_region = full_image[int(self.selection_coordinates[1]):int(self.selection_coordinates[3]),
                             int(self.selection_coordinates[0]):int(self.selection_coordinates[2])]
            gray_selected_region = cv2.cvtColor(selected_region, cv2.COLOR_BGR2GRAY)

            # Apply threshold to find dark spots
            _, thresholded = cv2.threshold(gray_selected_region, self.threshold_value.get(), 255, cv2.THRESH_BINARY_INV)

            # Find contours of dark spots
            contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Extract coordinates of dark spots with area more than 100 pixels
            dark_spots_coordinates = [cv2.boundingRect(contour) for contour in contours if cv2.contourArea(contour) > 50]

            # Update the attribute and display it
            self.dark_spots_coordinates = dark_spots_coordinates
            self.display_dark_spots()
            self.thresholded=thresholded    #######################################################################

            self.negative_canvas.config(width=self.selected_canvas.width, height=self.selected_canvas.height)
            negative_im = Image.fromarray(self.thresholded)
            negative_img = ImageTk.PhotoImage(image=negative_im)
            self.negative_canvas.create_image(0, 0, anchor=tk.NW, image=negative_img)
            self.negative_canvas.image = negative_img

    def display_dark_spots(self):
        # Clear existing rectangles
        self.main_canvas.delete("dark_spot_rectangle")

        if self.dark_spots_coordinates:
            # Draw red rectangles around dark spots in the selected region
            for (x, y, w, h) in self.dark_spots_coordinates:
                x += self.selection_coordinates[0]  # Adjust x-coordinate based on the selection
                y += self.selection_coordinates[1]  # Adjust y-coordinate based on the selection
                self.main_canvas.create_rectangle(x, y, x + w, y + h, outline="red", width=2, tags="dark_spot_rectangle")

            print("Dark Spots Coordinates:", self.dark_spots_coordinates)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSelectorApp(root)
    root.mainloop()
