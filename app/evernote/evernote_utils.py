import  evernote.edam.type.ttypes as Types
import xml.etree.ElementTree as ET
import binascii
import hashlib

from evernote.api.client import EvernoteClient
from app.evernote import evernote_patch




def make_note_store(token=None):

    if token is None:
        token = os.getenv('EVERNOTE_TOKEN') # TODO implement oauth flow for evernote

    client = EvernoteClient(token=token, sandbox=False, china=False)
    note_store = client.get_note_store()
    return note_store


def new_note(note_store, noteTitle, jpeg_bytesio=None, parentNotebook=None):
    ''' creates blank note and calls evenrote api to add to notestore '''

    nBody = '<?xml version="1.0" encoding="UTF-8"?>'
    nBody += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
    nBody += '<en-note>%s</en-note>' % noteBody

    ## Create note object
    ourNote = Types.Note()
    ourNote.title = noteTitle
    ourNote.content = nBody

    if jpeg_bytesio:
        ourNote = add_jpeg(ourNote, jpeg_bytesio)
    ## parentNotebook is optional; if omitted, default notebook is used
    if parentNotebook and hasattr(parentNotebook, 'guid'):
        ourNote.notebookGuid = parentNotebook.guid

    ## Attempt to create note in Evernote account
    try:
        note = note_store.createNote(ourNote)
    except Errors.EDAMUserException as edue:
        ## Something was wrong with the note data
        ## See EDAMErrorCode enumeration for error code explanation
        ## http://dev.evernote.com/documentation/reference/Errors.html#Enum_EDAMErrorCode
        print("EDAMUserException:", edue)
        return None
    except Errors.EDAMNotFoundException as ednfe:
        ## Parent Notebook GUID doesn't correspond to an actual notebook
        print("EDAMNotFoundException: Invalid parent notebook GUID")
        return None

    ## Return created note object
    return note

def add_text(note, text):

    content  = ET.fromstring(note)
    text = content.attrib.get('en-note')
    print(text)






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
    resource.mime = 'image/png'
    resource.data = data

# Now, add the new Resource to the note's list of resources
    note.resources = [resource]

# To display the Resource as part of the note's content, include an <en-media>
# tag in the note's ENML content. The en-media tag identifies the corresponding
# Resource using the MD5 hash.
    hash_hex = binascii.hexlify(hash)
    hash_str = hash_hex.decode("UTF-8")

# The content of an Evernote note is represented using Evernote Markup Language
# (ENML). The full ENML specification can be found in the Evernote API Overview
# at http://dev.evernote.com/documentation/cloud/chapters/ENML.php
    note.content += '</en-note>'

# Finally, send the new note to Evernote using the createNote method
# The new Note object that is returned will contain server-generated
# attributes such as the new note's unique GUID.


if __name__ == "__main__":
    test_note = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-export SYSTEM "http://xml.evernote.com/pub/evernote-export3.dtd">
<en-export export-date="20200611T165853Z" application="Evernote" version="Evernote Mac 6.13.1 (455785)">
<note><title>stuff</title><content><![CDATA[<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">

<en-note><div><br/></div><div>Sunningdale</div><div>riptide9</div><div><br/></div><div>9.94</div><div><br/></div><div>1656.43</div><div><br/></div></en-note>]]></content><created>20171113T161145Z</created><updated>20180316T160229Z</updated><note-attributes><author>Serge</author><source>desktop.win</source><source-application>evernote.win32</source-application><reminder-order>0</reminder-order></note-attributes></note>
</en-export>"""

    add_text(test_note, "hello")
