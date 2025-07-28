from urllib.request import urlopen
from os.path import split, exists

import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import ImageTk, Image

from Media import *

# [ ]: get this code better and more organized
# [ ]: add the scroll for multiple media objects
# [ ]: add the possibility to download all the media added once
# [ ]: add an progress bar
# [ ]: add the possibility to add a playlist (checks if is a playlist duhh)
# TODO: add a function to display error or succeed modal

class DownloadMedia:
    """A utility class for handling media file path selection and initiating downloads."""
    @staticmethod
    def get_file_save_dir(media: Media) -> str:
        """
        Opens a file save dialog for the user to choose a directory to save the media file.
        Supports saving in .mp4 format for videos and .mp3 format for audio.
        """
        full_file_path = ""
        try:
            match(media.file_type):
                case FileType.VIDEO:
                    full_file_path = filedialog.asksaveasfilename(
                        initialfile=media.get_media_info().get('title'), 
                        defaultextension='.mp4', 
                        filetypes=[("Video","*.mp4"), ("All Files","*.*")],
                    )
                case FileType.AUDIO:
                    full_file_path = filedialog.asksaveasfilename(
                        initialfile=media.get_media_info().get('title'), 
                        defaultextension='.mp3', 
                        filetypes=[("Audio","*.mp3"), ("All Files","*.*")],
                    )
                case _:
                    print(f"FileType '{media.file_type}' does not exist!")
                    return None
        except Exception as e:
            print("Select file path exception:", e)
            return None

        if full_file_path == "":
            return None
        if exists(full_file_path):
            try:
                remove(full_file_path)
            except Exception as e:
                print("Remove file exception:", e)

        file_save_dir, media.file_name = split(full_file_path)
        if not file_save_dir or not media.file_name:
            print("Download canceled or invalid path")
            return None
        
        return file_save_dir

    @staticmethod
    def download_media(media: Media, path: str) -> None:
        """Initiates the download process for the specified media, saving it in the provided path."""
        try:
            if path:
                downloader = Downloader(media, path)
                downloader.download()
        except Exception as e:
            print("Download has encoutered an exception:", e)
            return None
        

class MediaInfo(ttk.Frame):
    """A GUI component that displays media information and download options for a specific media item."""
    def __init__(self, parent: tk.Widget, url: str, images_dict: dict[ImageTk.PhotoImage]) -> None:
        super().__init__(parent)
        self.images_dict = images_dict
        self.media = Media(url)
        self.media_info = self.media.get_media_info()
        
        self.pack(padx=10, pady=10)
        self.container()
    
    def container(self) -> None:
        """
        Configures the layout for frames and widgets to display media information, 
        including the thumbnail, title, channel, and duration. It also creates buttons 
        for removing the item, downloading, and toggling between video and audio modes.
        """
        # region frames configuration
        media_frame = ttk.Frame(self)
        option_frame = ttk.Frame(self)
        info_frame = ttk.Frame(media_frame)

        self.columnconfigure(2, weight=1)
        info_frame.rowconfigure((0,1,2), weight=1)
        media_frame.columnconfigure((0,1), weight=1)
        option_frame.rowconfigure((0,1,2), weight=1)
        # endregion
        
        # region widgets configuration
        self.imgThumb = self.get_thumbnail()
        thumbnail = ttk.Label(media_frame, image=self.imgThumb)
        title = ttk.Label(info_frame, text=self.media_info.get("title"), font=("Arial", 12, "bold"))
        channel = ttk.Label(info_frame, text=self.media_info.get("channel"), font=("Arial", 12))
        duration = ttk.Label(info_frame, text=self.media_info.get("duration"), font=("Arial", 12))

        remove = ttk.Button(option_frame, image=self.images_dict.get("close"), command=lambda: self.destroy())
        download = ttk.Button(option_frame, image=self.images_dict.get("download"), command=lambda: DownloadMedia.download_media(self.media, DownloadMedia.get_file_save_dir(self.media)))
        option = ttk.Button(option_frame, image=self.images_dict.get("video"), command=lambda: self.change_media_type(option))
        # endregion

        # region frames/widgets display
        thumbnail.grid(row=0, column=0, sticky='nswe')
        title.grid(row=0, sticky='nw', padx=10)
        channel.grid(row=1, sticky='nw', padx=10)
        duration.grid(row=2, sticky='nw', padx=10)

        remove.grid(row=0, sticky='nswe')
        download.grid(row=1, sticky='nswe')
        option.grid(row=2, sticky='nswe')

        info_frame.grid(row=0, column=1, sticky='nw')
        media_frame.grid(row=0, column=0, sticky='nswe')
        option_frame.grid(row=0, column=1, sticky='nswe')
        # endregion
    
    def get_thumbnail(self) -> ImageTk.PhotoImage:
        """Fetches the thumbnail image from the media metadata URL and resizes it for display."""
        try:
            data = urlopen(self.media_info.get('thumbnail'))
            img = Image.open(data).resize((192,130))
            return ImageTk.PhotoImage(image=img)
        except Exception as e:
            print("Error getting thumbnail:", e)
            return ImageTk.PhotoImage(Image.open(join("images", "noImage.png")).resize((192,130)))

    def change_media_type(self, button: ttk.Button):
        """Toggles the media type between video and audio. Updates the button icon based on the selected media type."""
        if self.media.file_type == FileType.VIDEO:
            button.configure(image=self.images_dict.get("audio"))
            self.media.file_type = FileType.AUDIO
        else:
            button.configure(image=self.images_dict.get("video"))
            self.media.file_type = FileType.VIDEO


