from notion.client import NotionClient
from notion.block import ImageBlock, TextBlock
import os



class NotionNotes:

    def __init__(self, token_v2, notes_collection_url, tags_colleciton_url):

        client = NotionClient(token_v2=token_v2)

        self.notes_collection = client.get_collection_view(notes_collection_url)
        self.tags_collection = client.get_collection_view(tags_colleciton_url)


    def get_tags_from_notion(self):
        self.tags_in_notion = {row.title : row for row in self.tags_collection.default_query().execute()}

    def add_note(self, note):
        self.get_tags_from_notion()
        print(f'extentsion {note.ext}')
        note.process()
        row = self.notes_collection.collection.add_row()
        row.name = note.title
        image_container = row.children.add_new(ImageBlock, width=500)

        path ='upload.jpg'
        text = row.children.add_new(TextBlock)
        text.title = note.raw_text

        note.tag(tags=self.tags_in_notion.keys(), allow_new_tag=True)

        for tag in note.tags:
            try:
                new_tag = self.tags_in_notion[tag]
            except KeyError:
                new_tag = self.tags_collection.collection.add_row()
                new_tag.name = tag

            row.tags = [new_tag, *row.tags]

        temp_file ='temp_upload_file.jpeg'
        note.image.save(path, "JPEG")
        image_container.upload_file(path)





