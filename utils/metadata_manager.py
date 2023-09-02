import pyexiv2
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, TXXX


class InvalidKeyError(Exception):
    pass

class MetadataManager:
    """
    What is this?
    This class utilizes mutagen & pyexiv2 to provide Exif metadata support, most importantly to the mp4, mp3, png, jpg and jpeg file formats.
    While not focused on perfect integration, it achieves the metadata addition, cross-platform compatible, to supported formats in a timely manner.
    The resulting cleaned metadata can be accessed as dict through .formatted_metadata() or unformatted with .raw_metadata
    Only the following custom_key names are permissible: HSH (representing Hash) and ID (representing MediaID).
    
    Limitations:
    - Inability to add metadata to all images over 1 GB in size, due to pyexiv2.
    - Inability to read metadata from images, over 2 GB in filesize, due to pyexiv2.
    - Lack of thread safety due to pyexiv2's global variables in C++.
    - Incomplete support for ARM platform with pyexiv2.
    - In line with GIFs general lack of Exif support, this class also doesn't cover GIFs.
    
    Usage:
    filepath = '[filename].[fileformat]'
    
    Add metadata:
    metadata_manager = MetadataManager()
    metadata_manager.is_file_supported(file_extension) # e.g. use this as conditional, returns boolean
    metadata_manager.set_filepath(filepath)
    metadata_manager.set_custom_metadata("ID", '305462832970526416')
    metadata_manager.set_custom_metadata("HSH", '10ej3e691af63ae66843218c42d5d0b3')
    metadata_manager.add_metadata()
    metadata_manager.save()
    
    Read metadata:
    metadata_manager = MetadataManager()
    metadata_manager.read_metadata(filepath)
    print(metadata_manager.formatted_metadata())
    print(metadata_manager.raw_metadata)
    """ 
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.custom_metadata = {}
        self.filetype = None if filepath is None else filepath.split('.')[-1].lower()
        self.raw_metadata = {}
        self.image_filetypes = [
            'jpeg', 'jpg', 'png',
            'exv', 'cr2', 'crw', 'tiff', 'webp', 'dng', 'nef', 'pef',
            'srw', 'orf', 'pgf', 'raf', 'xmp', 'psd', 'jp2'
        ]

    def is_file_supported(self, filetype=None):
        filetype = self.filetype if filetype is None else filetype
        return filetype in ['mp4', 'mp3'] or filetype in self.image_filetypes

    def set_filepath(self, filepath):
        self.filepath = filepath
        self.filetype = filepath.split('.')[-1].lower()

    # initial temporary storage in-case multiple keys shall be added, in one run
    def set_custom_metadata(self, custom_key: str, custom_value: str):
        if not any([custom_key, custom_value]):
            return
        if custom_key not in ["HSH", "ID"]:
            raise InvalidKeyError(f"Received custom_key \'{custom_key}\', but MetadataManager only supports custom keys named \'HSH\' or \'ID\'")
        self.custom_metadata[custom_key] = custom_value

    # return formatted metadata
    def formatted_metadata(self):
        self.read_metadata()
        result = {}
        if self.filetype == 'mp3':
            if 'TXXX:HSH' in self.raw_metadata:
                value = self.raw_metadata['TXXX:HSH'].text[0]
                result['HSH'] = int(value) if value.isdigit() else value
            if 'TXXX:ID' in self.raw_metadata:
                value = self.raw_metadata['TXXX:ID'].text[0]
                result['ID'] = int(value) if value.isdigit() else value
        elif self.filetype == 'mp4':
            for key, value in self.raw_metadata.items():
                clean_key = key.replace('_', '')
                if clean_key in ['HSH', 'ID']:
                    result[clean_key] = int(value[0]) if value[0].isdigit() else value[0]
        elif self.filetype in self.image_filetypes:
            custom_tag_mapping = {
            'Exif.Image.Software': 'ID',
            'Exif.Image.DateTime': 'HSH'
            }
            for key, value in self.raw_metadata.items():
                if key in custom_tag_mapping:
                    result[custom_tag_mapping[key]] = int(value) if value.isdigit() else value
        return result

    # read metadata
    def read_metadata(self, filepath=None):
        if not self.filepath and filepath:
            self.filepath = filepath
            self.filetype = filepath.rsplit('.')[1]
        if self.filetype in ['mp4', 'mp3']:
            self.read_audio_video_metadata()
        elif self.filetype in self.image_filetypes:
            self.read_image_metadata()

    def read_audio_video_metadata(self):
        if self.filetype == 'mp3':
            self.raw_metadata = ID3(self.filepath)
        elif self.filetype == 'mp4':
            self.raw_metadata = MP4(self.filepath)

    def read_image_metadata(self):
        with pyexiv2.Image(self.filepath) as image:
            self.raw_metadata = image.read_exif()

    # add metadata
    def add_metadata(self):
        for key, value in self.custom_metadata.items():
            if self.filetype == 'mp3':
                self.add_mp3_metadata(key, value)
            elif self.filetype == 'mp4':
                self.add_mp4_metadata(key, value)
            elif self.filetype in self.image_filetypes:
                self.add_image_metadata(key, value)
    
    def add_mp3_metadata(self, key, value):
        txxx_frame = TXXX(encoding=3, desc=key, text=value)
        self.raw_metadata.add(txxx_frame)
    
    def add_mp4_metadata(self, key, value):
        if not isinstance(self.raw_metadata, MP4):
            self.read_audio_video_metadata()
        if len(key) < 4:
            key = key + '_' * (4 - len(key))
        elif len(key) > 4:
            key = key[:4]
        self.raw_metadata[key] = str(value)

    def add_image_metadata(self, key, value):
        custom_tag_mapping = {
            'ID': 'Exif.Image.Software',
            'HSH': 'Exif.Image.DateTime'
        }
        if key in custom_tag_mapping:
            key = custom_tag_mapping[key]
        self.raw_metadata[key] = value

    def save(self):
        if self.filetype in self.image_filetypes:
            with pyexiv2.Image(self.filepath) as image:
                image.modify_exif(self.raw_metadata)
        else:
            self.raw_metadata.save(self.filepath)