class SearchMenu(ttk.Frame):
    """A GUI component that provides a search entry and button to validate and add media urls."""
    def __init__(self, parent, add_media_callback) -> None:
        super().__init__(parent)
        self.pack(pady=50)

        self.add_media_callback = add_media_callback
        
        self.entry_container("Search")

    def entry_container(self, button_text):
        """Creates and configures an entry field and button for inputting a media url."""
        entry_url = tk.StringVar()
        self.entry = ttk.Entry(self, width=80, textvariable=entry_url)
        self.button = ttk.Button(
            self, 
            text=button_text, 
            bootstyle=SUCCESS, 
            command=lambda:self.validate_url(entry_url.get()))

        self.entry.grid(row=0, column=0, sticky='e')
        self.button.grid(row=0, column=1, sticky='w')
    
    def validate_url(self, url: str) -> None:
        """Validates the provided media url. If valid, calls `add_media_callback` with the url
        and updates the entry style to indicate success; otherwise, updates the style to indicate an error."""
        if not Media.is_url(url):
            self.entry.configure(bootstyle=DANGER)
        else:
            self.entry.configure(bootstyle=SUCCESS)
            self.add_media_callback(url)


class App(ttk.Window):
    """A main application window for managing and displaying media download options in the GUI."""
    def __init__(self, title: str, theme: str, size: tuple[int]) -> None:
        super().__init__(title=title, themename=theme, size=size, minsize=size)
        
        self.images_dict = {
            "audio":ImageTk.PhotoImage(Image.open(join("images", "audio.png")).resize((20,20))),
            "video":ImageTk.PhotoImage(Image.open(join("images", "video.png")).resize((20,20))),
            "download":ImageTk.PhotoImage(Image.open(join("images", "download.png")).resize((20,20))),
            "close":ImageTk.PhotoImage(Image.open(join("images", "close.png")).resize((20,20))),
            "noImage":ImageTk.PhotoImage(Image.open(join("images", "noImage.png")).resize((192,130)))
        }

        SearchMenu(self, self.add_media_info)

        self.media_container = ttk.Frame(self)
        self.media_container.pack()

        self.mainloop()
    
    def add_media_info(self, url: str) -> None:
        """
        Adds a `MediaInfo` widget to the media container for displaying information and 
        download options for the provided media url.
        """
        media_info = MediaInfo(self.media_container, url, self.images_dict)
        media_info.pack(padx=10, pady=10)


if __name__ == "__main__":
    App("Media Downloader", "darkly", (900,600))