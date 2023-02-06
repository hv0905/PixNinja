from dataclasses import dataclass
from imagehash import ImageHash, dhash, colorhash
from functools import total_ordering
from PIL import Image

CMP_BY_COLORHASH = False


@dataclass
class ImageFile:
    filePath: str
    width: int
    height: int
    dHash: ImageHash
    colorHash: ImageHash

    # WARNING: this func will NOT check if the hashing value is ready, make sure you have calculated the required
    # hash before calling it.
    def dist(self, other) -> int:
        if CMP_BY_COLORHASH:
            return self.colorHash - other.colorHash
        else:
            return self.dHash - other.dHash

    def calculateHash(self):
        with Image.open(self.filePath) as img:
            self.width = img.width
            self.height = img.height
            if CMP_BY_COLORHASH:
                self.colorHash = colorhash(img)
            else:
                self.dHash = dhash(img)
