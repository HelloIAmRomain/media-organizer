import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageTk, ExifTags
import cv2
from pillow_heif import register_heif_opener
import datetime
import re
import ffmpeg

register_heif_opener()

# Function to extract dates from various sources


def extract_dates(file_path):
    detected_date = None

    # Extract date from filename using regular expressions
    date_patterns = [
        r'(20\d{2})(\d{2})(\d{2})',  # yyyymmdd pattern starting with '20'
        # Screenshot_yyyymmdd pattern starting with '20'
        r'Screenshot_(20\d{2})(\d{2})(\d{2})',
        # VID_yyyymmdd pattern starting with '20'
        r'VID_(20\d{2})(\d{2})(\d{2})',
        r'(20\d{2})-(\d{2})-(\d{2})',  # yyyy-mm-dd pattern starting with '20'
    ]

    for pattern in date_patterns:
        match = re.search(pattern, file_path)
        if match:
            try:
                year, month, day = map(int, match.groups())
                detected_date = datetime.date(year, month, day)
                if 2005 <= year <= 2025:  # Safeguard to keep dates between 2005 and 2025
                    return detected_date
            except ValueError:
                continue

    # Extract date from image metadata using PIL
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag, tag)
                if tag_name == 'DateTimeOriginal' or tag_name == 'DateTime':
                    metadata_date = datetime.datetime.strptime(
                        value, '%Y:%m:%d %H:%M:%S').date()
                    if 2005 <= metadata_date.year <= 2025:
                        detected_date = metadata_date
                        return detected_date
    except Exception as e:
        pass

    # Searching for unix timestamp pattern

    filename = os.path.basename(file_path)
    timestamp_pattern = r'(\d{10})'  # Matches Unix timestamp in seconds

    match = re.search(timestamp_pattern, filename)
    if match:
        try:
            timestamp = int(match.group(1))
            detected_date = datetime.datetime.fromtimestamp(timestamp)
            if 2000 <= detected_date.year <= 2025:  # Safeguard to keep dates between 2005 and 2025
                new_filename = f"{detected_date}_{filename}"
                new_path = os.path.join(
                    os.path.dirname(file_path), new_filename)
                os.rename(file_path, new_path)
                return detected_date
        except (ValueError, OSError):
            pass  # Handle errors gracefully

    return detected_date

# Function to extract all EXIF data using PIL


def extract_exif_data(file_path):
    try:
        # Get the file extension to determine the type
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()

        if file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            # For images
            image = Image.open(file_path)
            exif_data = image._getexif()
            if exif_data:
                exif_dict = {ExifTags.TAGS.get(
                    tag, tag): value for tag, value in exif_data.items()}
                return exif_dict

        elif file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
            # For videos
            metadata = ffmpeg.probe(file_path)
            exif_dict = {}
            if 'streams' in metadata:
                for stream in metadata['streams']:
                    exif_dict.update(stream)
            if 'format' in metadata:
                exif_dict.update(metadata['format'])
                exif_data["DateTime"] = metadata["format"]["tags"].get(
                    "creation_time")
            return exif_data

    except Exception as e:
        print("Error extracting EXIF data:", e)

    return {}


# Function to move a file to a date-based directory


def move_file_to_date_based_folder(source_path, destination_base_path, date):
    year_folder = os.path.join(destination_base_path, str(date.year))
    month_folder = os.path.join(year_folder, f"{date.month:02d}")

    # Create directories if they don't exist
    os.makedirs(month_folder, exist_ok=True)

    # Construct the destination path
    destination_path = os.path.join(
        month_folder, os.path.basename(source_path))

    # Move the file
    shutil.move(source_path, destination_path)


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

        # Treeview to display EXIF data
        self.metadata_tree = ttk.Treeview(self.root, columns=(
            "Key", "Value"), show="headings", height=8)
        self.metadata_tree.heading("Key", text="Key")
        self.metadata_tree.heading("Value", text="Value")
        self.metadata_tree.column("Key", anchor="w", width=200)
        self.metadata_tree.column("Value", anchor="w", width=350)
        self.metadata_tree.pack(pady=10)

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

        self.auto_sort_button = tk.Button(
            self.root, text="Auto-Sort by Date", command=self.auto_sort_by_date)
        self.auto_sort_button.pack(pady=10)

        self.new_folder_button = tk.Button(
            self.root, text="Create New Folder", command=self.create_new_folder)
        self.new_folder_button.pack(pady=10)

    def load_media(self, filename):
        file_path = os.path.join(self.unordered_base_path, filename)
        file_presence_info = self.check_file_presence(filename)
        self.file_info_label.config(text=f"{filename} - {file_presence_info}")

        # Display image or video thumbnail
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

        # Extract and display EXIF data
        detected_date = extract_dates(file_path)
        exif_data = extract_exif_data(file_path)

        # Clear the Treeview and insert new data
        self.metadata_tree.delete(*self.metadata_tree.get_children())

        if detected_date:
            self.metadata_tree.insert(
                "", "end", values=("Detected Date", detected_date))

        if exif_data:
            for key, value in exif_data.items():
                self.metadata_tree.insert("", "end", values=(key, value))
        else:
            # If no EXIF data, reduce the Treeview size
            self.metadata_tree.config(height=1)
            self.metadata_tree.insert(
                "", "end", values=("No EXIF data found", ""))

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

    def auto_sort_by_date(self):
        skipped_files = []
        for file in self.unordered_files[:]:
            file_path = os.path.join(self.unordered_base_path, file)
            detected_date = extract_dates(file_path)
            if detected_date:
                move_file_to_date_based_folder(
                    file_path, self.subfolders_base_path, detected_date)
                self.unordered_files.remove(file)
            else:
                skipped_files.append(file)

        if skipped_files:
            messagebox.showinfo(
                "Info", f"Auto-sorting completed. Some files could not be sorted and will be presented manually.")
        else:
            messagebox.showinfo("Info", "Auto-sorting completed successfully.")

        # Continue with manual sorting of the remaining files
        if self.unordered_files:
            self.current_file_index = 0
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
    print("--- DONE ---")
