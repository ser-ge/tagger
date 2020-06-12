from functools import wraps
import pickle
from google.cloud import vision
from hashlib import md5

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




