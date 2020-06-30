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

    def _load_from_buff(self):

        if self.mime_type == "application/pdf":
            self.image = convert_from_bytes(
                self.content.getvalue(), single_file=True
            )[0]
            self.content.truncate(0)
            self.content.seek(0)
            self.image.save(self.content, format="JPEG")

        elif self.mime_type in ["image/png", "image/jpg", "image/jpeg"]:
            self.content = self.content
            self.image = Image.open(self.content)
            buff = BytesIO()
            self.image.save(buff, format="JPEG")
            self.content = buff

        else:
            raise TypeError("Invalid file format: only images or pdfs allowed")


    def to_text(self, service="google"):
        if service == "google":
            self.raw_text = ocr_google(self.content)
        return self.raw_text

    def extract_raw_tags(self, mode="linewise"):
        """
        a tag is one or more words on a line begining with @
        one tag per line
        """
        self.raw_tags = []

        if mode == "linewise":
            lines = self.raw_text.split("\n")
            for line in lines:
                if TAG_MARK in line:
                    words = line.strip().split(TAG_MARK)[-1].split(" ")
                    words = list(filter(None, words))  # remove empty strings
                    tag = " ".join(words)
                    self.raw_tags.append(tag)

        if mode == "end":  # only single word tags supported in this mode
            end_tags = (
                self.raw_text.replace("\r", " ")
                .replace("\n", " ")
                .strip()
                .split(TAG_MARK)[1]
            )

            words = tags.split(" ")
            words = list(filter(None, words))  # remove empty strings
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
                self.actions[action](self, *params)

            except KeyError:
                raise KeyError

            except Exception as e:
                print(f"Action {action} failed")
                print(e)

    def match_tags(self, allow_new_tag=False):
        """Match raw tags against a list of target_tags, assign closest match to self.tags"""

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

    def parse(self, file):

        self.mime_type = file.mime_type
        self.name = file.name
        self.content = file.content
        self.target_actions = {"new": self.add_new_tag}

        self._load_from_buff()
        self.to_text()
        title = self.raw_text.split("\n")[0]
        self.extract_raw_tags()
        if self.target_actions:
            self.match_actions()
        self.match_tags()
        if self.target_actions:
            self.process_actions()

        note = Note(**file.dict(by_alias=True), tags=self.tags, text=self.raw_text, title=title)

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
