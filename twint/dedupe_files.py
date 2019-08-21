import filecmp
import itertools
import logging
import os
import sys
import hashlib
import logging
from PIL import Image
import imagehash
import face_recognition
import cv2 as cv


logger = logging.getLogger(__name__)


# dedupe-rename.py -d /Volumes/Data/4chan/jpg  -o dedupe

def dedupe_slower(filenames, prefer_shorter=True):
    deleted = set()
    for filename1, filename2 in itertools.combinations(filenames, 2):
        if filename1 not in deleted and filename2 not in deleted and filecmp.cmp(filename1, filename2):
            file_to_delete, original_file = sorted([filename1, filename2], reverse=prefer_shorter)
            os.remove(file_to_delete)
            deleted.add(file_to_delete)
            logger.info('Deleted: %s (duplicate of: %s)', file_to_delete, original_file)


def findDup(parentFolder):
    log = logging.getLogger('findDup')
    log.info(f"findDup starting ... {parentFolder}")
    print(f"Scanning {parentFolder}")
    # Dups in format {hash:[names]}
    dups = {}
    path, dirs, files = next(os.walk(parentFolder))
    file_count = len(files)
    if file_count is None:
        exit(1)

    print(f"No of files found= {file_count}")

    for dirName, subdirs, fileList in os.walk(parentFolder):
        for filename in fileList:
            # Get the path to the file
            if is_image(filename):
                path = os.path.join(dirName, filename)
                # Calculate hash
                file_hash = hashfile(path)
                # Add or append the file path
                if file_hash in dups:
                    dups[file_hash].append(path)
                else:
                    dups[file_hash] = [path]
    return dups

def is_image(filename):
    log = logging.getLogger('is_image')
    # log.info(f"is_image starting ...")
    try:
        f = filename.lower()
        return f.endswith(".png") or f.endswith(".jpg") or \
        f.endswith(".jpeg") or f.endswith(".bmp") or f.endswith(".gif") or '.jpg' in f
    except RuntimeError as e:
        log.critical(f"is_image error: {str(e)}")

def get_filenames(userpaths):
    file_list = []
    for dirName, subdirs, fileList in os.walk(userpaths):
        for filename in fileList:
            if is_image(filename):
                file_list.append(os.path.join(dirName, filename))
    return file_list

def face_detect_fast(img):
    image = face_recognition.load_image_file(img)
    face_landmarks_list = face_recognition.face_landmarks(image)

    faces_detected = len(face_landmarks_list)
    if faces_detected:
        return True
    else:
        return False

def face_detect_better(img):

    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'twint/profiles'))
    face_cascade_list = [
        f'{dir_path}/haarcascade_frontalface_alt2.xml',
        f'{dir_path}/haarcascade_profileface.xml',
        f'{dir_path}/haarcascade_frontalface_default.xml',
        f'{dir_path}/haarcascade_fullbody.xml']

    image = cv.imread(img)
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    for fc in face_cascade_list:

        face_cascade = cv.CascadeClassifier(fc)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        faces_detected = len(faces)

        if faces_detected:
            return True
    return False


