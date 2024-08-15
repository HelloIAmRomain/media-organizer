# Media Organizer

## Description
Media Organizer is a Python application that helps you organize your unordered photos and videos into designated folders. It provides a user-friendly interface for previewing and moving files.

## Installation

1. Clone the repository:
   - Run `git clone https://github.com/yourusername/media-organizer.git`
   - Navigate to the project directory with `cd media-organizer`

2. Create a virtual environment:
   - Run `python -m venv .venv`

3. Activate the virtual environment:
   - On Windows, run `.venv\Scripts\activate`
   - On macOS/Linux, run `source .venv/bin/activate`

4. Install the required packages:
   - Run `pip install -r requirements.txt`

## Usage

1. Run the application:
   - Execute `python tri_photos_videos.py`

2. Follow the on-screen instructions to select directories and organize your media files.

## Contributing
Feel free to open an issue or submit a pull request if you have suggestions or improvements.

## TODO
* For now the sort is done in one level of folders, the next step is to check recurcively the folders (ex : year > month, ...)
   --> (unordered) Add a checkbox that asks if the photos are only on root or find recurcively photos
   --> Find a way to show and select the layers of destination folders (ex : when selecting a folder in an input, a new ne appears below, and if i deselect one folder, the subfolders disappear - keep in memory the last folder used in case of error ?)

* Use AI to compare the image to the ones in the folder  (what, how ?) to propose the best location based on its characteristics. And why not, if possible, propose to rearange the folders to better sort the media.

- Also, add a integrated player for videos to play them instead of getting a preview image of the video.


## Recent work

- Added a button that automatically sort photos based on metadata or filename (format yyyy > mm)

## License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
