import os
import json
import hashlib

from .r2_bucket import upload, get_bucket_contents
from .not_an_ssg import render


#returning list of names of all articles in the articles directory orders with newest articles first
def get_articles():
    with os.scandir("articles/markdown_files") as articles:
        list_with_posix_scan_iterator =  [article for article in articles if article.name[-3:] == ".md"]
        list_with_posix_scan_iterator.sort(key = lambda x: x.stat().st_ctime, reverse=True)
        articles_list = [article.name for article in list_with_posix_scan_iterator]
        if ".obsidian" in articles_list:
            articles_list.remove(".obsidian")
        return articles_list
    
def get_file_hash(filepath):
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(4096):  # Read file in chunks
                hasher.update(chunk)
    except FileNotFoundError:
        return None
    return hasher.hexdigest()

def prev_hash(prev_file_name):
    with open("hash_tracker.json", "r") as f:
        data = json.load(f)
        return data.get(prev_file_name)

def detect_file_changes(filename): #return false if NO changes in file
    return get_file_hash(filename) != prev_hash(filename)

def update_hash(filename):
    new_hash = get_file_hash(filename)
    with open("hash_tracker.json","r") as f: #load
        json_data = json.load(f)
    json_data[filename] = new_hash #update
    with open("hash_tracker.json","w") as f: #dump
        json.dump(json_data,f)

def get_images(relative_path = ""):
    with os.scandir(relative_path+"templates/assets/img") as images:
        list_with_posix_scan_iterator =  list(images)
        return [relative_path+'templates/assets/img/'+(image.name) for image in list_with_posix_scan_iterator] 

def cleanup_image_names(relative_path = ""):
    for image in get_images():
        if " "in image:
            os.rename(relative_path+image, (relative_path+image).replace(" ","_"))
        if "\u202f" in image:
            os.rename(relative_path+image, (relative_path+image).replace("\u202f","_"))

def images_to_upload():
    prev_bucket_contents = ['templates/assets/img/'+ image_name for image_name in get_bucket_contents()]
    list_of_all_images = get_images()
    images_not_in_bucket = [image for image in list_of_all_images if image not in prev_bucket_contents]
    if "templates/assets/img/.DS_Store" in images_not_in_bucket: #removing .DS_Store from the list
        images_not_in_bucket.remove("templates/assets/img/.DS_Store")
    return (images_not_in_bucket)

def markdowns_to_rebuild():
    '''Iterating through each article in the markdown_files folder and checking for any hash changes'''

    list_of_articles_to_rebuild = []
    list_of_articles = get_articles()
    for article in list_of_articles:
        article = "articles/markdown_files/"+article
        if detect_file_changes(article):
            list_of_articles_to_rebuild.append(article)
            update_hash(article)

    return(list_of_articles_to_rebuild)


def build_html(article):
    with open(article, "r", encoding="utf-8") as file:
        article_data = file.read()

    html = render(article_data)

    #formatting from absolute path to just file name
    article_name = article.split('/')[-1][:-3]
    with open(f"templates/builds/{article_name}.html","w") as file:
        file.write(html)


'''Main Build Function'''
def build():
    
    #cleaning up image names
    cleanup_image_names()

    #uploading images
    for image in images_to_upload():
        print(f"Uploading -> {image} right now\n\n")
        upload(image)
        
    #building html files
    for markdown in markdowns_to_rebuild():
        print(f"Building -> {markdown} right now\n\n")
        build_html(markdown)

    

    print("Done with all builds and uploads")

def build_n_upload_images_only():
    #cleaning up image names
    cleanup_image_names()

    #uploading images
    for image in images_to_upload():
        print(f"Uploading -> {image} right now\n\n")
        upload(image)


if __name__ == "__main__":
    build()