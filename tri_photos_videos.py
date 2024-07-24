import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import cv2
from pillow_heif import register_heif_opener

register_heif_opener()


class MediaOrganizerApp:
    def __init__(self, root, unordered_base_path, subfolders_base_path):
        self.root = root
        self.unordered_base_path = unordered_base_path
        self.subfolders_base_path = subfolders_base_path
        self.current_file_index = 0
        self.unordered_files = self.get_unordered_files()
        self.subfolders = self.get_subfolders()

        self.setup_ui()

        if self.unordered_files:
            self.load_media(self.unordered_files[self.current_file_index])
        else:
            messagebox.showinfo(
                "Info", "No unordered files found in the directory.")

    def get_unordered_files(self):
        files = [f for f in os.listdir(self.unordered_base_path) if os.path.isfile(
            os.path.join(self.unordered_base_path, f))]
        return files

    def get_subfolders(self):
        subfolders = [f.name for f in os.scandir(
            self.subfolders_base_path) if f.is_dir()]
        return subfolders

    def check_file_presence(self, filename):
        for folder in self.subfolders:
            folder_path = os.path.join(self.subfolders_base_path, folder)
            if filename in os.listdir(folder_path):
                return f"Already present in {folder}"
        return "Not present yet"

    def setup_ui(self):
        self.root.title("Media Organizer")

        self.file_info_label = tk.Label(self.root, text="")
        self.file_info_label.pack(pady=10)

        self.image_label = tk.Label(self.root)
        self.image_label.pack(pady=10)

        self.folder_dropdown = ttk.Combobox(self.root, values=self.subfolders)
        self.folder_dropdown.pack(pady=10)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.move_button = tk.Button(
            button_frame, text="Move to Folder", command=self.move_file)
        self.move_button.grid(row=0, column=0, padx=5)

        self.skip_button = tk.Button(
            button_frame, text="Skip", command=self.skip_media)
        self.skip_button.grid(row=0, column=1, padx=5)

        self.new_folder_button = tk.Button(
            self.root, text="Create New Folder", command=self.create_new_folder)
        self.new_folder_button.pack(pady=10)

    def load_media(self, filename):
        file_path = os.path.join(self.unordered_base_path, filename)
        file_presence_info = self.check_file_presence(filename)
        self.file_info_label.config(text=f"{filename} - {file_presence_info}")

        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.heic')):
            image = Image.open(file_path)
            image.thumbnail((500, 500))
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
        elif filename.lower().endswith(('.mp4', '.mov')):
            cap = cv2.VideoCapture(file_path)
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (500, 500))
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo)
                self.image_label.image = photo
            cap.release()

    def move_file(self):
        selected_folder = self.folder_dropdown.get()
        if selected_folder:
            current_file = self.unordered_files[self.current_file_index]
            source_path = os.path.join(self.unordered_base_path, current_file)
            destination_path = os.path.join(
                self.subfolders_base_path, selected_folder, current_file)
            shutil.move(source_path, destination_path)
            self.unordered_files.pop(self.current_file_index)
            if self.unordered_files:
                self.current_file_index %= len(self.unordered_files)
                self.load_media(self.unordered_files[self.current_file_index])
            else:
                self.all_files_processed()
        else:
            messagebox.showwarning(
                "Warning", "Please select a folder to move the file to.")

    def create_new_folder(self):
        folder_name = simpledialog.askstring(
            "New Folder", "Enter folder name:")
        if folder_name:
            new_folder_path = os.path.join(
                self.subfolders_base_path, folder_name)
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
                self.subfolders.append(folder_name)
                self.folder_dropdown.config(values=self.subfolders)
            else:
                messagebox.showwarning("Warning", "Folder already exists.")

    def skip_media(self):
        self.unordered_files.pop(self.current_file_index)
        if self.unordered_files:
            self.current_file_index %= len(self.unordered_files)
            self.load_media(self.unordered_files[self.current_file_index])
        else:
            self.all_files_processed()

    def all_files_processed(self):
        messagebox.showinfo("Info", "All files have been organized.")
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    unordered_base_path = filedialog.askdirectory(
        title="Select Folder with Unordered Files")
    if unordered_base_path:
        subfolders_base_path = filedialog.askdirectory(
            title="Select Folder Containing Subfolders")
        if subfolders_base_path:
            app = MediaOrganizerApp(
                root, unordered_base_path, subfolders_base_path)
            root.mainloop()
        else:
            messagebox.showinfo("Info", "No subfolder directory selected.")
    else:
        messagebox.showinfo("Info", "No folder with unordered files selected.")
