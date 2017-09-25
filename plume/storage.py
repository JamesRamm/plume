import os
import re
import io
import mimetypes
from time import time

def unique_id():
    """Simplistic unique ID generation.
    The returned ID is just the current timestamp (in ms) converted to hex
    """
    return hex(int(time()*1000000))


class FileStore(object):
    _CHUNK_SIZE_BYTES = 4096

    # Note the use of dependency injection for standard library
    # methods. We'll use these later to avoid monkey-patching.
    def __init__(
            self,
            storage_path,
            namegen=unique_id,
            fopen=io.open,
            name_pattern='^(0x)?[a-f0-9]+$'
        ):
        self._storage_path = storage_path
        self._namegen = namegen
        self._fopen = fopen
        self._name_pattern = re.compile(name_pattern)

    def _validate_filename(self, filename):
        name = os.path.splitext(filename)[0]
        return self._name_pattern.match(name)

    def save(self, stream, image_content_type):
        ext = mimetypes.guess_extension(image_content_type)
        name = '{uuid}{ext}'.format(uuid=self._namegen(), ext=ext)
        filepath = os.path.join(self._storage_path, name)

        with self._fopen(filepath, 'wb') as fileobj:
            while True:
                chunk = stream.read(self._CHUNK_SIZE_BYTES)
                if not chunk:
                    break

                fileobj.write(chunk)

        return name

    def open(self, name):
        # Validate the requested filename
        if not self._validate_filename(name):
            raise IOError('File not found')

        image_path = os.path.join(self._storage_path, name)
        stream = self._fopen(image_path, 'rb')
        stream_len = os.path.getsize(image_path)

        return stream, stream_len

    def list(self):
        uploads = [name for name
                   in os.listdir(self._storage_path)
                   if self._validate_filename(name)]
        return uploads
