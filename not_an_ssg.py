'''
This is not meant to be a standalone ssg, this is the ssg implimentation part for my website
if you want to use it, disable all the R2-S3 bucket integrations, too lazy to cleanup now, shall do it later maybe
'''

import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
import os
#from r2_bucket import upload, get_bucket_contents

def get_images_all(relative_path = ''):
    with os.scandir(relative_path+"templates/assets/img") as images:
        list_with_posix_scan_iterator =  list(images)
        return [relative_path+'templates/assets/img/'+(image.name) for image in list_with_posix_scan_iterator] 
    
def image_name_cleanup(relative_path = ''):
    for image in get_images_all():
        if " "in image:
            os.rename(relative_path+image, (relative_path+image).replace(" ","_"))
        if "\u202f" in image:
            os.rename(relative_path+image, (relative_path+image).replace("\u202f","_"))

def images_to_upload():
    prev_bucket_contents = ['templates/assets/img/'+ image_name for image_name in get_bucket_contents()]
    list_of_all_images = get_images_all()
    images_not_in_bucket = [image for image in list_of_all_images if image not in prev_bucket_contents]
    if "templates/assets/img/.DS_Store" in images_not_in_bucket: #removing .DS_Store from the list
        images_not_in_bucket.remove("templates/assets/img/.DS_Store")
    return (images_not_in_bucket)

class DefaultImageSizeProcessor(Treeprocessor):
    def run(self, root):
        for img in root.iter('img'):  # Iterate over all <img> elements
            # Change the image filename to 'hello.png' while keeping the original path
            #cleaning up image names
            image_name_cleanup()

            #uploading images
            for image in images_to_upload():
                print(f"Uploading -> {image} right now\n\n")
                upload(image)
            cleaned_name = img.get('src').split('/')[-1]
            img.set('src', f'https://mebin.shop/{cleaned_name}')

            # Set default width and height if not specified
            if 'width' not in img.attrib:
                img.set('width', '780')
            if 'height' not in img.attrib:
                img.set('height', '480')

        return root

class DefaultImageSizeExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(DefaultImageSizeProcessor(md), 'default_image_size', 15)



###################################################


#reading default css
with open('./templates/assets/css/articles_css.css', 'r') as file:
    defaultcss = file.read()

def prettify(markdown_content,css = defaultcss):
    output_html = """<!DOCTYPE html>
                        <html lang="en">

                        <head>
                            <meta charset="utf-8">
                            <style type="text/css">
                        """
    output_html += css
    output_html += """
                            </style>
                        </head>
                        <body>
                            """
    markdown_content = (markdown_content.replace("\n\n\n"," <br><br>\n"))
    markdown_content = (markdown_content.replace("\n\n"," <br>\n"))
    #print(markdown_content)
    output_html += markdown.markdown(markdown_content, extensions=['fenced_code',"nl2br", "attr_list", DefaultImageSizeExtension()]) #fenced_code for code fence ; nl2br for line breaks ; extra for better paragraph handling ; attr_list for specifying width and height for images
    #print(output_html)
    output_html += """

    <br><br><br>
    <center> <p><i> Powered <a href="https://github.com/mebinthattil/Not-An-SSG">Not An SSG </a></i>😎</p> </center> 
    <br>
    <center>
    <a href="https://mebin.in" style="text-decoration: none; color: black;">
    <button class="button">
  <div class="button-box">
    <span class="button-elem">
      <svg viewBox="0 0 46 40" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M46 20.038c0-.7-.3-1.5-.8-2.1l-16-17c-1.1-1-3.2-1.4-4.4-.3-1.2 1.1-1.2 3.3 0 4.4l11.3 11.9H3c-1.7 0-3 1.3-3 3s1.3 3 3 3h33.1l-11.3 11.9c-1 1-1.2 3.3 0 4.4 1.2 1.1 3.3.8 4.4-.3l16-17c.5-.5.8-1.1.8-1.9z"
        ></path>
      </svg>
    </span>
    <span class="button-elem">
      <svg viewBox="0 0 46 40">
        <path
          d="M46 20.038c0-.7-.3-1.5-.8-2.1l-16-17c-1.1-1-3.2-1.4-4.4-.3-1.2 1.1-1.2 3.3 0 4.4l11.3 11.9H3c-1.7 0-3 1.3-3 3s1.3 3 3 3h33.1l-11.3 11.9c-1 1-1.2 3.3 0 4.4 1.2 1.1 3.3.8 4.4-.3l16-17c.5-.5.8-1.1.8-1.9z"
        ></path>
      </svg>
    </span>
  </div>
</button>
</a>
    </center>
                        </body>
                        </html>
                        """
    return output_html
    