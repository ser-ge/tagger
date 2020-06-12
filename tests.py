from app.note import Note
from app.evernote import evernote_utils as e


if __name__ == "__main__":
    store = e.make_note_store()
    note = Note("cli_prototype/downloads/test.pdf", None, ['reporting'])
    note.to_evernote(store)
