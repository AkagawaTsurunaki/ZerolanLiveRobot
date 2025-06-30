from enum import Enum


class AudioFileType(str, Enum):
    FLV = 'flv'
    WAV = 'wav'
    OGG = 'ogg'
    MP3 = 'mp3'
    RAW = 'raw'


class ImageFileType(str, Enum):
    PNG = 'png'
    JPEG = 'jpeg'
    JPG = 'jpg'
