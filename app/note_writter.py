import xml.etree.ElementTree as ET
import binascii
import hashlib
import os
from typing import List

from evernote.api.client import EvernoteClient
import evernote.edam.type.ttypes as Types

from app.evernote import evernote_patch
from app.schemas import Note



class NoteRepo:

    '''
    Evernote Wrapper for creating and updating notes
    Note.tags <-> evernote tags
    Note.folder <-> evernote notebooks
    '''

    def __init__(self, token):

        self._note_store = build_evernote_store(token)

    @property
    def folders(self) -> List[str]:
        note_books = self._note_store.ListNotebooks()
        folders = [note_book.name for note_book in note_books]

        return folders

    @property
    def tags(self) -> List[str]:
        ever_tags = self._note_store.listTags()
        tags = [tag.name for tag in ever_tags]

        return tags

    def update(id, text=None, timage=None, ags=None, folder=None):
        pass

    def create(note: Note) -> Note:
        ever_note = new_evernote(self._note_store, note)
        note.target = self.service
        note.target_id = ever_note.guid

        return note




def build_evernote_store(token):
    client = EvernoteClient(token=token, sandbox=False, china=False)
    note_store = client.get_note_store()
    return note_store

def new_evernote(note_store, note):
    ''' creates blank note and calls evenrote api to add to notestore '''

    noteTitle = note.title
    note_text = note.text
    jpeg_bytesio = note.content
    parentNotebook = note.folder
    nBody = '<?xml version="1.0" encoding="UTF-8"?>'
    nBody += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'

    ## Create note object
    ourNote = Types.Note()
    ourNote.title = noteTitle
    ourNote.tagNames = tags
    ourNote.content = nBody
    ourNote.content +='<en-note>'
    if jpeg_bytesio:
        ourNote = add_jpeg(ourNote, jpeg_bytesio)
    ## parentNotebook is optional; if omitted, default notebook is used
    if parentNotebook and hasattr(parentNotebook, 'guid'):
        ourNote.notebookGuid = parentNotebook.guid

    ourNote.content +='</en-note>'
    ## Attempt to create note in Evernote account
    try:
        note = note_store.createNote(ourNote)
    except Exception as edue:
        ## Something was wrong with the note data
        ## See EDAMErrorCode enumeration for error code explanation
        ## http://dev.evernote.com/documentation/reference/Errors.html#Enum_EDAMErrorCode
        print("EDAMUserException:", edue)
        return None
    except Exception as ednfe:
        ## Parent Notebook GUID doesn't correspond to an actual notebook
        print("EDAMNotFoundException: Invalid parent notebook GUID")
        return None

    ## Return created note object
    return note


def add_jpeg(note, jpeg_bytesio):
    '''Add jpeg  attachment to evernote note from BytesIo object'''
    image = jpeg_bytesio.getvalue()
    md5 = hashlib.md5()
    md5.update(image)
    hash = md5.digest()

    data = Types.Data()
    data.size = len(image)
    data.bodyHash = hash
    data.body = image

    resource = Types.Resource()
    resource.mime = 'image/jpeg'
    resource.data = data

    # Now, add the new Resource to the note's list of resources
    note.resources = [resource]
    # To display the Resource as part of the note's content, include an <en-media>
    # tag in the note's ENML content. The en-media tag identifies the corresponding
    # Resource using the MD5 hash.

    # The content of an Evernote note is represented using Evernote Markup Language
    # (ENML). The full ENML specification can be found in the Evernote API Overview
    # at http://dev.evernote.com/documentation/cloud/chapters/ENML.php
    hash_hex = binascii.hexlify(hash)
    hash_str = hash_hex.decode("UTF-8")
    note.content += '<en-media type="image/png" hash="{}"/>'.format(hash_str)
    return note
