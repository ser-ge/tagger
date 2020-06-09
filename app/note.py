from google.cloud import vision
import io
from io import BytesIO
import os
from pdf2image import convert_from_path, convert_from_bytes
import glob
from PIL import Image
from fuzzywuzzy import process, fuzz
from functools import wraps
from hashlib import md5
import pickle

TAG_MARK = '@'

path ='/Users/serge/Google Drive/NeoNotesPDF/scrap_book_p16_20200522.pdf'


class Note:
    """
    Base Class for Processing Scanned Documents (Notes)

    Args:
        path (str): file path or file name with extension
        file_buff (BytesIO): image or pdf to be processed
        target_tags ([str,]): list of target tags against witch found tags are matched
    """

    def __init__(self, path, file_buff, target_tags):

        self.path = path
        self.file_buff = file_buff
        self.target_tags = target_tags
        self.img_types = ['png', 'jpg', 'jpeg']
        self.ext = path.split('.')[-1]
        print("Extension: ", self.ext)

    def _load_from_buff(self):

        if self.ext == 'pdf':
            self.image = convert_from_bytes(self.file_buff.getvalue(), single_file=True)[0]
            buff = BytesIO()
            self.image.save(buff, format='JPEG')
            self.content = buff

        elif self.ext in self.img_types:
            self.content = self.file_buff
            self.image = Image.open(self.content)

        else:
            raise TypeError("Invalid file format: only images or pdfs allowed")

    def _load_from_path(self):

        with io.open(self.path, 'rb') as f:
            if self.ext == 'pdf':
                self.image = convert_from_bytes(f.read(), single_file=True)[0]
                buff = BytesIO()
                self.image.save(buff, format='JPEG')
                self.content = buff

            elif self.ext in self.img_types:
                self.content =  BytesIO(f.read())
                self.image = Image.open(self.content)

            else:
                raise TypeError("Invalid file format: only images or pdfs allowed")

    def to_text(self, service='google'):
        if service == 'google':
            self.raw_text = ocr_google(self.content)
        return self.raw_text

    def extract_raw_tags(self, mode="linewise"):

        self.raw_tags = []

        if mode == "linewise":
            lines = self.raw_text.split("\n")
            for line in lines:
                if TAG_MARK in line:
                    words = line.strip().split(TAG_MARK)[-1].split(" ")
                    words = list(filter(None, words)) # remove empty strings
                    tag = " ".join(words)
                    self.raw_tags.append(tag)


        if mode == "end": # only single word tags supported in this mode
            end_tags = self.raw_text.replace("\n", " ").replace('\r', ' ').strip().split(TAG_MARK)[1]
            words = tags.split(" ")
            words = list(filter(None, words)) # remove empty strings
            self.raw_tags.extend(words)

        return self.raw_tags

    def match_tags(self, allow_new_tag=False):
        '''Match raw tags against a list of target_tags, assign closest match to self.tags'''

        self.tags = []
        for raw_tag in self.raw_tags:
            matching_tag = fuzzy_match(raw_tag, self.target_tags)

            if matching_tag is not None:
                self.tags.append(matching_tag)

            if matching_tag is None and allow_new_tag:
                self.tags.append(raw_tag)

        return self.tags

    def process(self):
        """
        Returns:
            title: first line of text
            text: whole text, including first line
            tags: tags matched in target_tags
            image: PIL image object
        """
        self._load_from_buff()
        self.to_text()
        self.title = self.raw_text.split("\n")[0]
        self.extract_tags()
        self.match_tags()
        return self.title, self.raw_text, self.tags, self.image


def ocr_memo(func):
    """cacche for google vision api calls"""
    @wraps(func)
    def wraper(arg):
        try:
            cache = pickle.load(open("ocr_cache.p", "rb"))
        except FileNotFoundError:
            cache = dict()
        key = md5(arg.getbuffer()).hexdigest()
        if key not in cache:
            cache[key] = func(arg)
        pickle.dump(cache, open("ocr_cache.p", "wb"))
        return cache[key]
    return wraper



@ocr_memo
def ocr_google(content):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/serge/projects/neonotes/googlecreds.json"
    client = vision.ImageAnnotatorClient()
    print("calling google api")
    v_image = vision.types.Image(content=content.getvalue())
    response = client.document_text_detection(image=v_image)


    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    texts = response.text_annotations
    text = [text.description for text in texts][0]
    return text

def fuzzy_match(new_tag, tags, theta=85):
    result= process.extractOne(new_tag, tags, scorer=fuzz.partial_token_sort_ratio )
    if result and (result[1] > theta):
        print(f"{new_tag} ==> {result[0]} ; score: {result[1]}")
        return result[0]
    else:
        return None



if __name__ == "__main__":
    note = Note(path)
    note.process()

    info = f'''Note Text:\n{note.raw_text}Tags: {note.raw_tags} '''

    print(info)









