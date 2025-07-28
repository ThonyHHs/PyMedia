from os import system, remove
from os.path import join
import sys, getopt
from enum import Enum
import re
import subprocess

from pytubefix import YouTube, Stream

FFMPEG_PATH = join('ffmpeg', 'bin')


def get_number_of_items(listItems: list, numElements: int) -> list:
    if len(listItems) <= numElements:
        return listItems
    return [listItems[item] for item in range(numElements)]


class FileType(Enum):
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"


class Media:
    """
    A class for managing media from YouTube, including validation, information retrieval,
    and downloading of video and audio streams.
    """
    YOUTUBE_REGEX = (
        r"^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/"
        r"(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
    )

    def __init__(self, url: str, file_name: str = None, file_type: FileType = FileType.VIDEO):
        if not self.is_url(url):
            raise ValueError(f"Invalid Youtube url provided: {url}")
        self.url = url
        self.file_name = file_name
        self.file_type = file_type
        self.video_name = None
        self.audio_name = None
        self.yt = YouTube(url)
    
    @staticmethod
    def is_url(url: str) -> bool:
        """Validates if the given url matches the YouTube URL pattern."""
        if not re.match(Media.YOUTUBE_REGEX, url):
            print("Invalid format: Not a recognizable Youtube URL")
            return False
        return True

    def get_media_info(self) -> dict:
        """
        Retrieves and returns basic media information.

        Returns:
            dict: A dictionary containing media thumbnail URL, title, channel name, and duration.
        """
        return {
            "thumbnail":self.yt.thumbnail_url, 
            "title":self.yt.title, 
            "channel":self.yt.author, 
            "duration":self.yt.length
        }

    def get_highest_resolution(self, streams: list[Stream]) -> Stream:
        """
        Finds the highest resolution video stream from the provided list, prioritizing specific resolutions.

        Returns:
            Stream: The stream object of the highest resolution video, or None if unavailable.
        """
        resolution_priority = ['1080p', '720p', '480p', '360p', '240p', '144p']
        filtered_streams = [
            stream for stream in streams 
            if stream.type.lower() == "video" 
            and stream.codecs[0].split('.')[0].lower() == "avc1" 
            and stream.is_progressive is False
        ]
        sorted_streams = sorted(
            filtered_streams, key=lambda stream: stream.fps, reverse=True
        )
        return next((stream for stream in sorted_streams if stream.resolution in resolution_priority), None)
    
    def get_highest_bitrate(self, streams: list[Stream]) -> Stream:
        """
        Finds the highest bitrate audio stream from the provided list, prioritizing specific bitrates.

        Returns:
            Stream: The stream object of the highest bitrate audio, or None if unavailable.
        """
        audio_bitrates_priority = ['128kbps', '48kbps']
        filtered_streams = [
            stream for stream in streams 
            if stream.type.lower() == "audio" 
            and stream.codecs[0].split('.')[0].lower() == "mp4a"
        ]
        sorted_streams = sorted(filtered_streams, key=lambda stream: stream.abr)
        return next((stream for stream in sorted_streams if stream.abr in audio_bitrates_priority), None)

    def download_video(self) -> None:
        """
        Downloads the highest resolution video stream and saves it as a temporary file.
        
        Sets:
            video_name (str): The name of the temporary video file downloaded.
        """
        stream = self.get_highest_resolution(self.yt.streams)
        if stream is None:
            print("Video stream is empty!")
            return
        self.video_name = stream.download(filename=f"TEMPvideo.mp4")

    def download_audio(self) -> None:
        """
        Downloads the highest bitrate audio stream and saves it as a temporary file.
        
        Sets:
            audio_name (str): The name of the temporary audio file downloaded.
        """
        stream = self.get_highest_bitrate(self.yt.streams)
        if stream is None:
            print("Audio stream is empty!")
            return
        self.audio_name = stream.download(filename=f"TEMPaudio.mp3")