def find_similar_images(userpaths):
    hashfunc = imagehash.average_hash
    if not os.path.exists(userpaths):
        Print(f"Path doesn't exist: {userpaths}")
        exit(1)
    try:
        image_filenames = get_filenames(userpaths)

        num = 1
        images = {}
        for img in sorted(image_filenames):
            if not os.path.isfile(img):
                print("file not found")
                return
            hash = imagehash.dhash(Image.open(img), 10)
            # hash = imagehash.average_hash(Image.open(img), 16)
            # phash lower number matches everything to everything
            # hash = imagehash.phash(Image.open(img), 4, 12)

            # hash = imagehash.whash(Image.open(img), 4)
            # hash = imagehash.whash(Image.open(img), mode='db4')
            path = os.path.split(img)[0]
            if not path.endswith(os.path.sep):
                path += os.path.sep
            new_nameSTR = f"{path}{hash}-{num}{os.path.splitext(img)[1]}"
            new_name = os.path.join(path, new_nameSTR)

            # print(f"hash: {hash}  \t image: {img}")

            if hash in images:
                # its a duplicate
                if 'dupPictures' in img:
                    print('rm -v', img)
            # os.rename(img, new_name)
            # images[hash] = images.get(hash, []) + [img]

            filename = os.path.split(img)[1]
            if filename[:2] == "F-":
                print(f"{img}  --  Skipped file")
                continue
            else:
                # faces_detected = face_detect_fast(img)
                faces_detected = face_detect_better(img)

            if faces_detected:
                new_nameSTR_face = f"F-{hash}-{num}{os.path.splitext(img)[1]}"
                new_name = os.path.join(path, new_nameSTR_face)

                print(f"{new_name} \t faces detected")

                images[hash] = images.get(hash, []) + [new_name]
                try:
                    os.rename(img, new_name)
                except OSError:
                    ext = filename[4:]
                    # need to add a b before last 3 characters here
                    # os.rename(img, new_name + "b")
                    print("test renaming file: " + os.path.join(path, filename + "b" + ext))
            else:
                images[hash] = images.get(hash, []) + [new_name]
                os.rename(img, new_name)
                print(f"{new_name}")

            num = num + 1
    except Exception as e:
            print('Problem:', e, 'with', img)


    # for k, img_list in six.iteritems(images):
    #    if len(img_list) > 1:
    #        print(" ".join(img_list))
    printResults(images)

def progress_bar(counter, range):
    for j in trange(66, leave=True):
    #    sleep(0.1)
        pass


# Joins two dictionaries
def joinDicts(dict1, dict2):
    for key in dict2.keys():
        if key in dict1:
            dict1[key] = dict1[key] + dict2[key]
        else:
            dict1[key] = dict2[key]


def hashfile_new(path):
    log = logging.getLogger('hashfile')
    try:
        hasher = imagehash.average_hash(Image.open(path))
    except OSError:
        log.info(f'access denied on: path: {path} ')
        return
        pass
    log.info(f"hash: {hasher} \t :image: {path}")
    return hasher


def hashfile(path, blocksize=65536):
    log = logging.getLogger('hashfile')
    try:
        afile = open(path, 'rb')
        # log.info(f'afile path/ {path}')

        hasher = hashlib.md5()
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
        afile.close()
    except OSError:
        log.info(f'access denied on: path: {path} ')
        return
        pass

    return hasher.hexdigest()


def printResults(dict1):
    log = logging.getLogger('printResults')
    results = list(filter(lambda x: len(x) > 1, dict1.values()))
    qty_dupes = len(results)
    print(f'Identical Duplicate Groups: {qty_dupes}')
    dupe_no = type(int)
    if qty_dupes > 0:

        print('The following files are identical. The name could differ, but the content is identical')
        print('--------------------')

        # dedupe(results)

        for result in results:

            dupe_no = len(results)
            print(f'Duplicate Files: {len(result)}')
            print('--------------------')
            shortest = min(result, key=len)
            print(f"Keeping file: {shortest}")
            for file_to_delete in result:
                if not file_to_delete == shortest:
                    os.remove(file_to_delete)
                    print(f"Deleted: {file_to_delete}")

            print('--------------------')

    if qty_dupes is None:
        print('No duplicate files found.')
    print(f'Total duplicate files found: {dupe_no}')


def start(folder_to_dedupe):
    if os.path.exists(folder_to_dedupe):
        log = logging.getLogger('run_dedupe')
        # log.info(f'starting on folder: {folder_to_dedupe}')
        log.info('creating executor tasks')
        # if len(sys.argv) > 1:
        dups = {}
        # folders = sys.argv[1:]
        folder = folder_to_dedupe
        # for i in folders:
        # Iterate the folders given

        # Find the duplicated files and append them to the dups
        joinDicts(dups, findDup(folder_to_dedupe))
        # else:
        # print('last')
        # sys.exit()
        printResults(dups)
        print('finished de-duping...')
    else:
        print('Usage: python dupFinder.py folder or python dupFinder.py folder1 folder2 folder3')
