
import os
from argparse import ArgumentParser
import os.path
import glob
from time import time
import pickle
from note import Note
from notion_client import NotionNotes




os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/serge/projects/neonotes/googlecreds.json"

token_v2 ='a1bce12825e34bec193155b95765edddb3d1f85ded3ba139e4a5ad23a213a565ffe7d3a8bc4d7870aace1ec1f13361eb4902b586df9d04d3ae992b215cffc93cdf5a921c4a84e288d8e7e424ebbf'
notes_collection_url = "https://www.notion.so/6cc22d25fb6b4b7c9b7f62a290851d15?v=1a34498ef4724620aa555ac7b7a671e1"
tags_colleciton_url = "https://www.notion.so/5a145aae97344da7b28b7a0720eec707?v=347b6b7816624927a70eb3d650c11633"




def main():

    new_notes = []


    try:
        last_run = pickle.load(open("last_run.p", "rb"))
    except FileNotFoundError:
        last_run = False
        print("false")


    for path in glob.glob("/Users/serge/Google Drive/NeoNotesPDF/*.pdf"):
        if not last_run or os.path.getmtime(path) > last_run:
            print("found notes to update")
            new_notes.append(path)


    notion_client = NotionNotes(token_v2,notes_collection_url, tags_colleciton_url)
    for path in new_notes:
        notion_client.add_note(Note(path))


    pickle.dump(time(), open("last_run.p", "wb"))


if __name__ == "__main__":
    main()
