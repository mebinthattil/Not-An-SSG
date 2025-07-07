import markdown
import os
import ui_components
import json
from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from dotenv import load_dotenv


def verbose_decorator(func):
    def wrapper(*args, **kwargs):
        verbose = kwargs.get('verbose', False)
        result = func(*args, **kwargs)
        if verbose:
            if isinstance(result, (list, tuple, dict)):
                for item in result:
                    print(item)
            else:
                print(result)
        
        return result
    return wrapper

# === HANDLE IMAGES ===

def load_config():
    load_dotenv()
    config = {}
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

    except FileNotFoundError:
        print("Warning: config.json not found. Using default image dimensions. This usually means you have not ran the setup script. Please run setup.py.")
        config = {"image_dimensions": {"width": 800, "height": 500}}
    
    return config


def get_images_all(relative_path=''):
    img_dir = os.path.join(relative_path, "templates", "assets", "img")
    if not os.path.exists(img_dir):
        print(f"Image directory {img_dir} does not exist")
        return []
    
    try:
        with os.scandir(img_dir) as images:
            list_with_posix_scan_iterator =  list(images)
            return [os.path.join(img_dir, image.name) for image in list_with_posix_scan_iterator if image.is_file()]
    except Exception as e:
        print(f"Error scanning image directory: {e}")
        return []


def image_name_cleanup(relative_path=''):
    try:
      for image in get_images_all():
          weird_chars = [" ", "\u202f", "%20"]
          for char in weird_chars:
              if char in image:
                  os.rename(relative_path+image, (relative_path+image).replace(char,"_"))
    except:
        print("Error, send for re-build")


def images_to_upload():
    """
    Determine which images need to be uploaded to the bucket, skip images that are already in the bucket and bs like .DS_Store
    """
    try:
        # Import bucket functions if available
        from r2_bucket import get_bucket_contents
        
        prev_bucket_contents = ['templates/assets/img/' + image_name for image_name in get_bucket_contents()]
        list_of_all_images = get_images_all()
        images_not_in_bucket = [image for image in list_of_all_images if image not in prev_bucket_contents]
        
        if "templates/assets/img/.DS_Store" in images_not_in_bucket: #removing .DS_Store from the list
            images_not_in_bucket.remove("templates/assets/img/.DS_Store")
        return (images_not_in_bucket)
        
    except ImportError:
        print("Warning: r2_bucket module not available. Skipping bucket operations.")
        return []
    except Exception as e:
        print(f"Error checking bucket contents: {e}")
        return []


class DefaultImageSizeProcessor(Treeprocessor):
    def __init__(self, md, config=None):
        super().__init__(md)
        self.config = config or {"image_dimensions": {"width": 800, "height": 500}}
    
    def run(self, root):
        load_dotenv()
        cdn_url = os.getenv('CDN_URL', 'https://your-amazing-non-existant-cdn.com')
        
        for img in root.iter('img'):
            image_name_cleanup()
            
            bucket_name = os.getenv('STORAGE_BUCKET_NAME')
            if bucket_name:
                try:
                    from r2_bucket import upload
                    for image in images_to_upload():
                        print(f"Uploading -> {image}")
                        upload(image)
                except ImportError:
                    print("Warning: r2_bucket module not available for uploading")
                except Exception as e:
                    print(f"Error uploading images: {e}")
            
            cleaned_name = img.get('src').split('/')[-1]

            weird_chars = [" ", "\u202f", "%20"]
            for char in weird_chars:
                if char in cleaned_name:
                    cleaned_name = cleaned_name.replace(char,"_")

            img.set('src', f'{cdn_url}/{cleaned_name}')
            
            dimensions = self.config.get('image_dimensions', {})
            default_width = str(dimensions.get('width', 800))
            default_height = str(dimensions.get('height', 500))
            
            if 'width' not in img.attrib:
                img.set('width', default_width)
            if 'height' not in img.attrib:
                img.set('height', default_height)
        
        return root


class DefaultImageSizeExtension(Extension):
    """
    Markdown extension to apply default image sizing
    """
    def __init__(self, config=None, **kwargs):
        self.config = config
        super().__init__(**kwargs)
    
    def extendMarkdown(self, md):
        processor = DefaultImageSizeProcessor(md, self.config)
        md.treeprocessors.register(processor, 'default_image_size', 15)


# === RENDER & SERVE ===

def render(markdown_content, root_location="https://google.com", css=None):
    if css is None:
        css = read_stylsheet()
    config = load_config()
    
    output_html = ui_components.html_header_with_stylesheet(css)

    extensions = ['fenced_code', 'codehilite', 'nl2br', 'tables', 'attr_list', DefaultImageSizeExtension(config)]
    
    output_html += markdown.markdown(markdown_content, extensions=extensions)

    output_html += ui_components.not_an_ssg_footer()
    output_html += ui_components.return_home_btn(root_location)

    return output_html

def serve(output_html_path = '/generated.html', port = 6969, open_browser = True):
    import http.server
    import webbrowser

    class SimpleHTMLServer(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = output_html_path 
            return super().do_GET()

    def start_server():
        server = http.server.HTTPServer(("", port), SimpleHTMLServer)
        if open_browser:
            webbrowser.open(f"http://localhost:{port}")
        else:
            print(f"Serving on http://localhost:{port}")

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped by user.")
            server.server_close() 

    start_server()


# === CSS RELATED FUNCTIONS ===
@verbose_decorator
def generate_theme_css(theme_name='monokai', verbose = False):
    pre_text = "\n/* Start syntax highlighting for code fences */\n"
    post_text = "\n/* End syntax highlighting for code fences */"
    formatter = HtmlFormatter(style=theme_name)
    return pre_text + formatter.get_style_defs('.codehilite') + post_text

def read_stylsheet(path_to_stylesheet = "./articles_css.css", read_mode = "read"):
    with open(path_to_stylesheet, 'r') as file:
        func = getattr(file, read_mode)
        return func()

def write_stylsheet(css_content, path_to_stylesheet = "./articles_css.css", write_mode = "write") -> None:
    with open(path_to_stylesheet, 'w') as file:
        func = getattr(file, write_mode)
        func(css_content)

@verbose_decorator
def set_theme(style_sheet_path, theme_name, verbose = False):
    css = remove_theme(style_sheet_path)
    css_generated = generate_theme_css(theme_name).splitlines(keepends=True)
    write_stylsheet(css + css_generated, style_sheet_path, write_mode="writelines")

@verbose_decorator    
def remove_theme(sytle_sheet_path, verbose = False) -> str: # Removes the theme and also returns the remaining css contents
    css = read_stylsheet(sytle_sheet_path, read_mode="readlines")
    new_css, read_flag = [], True

    for line in css:
        if "/* Start syntax highlighting for code fences */" in line:
            read_flag = False
        elif "/* End syntax highlighting for code fences */" in line:
            read_flag = True
            continue

        if read_flag:
            new_css.append(line)
    write_stylsheet(new_css, sytle_sheet_path, write_mode="writelines")
    return new_css

@verbose_decorator
def list_themes(verbose = False):
    return list(get_all_styles())


# === TESTING ===
f = open("demo_comprehensive.md","r")
markdown_content = f.read()
f.close()

f = open("generated.html","w")
f.write(render(markdown_content))
f.close()


#print(generate_theme_css())
#set_theme("./articles_css.css", "stata-dark")
#remove_theme("./articles_css.css")

render(markdown_content)
serve()
