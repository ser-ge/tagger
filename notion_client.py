from notion.client import NotionClient
from notion.block import ImageBlock, TextBlock
from fuzzywuzzy import process, fuzz


client = NotionClient(token_v2 ='a1bce12825e34bec193155b95765edddb3d1f85ded3ba139e4a5ad23a213a565ffe7d3a8bc4d7870aace1ec1f13361eb4902b586df9d04d3ae992b215cffc93cdf5a921c4a84e288d8e7e424ebbf')

def note2notion(image, note_text):
    notes_collection = client.get_collection_view("https://www.notion.so/7189ca907b6d48eeaa124145ea9ce2f1?v=658ec8dff5844320aad4935a2564e170")
    tags_collection = client.get_collection_view("https://www.notion.so/5a145aae97344da7b28b7a0720eec707?v=347b6b7816624927a70eb3d650c11633")

    for row in notes_collection.collection.get_rows():
        print(row.name)

    row = notes_collection.collection.add_row()
    row.name = note_text.split("\n")[0]
    image_container = row.children.add_new(ImageBlock, width=500)
    path ='upload.jpg'
    text = row.children.add_new(TextBlock)
    text.title = note_text
    try:
        print(note_text)
        tags = note_text.replace("\n", " ").replace('\r', ' ').strip().split("#")[1]

        print(tags)

        tags = tags.split(" ")
        tags = list(filter(None, tags))
        print(tags)


        for tag in tags:
            print(tag)
            tags_in_notion = [row.title for row in tags_collection.default_query().execute()]
            print(f"Found existing tags {tags_in_notion}")
            if not fuzzy_match(tag, tags_in_notion):
                print(f"creating new tag {tag}")
                new_tag = tags_collection.collection.add_row()
                new_tag.name = tag
            else:
                match = tags_collection.default_query().execute()
                closest = fuzzy_match(tag, tags_in_notion)
                new_tag = next(filter(lambda x : x.title == closest ,match))

            print(f"adding tag: {new_tag}")
            row.tags= [new_tag, *row.tags]
            print("Tags:")
            print(row.tags)
    

    except IndexError as e:
        pass

    image.save(path, "JPEG")
    image_container.upload_file(path)



def fuzzy_match(new_tag, tags, theta=85):
    result= process.extractOne(new_tag, tags, scorer=fuzz.partial_token_sort_ratio )
    if result and (result[1] > theta):
        print(f"{new_tag} ==> {result[0]} ; score: {result[1]}")
        return result[0]
    else:
        return False