class Downloader:
    """
    A class to manage media downloads and conversions, 
    supporting combined media downloads (video and audio) 
    and audio-only conversions using FFMPEG.
    """
    def __init__(self, media: Media, file_dir: str = ''):
        self.media = media
        self.file_dir = file_dir
    
    def __combine_media(self):
        """
        Downloads video and audio streams from the media and combines them into a single file.
        The output file is saved to the specified file directory.

        Raises:
            Exception: If an error occurs during the merging process.
        """
        try:
            self.media.download_video()
            self.media.download_audio()
            system(f'{join(FFMPEG_PATH, 'ffmpeg.exe')} -i {self.media.video_name} -i {self.media.audio_name} -c:v copy -c:a aac "{join(self.file_dir, self.media.file_name)}"')
        except Exception as e:
            print("merging error: ",e)
    
    def __audio_converter(self):
        """
        Downloads the audio stream from the media and converts it to MP3 format using FFMPEG.
        The output file is saved to the specified file directory.

        Raises:
            Exception: If an error occurs during the audio conversion process.
        """
        try:
            self.media.download_audio()
            system(f'{join(FFMPEG_PATH, 'ffmpeg.exe')} -i {self.media.audio_name} -acodec libmp3lame "{join(self.file_dir, self.media.file_name)}"')
        except Exception as e:
            print("audio error: ",e)
    
    def download(self) -> None:
        """
        Initiates the download process based on the media file type.
        
        - Combines video and audio for video files.
        - Converts audio to MP3 for audio files.
        - Cleans up temporary files after processing.
        
        Raises:
            ValueError: If the media file type is unsupported.
        """
        match(self.media.file_type):
            case FileType.VIDEO:
                self.__combine_media()
            case FileType.AUDIO:
                self.__audio_converter()
            case _:
                raise ValueError(f"FileType '{self.media.file_type}' does not exist!")
        self.__clean_up()

    def __clean_up(self):
        """
        Removes temporary video and audio files created during the download and conversion processes,
        setting the respective file names in the media instance to None.
        """
        if self.media.video_name:
            remove(self.media.video_name)
            self.media.video_name = None
        if self.media.audio_name:
            remove(self.media.audio_name)
            self.media.audio_name = None


# Still not used
class DownloadQueue:
    def __init__(self):
        self.queue = []

    def get_queue(self):
        return self.queue

    def add_to_queue(self, media: Media):
        self.queue.append(media)
    
    def process_queue(self):
        while self.queue:
            media = self.queue.pop(0)
            downloader = Downloader(media)
            downloader.download()


def cli(argv: list):
    try:
        options, args = getopt.getopt(argv, "van:p:l:", ["video", "audio", "name=", "path=", "url="])
    except Exception as e:
        print("Argument error:", e)
    
    url = file_name = file_type = file_dir = ""
    for opt, arg in options:
        if opt in ['-v', "--video"]:
            file_type = FileType.VIDEO
        elif opt in ['-a', "--audio"]:
            file_type = FileType.AUDIO
        elif opt in ['-n', "--name"]:
            file_name = arg
        elif opt in ['-p', "--path"]:
            file_dir = arg
        elif opt in ['-l', "--url"]:
            url = arg
    
    if file_type == FileType.VIDEO:
        file_name += '.mp4'
    elif file_type == FileType.AUDIO:
        file_name += '.mp3'

    try:
        media = Media(url, file_name, file_type)
        Downloader(media, file_dir).download()
    except Exception as e:
        print("Download error:", e)

def tui():
    print("""__ _____  _   _  ___
\\ V /_ _|| \\_/ || o \\
 \\ / | /o\\ \\_/ ||  _/
 |_| |_\\_/_| |_||_|
          """)
    
    url = input("Enter URL: ")
    file_type = input("Type: ")
    file_dir = input("Folder Path: ")
    file_name = input("File Name: ")
    print()
    file_type = FileType.VIDEO

    if file_type == FileType.VIDEO:
        file_name += '.mp4'
    elif file_type == FileType.AUDIO:
        file_name += '.mp3'

    try:
        media = Media(url, file_name, file_type)
        Downloader(media, file_dir).download()
    except Exception as e:
        print("Download error:", e)


if __name__ == "__main__":
    if sys.argv[1:]:
        cli(sys.argv[1:])
    tui()