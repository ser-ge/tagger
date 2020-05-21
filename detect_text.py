from google.cloud import vision
import io
from io import BytesIO
import os
from pdf2image import convert_from_path, convert_from_bytes
import glob
from PIL import Image


def ocr_google(content):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/serge/projects/neonotes/googlecreds.json"
    client = vision.ImageAnnotatorClient()
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
    

path ='/Users/serge/Google Drive/NeoNotesPDF/Memo_Note_p11_20200515.pdf'


class Note:

    def __init__(self, path):

        self.img_types = ['png', 'jpg', 'jpeg']
        pdf = ['.pdf']

        self.path = path 
        self.time_modified = os.path.getmtime(self.path)
        self.ext = path.split('.')[-1]
        print("Extension: ", self.ext)

    def load_from_path(self):

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

    def image_to_text(self, service='google'):
        if service == 'google':
            self.raw_text = ocr_google(self.content)

    def extract_tags(self, mode=="linewise"):

        self.raw_tags = []

        if mode == "linewise":
            lines = self.raw_text.split("\n")
            for line in lines:
                words = line.strip().split('#').split(" ")
                words = list(filter(None, words)) # remove empty strings
                tag = " ".join(words)
                self.raw_tags.append(tag)


        if mode == "end": # only single word tags supported in this mode
            end_tags = self.raw_text.replace("\n", " ").replace('\r', ' ').strip().split("#")[1]
            words = tags.split(" ")
            words = list(filter(None, words)) # remove empyt strings
            self.raw_tags.extend(words)






    def tag(self, tags, new_tag=False):
        self.tags = []
        
        for raw_tag in raw_tags:
            matching_tag = fuzzy_match(tag, tags)

            if matching_tag is not None: 
                self.tags.append(matching_tag)

            if matching_tag is None and new_tag:
                self.tags.append(raw_tag)





    def process(self):
        self.load_from_path()
        self.image_to_text()
  
        self.tag()
        return self.image, self.text


if __name__ == "__main__":
    note = Note(path)
    note.process()

    info = f'''Note Text:\n{note.text}Tags: {note.tags}\nLines:{note.lines} '''

    print(info)









