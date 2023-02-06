import os
import sys
from imgFile import ImageFile
from vptree import VPTree
from multiprocessing import Pool, Value

multi_counter = None


def diff_imgs(a: ImageFile, b: ImageFile) -> int:
    return a.dist(b)


def multiprocess_init(counter, total_count_):
    global multi_counter
    global total_count
    multi_counter = counter
    total_count = total_count_


def read_and_process_img(img_path) -> ImageFile | None:
    print(f"({multi_counter.value}/{total_count}) Reading file {img_path}...")
    with multi_counter.get_lock():
        multi_counter.value += 1
    try:
        image = ImageFile(filePath=img_path, width=-1, height=-1, dHash=None, colorHash=None)
        image.calculateHash()
        return image
    except Exception as exp:
        print(f"...Warning: while reading {img_path}:\n...{exp.__str__()}\n...Skipped.")
        return None


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please specify the directory to scan.")
        print("Stop.")
        exit(1)
    scan_dir = sys.argv[1]
    imagesPath = []
    for (root, dirs, files) in os.walk(scan_dir):
        print(f"Scanning {root}")
        imagesPath.extend(
            os.path.join(root, t) for t in files if t.endswith(".png") or t.endswith(".jpg") or t.endswith(".jpeg") or t.endswith(".jfif"))

    print(f"Collected {len(imagesPath)} images.")

    multi_counter = Value('i', 0)
    with Pool(8, initializer=multiprocess_init, initargs=(multi_counter, len(imagesPath))) as pool:
        images = pool.map(read_and_process_img, imagesPath)
    images = [t for t in images if t is not None]

    print("Read completed. Indexing hashes...")
    tree = VPTree(images, diff_imgs)

    for img in images:
        rg: list[(int, ImageFile)] = tree.get_all_in_range(img, 5)
        if len(rg) > 1:
            for (dist, item) in rg:
                print(f"dist: {dist} | {item.filePath}")
            print("---")
