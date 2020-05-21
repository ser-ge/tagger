from detect_text import pdf2note
from notion_client import note2notion
import os
from argparse import ArgumentParser
import os.path
import glob
from time import time
import pickle
from detect_text import Note 




os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/serge/projects/neonotes/googlecreds.json"

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



# for note in new_notes:
#     (image, text) = pdf2note(note)
#     note2notion(image, text)

for path in new_notes:
    (image, text) = Note(path).process()
    note2notion(image, text)

pickle.dump(time(), open("last_run.p", "wb"))


# def is_valid_file(parser, arg):
#     if not os.path.exists(arg):
#         parser.error("The file %s does not exist!" % arg)
#     else:
#         return open(arg, 'r')  # return an open file handle


# parser = ArgumentParser(description="Upload note scan to notion")

# parser.add_argument("-i", dest="filename", required=True,
#                     help="input path to pdf scan to upload to notion", metavar="FILE",
#                     type=lambda x: is_valid_file(parser, x))
# args = parser.parse_args()

# print(f"Input {args.filename}")
# print(args)