import io
from io import BytesIO
from typing import List

import os
from pdf2image import convert_from_path, convert_from_bytes
import glob
from PIL import Image
from fuzzywuzzy import process, fuzz
from hashlib import md5
import pickle

from app.ocr import ocr_google
from app.evernote.utils import new_evernote

TAG_MARK = "@"

from app.schemas import File, Note


class Reader:
    """
    Base Class for Processing Scanned Documents (Notes)

    Args:
        file (File): input file object
        target_tags ([str,]): list of target tags against witch found tags are matched
    """

    def __init__(self, target_tags: List[str]):
        self.target_tags = target_tags


    def extract_raw_tags(self, raw_text, mode="linewise"):
        """
        a tag is one or more words on a line begining with @
        one tag per line
        """
        raw_tags = []

        if mode == "linewise":
            lines = raw_text.split("\n")
            for line in lines:
                if TAG_MARK in line:
                    words = line.strip().split(TAG_MARK)[-1].split(" ")
                    words = list(filter(None, words))  # remove empty strings
                    tag = " ".join(words)
                    raw_tags.append(tag)

        if mode == "end":  # only single word tags supported in this mode
            end_tags = (
                raw_text.replace("\r", " ")
                .replace("\n", " ")
                .strip()
                .split(TAG_MARK)[1]
            )

            words = tags.split(" ")
            words = list(filter(None, words))  # remove empty strings
            raw_tags.extend(words)

        return raw_tags


    def match_tags(self,raw_tags, allow_new_tag=False):
        """Match raw tags against a list of target_tags, assign closest match to self.tags"""

        tags = []
        for raw_tag in raw_tags:
            matching_tag = fuzzy_match(raw_tag, self.target_tags)

            if matching_tag is not None:
                tags.append(matching_tag)

            if matching_tag is None and allow_new_tag:
                tags.append(raw_tag)

        return tags

    def parse(self, file):

        note = Note(**file.dict(by_alias=True))

        jpeg_bytes_io = to_jpeg_bytes_io(file.content, file.mime_type)
        raw_text = ocr(jpeg_bytes_io)

        raw_tags = self.extract_raw_tags(raw_text)
        tags = self.match_tags(raw_tags)
        title = raw_text.split("\n")[0]

        note.tags = tags
        note.title = title
        note.text = raw_text

        return note



    def to_evernote(self, note_store, process=True):

        try:
            if process:
                self.process()
            note = new_evernote(
                note_store,
                self.title,
                self.raw_text,
                self.tags,
                jpeg_bytesio=self.content,
            )

            return note

        except Exception as e:
            print(f"{self.name} failed with exception: {e}")

        finally:
            self.content.close()


def ocr(jpeg_bytes_io, service="google"):
    if service == "google":
        raw_text = ocr_google(jpeg_bytes_io)
    return raw_text

def to_jpeg_bytes_io(bytes_io, mime_type):

        if mime_type == "application/pdf":
            image = convert_from_bytes(
                bytes_io.getvalue(), single_file=True
            )[0]
            jpeg_bytes_io = BytesIO()
            image.save(jpeg_bytes_io, format="JPEG")

        elif mime_type in ["image/png", "image/jpg", "image/jpeg"]:
            image = Image.open(bytes_io)
            jpeg_bytes_io = BytesIO()
            image.save(jpeg_bytes_io, format="JPEG")
        else:
            raise TypeError("Invalid file format: only images or pdfs allowed")

        bytes_io.close() # in case BufferedFile is passed rather than in memmory BytesIO

        return jpeg_bytes_io

def fuzzy_match(new_tag, target_tags, theta=65):
    """Find the closest matching tag in target tags"""

    result = process.extractOne(
        new_tag, target_tags, scorer=fuzz.partial_token_sort_ratio
    )
    if result and (result[1] > theta):
        print(f"{new_tag} ==> {result[0]} ; score: {result[1]}")
        return result[0]
    else:
        return None
