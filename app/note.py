import io
from io import BytesIO
import os
from pdf2image import convert_from_path, convert_from_bytes
import glob
from PIL import Image
from fuzzywuzzy import process, fuzz
from hashlib import md5
import pickle

from app.ocr import ocr_google
from app.evernote.evernote_utils import new_note
TAG_MARK = '@'


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

        self.target_actions = { "new": self.add_new_tag}

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
            buff = BytesIO()
            self.image.save(buff, format='JPEG')
            self.content = buff



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
            '''
            a tag is one or more words on a line begining with @
            one tag per line
            '''
            lines = self.raw_text.split("\n")
            for line in lines:
                if TAG_MARK in line:
                    words = line.strip().split(TAG_MARK)[-1].split(" ")
                    words = list(filter(None, words)) # remove empty strings
                    tag = " ".join(words)
                    self.raw_tags.append(tag)


        if mode == "end": # only single word tags supported in this mode
            end_tags = self.raw_text\
                           .replace('\r', ' ')\
                           .replace("\n", " ")\
                           .strip()\
                           .split(TAG_MARK)[1]

            words = tags.split(" ")
            words = list(filter(None, words)) # remove empty strings
            self.raw_tags.extend(words)

        return self.raw_tags

    def match_actions(self):
        self.matched_actions = {}

        for raw_tag in self.raw_tags:
            first = raw_tag.split(" ")[0]
            rest = raw_tag.split()[1:]
            matching_action = fuzzy_match(first, self.target_actions)

            if matching_action:
                self.actions[matching_action] = rest
                self.raw_tags.remove(raw_tag)

    def process_actions(self):

        for action, params in self.matched_actions.items():
            try:
                 self.actions[action](self,*params)

            except KeyError:
                raise KeyError

            except Exception as e:
                print(f'Action {action} failed')
                print(e)


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

    def add_new_tag(self, *args):
        tag = " ".join(args)

        self.tags += tags

    def process(self):
        """
        Returns:
            title: first line of text
            text: whole text, including first line
            tags: tags matched in target_tags
            image: PIL image object
        """
        if self.file_buff:
            self._load_from_buff()
        else:
            self._load_from_path()
        self.to_text()
        self.title = self.raw_text.split("\n")[0]
        self.extract_raw_tags()
        if self.target_actions: self.match_actions()
        self.match_tags()
        if self.target_actions: self.process_actions()
        return self.title, self.raw_text, self.tags, self.image

    def to_evernote(self, note_store, process=True):

        if process: self.process()
        note = new_note(note_store, self.title, self.raw_text,self.tags, jpeg_bytesio=self.content)

        return note



def fuzzy_match(new_tag, target_tags, theta=65):
    '''Find the closest matching tag in target tags'''

    result= process.extractOne(new_tag, target_tags, scorer=fuzz.partial_token_sort_ratio )
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









