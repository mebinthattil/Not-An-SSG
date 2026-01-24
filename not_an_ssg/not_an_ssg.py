import os
import sys
import json

from . import ui_components
from .r2_bucket import upload, get_bucket_contents
import markdown
from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from dotenv import load_dotenv

# For accessing files bundled in the package such as css files
try:
    from importlib.resources import files as package_files
except ImportError:
    from importlib_resources import files as package_files # Fallback for older Python versions

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_package_resource(filename):
    """
    Get a resource file from the installed package.
    This needs to be done to ensure compatibility, sometimes due to packaging we can't directly access files relatively.
    """
    return package_files('not_an_ssg') / filename

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
    """
    Load configuration from .env and config.json in the current working directory.
    
    Uses defaults if files don't exist (no fallback to package directory).
    """
    load_dotenv('.env')
    
    config = {"image_dimensions": {"width": 800, "height": 500}}
    
    if os.path.exists('config.json'): # Try to load from CWD
        try:
            with open('config.json', 'r') as f:
                user_config = json.load(f)
                config.update(user_config) # Merging this with config dict
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config.json: {e}")
    
    return config


def get_images_all(base_path=''):
    """
    Get all images from the templates/assets/img directory or from base_path if provided.
    Returns a list of image file paths.
    """
    if base_path:
        img_dir = os.path.join(base_path, "templates", "assets", "img")
    else:
        img_dir = os.path.join(os.getcwd(), "templates", "assets", "img")
    
    if not os.path.exists(img_dir):
        print(f"Image directory {img_dir} does not exist")
        return []
    
    try:
        with os.scandir(img_dir) as images:
            return [os.path.join(img_dir, image.name) for image in images if image.is_file()]

    except Exception as e:
        print(f"Error scanning image directory: {e}")
        return []


def image_name_cleanup(base_path=''):
    try:
        for image in get_images_all(base_path):
            weird_chars = [" ", "\u202f", "%20"]
            for char in weird_chars:
                if char in image:
                    old_path = image
                    new_path = image.replace(char, "_")
                    os.rename(old_path, new_path)
    except Exception as e:
        print(f"Error during image cleanup: {e}")


def images_to_upload(base_path=''):
    """
    Determine which images need to be uploaded to the bucket, skip images that are already in the bucket and bs like .DS_Store
    """
    try:
        if SCRIPT_DIR not in sys.path:
            sys.path.insert(0, SCRIPT_DIR)
        
        bucket_contents = get_bucket_contents()
        if bucket_contents is None:
            bucket_contents = []
        
        list_of_all_images = get_images_all(base_path)
        
        images_not_in_bucket = []
        for image_path in list_of_all_images:
            filename = os.path.basename(image_path)
            if filename.startswith('.'):
                continue
                
            if filename not in bucket_contents:
                images_not_in_bucket.append(image_path)
        
        return images_not_in_bucket
        
    except ImportError:
        print("Warning: r2_bucket module not available. Skipping bucket operations. This means images might not render properly. Please make sure installation was done right.")
        return []
    except Exception as e:
        print(f"Error checking bucket contents: {e}")
        return []


class DefaultImageSizeProcessor(Treeprocessor):
    def __init__(self, md, config=None, input_file_dir=None, verbose=False):
        super().__init__(md)
        self.config = config or {"image_dimensions": {"width": 800, "height": 500}}
        self.input_file_dir = input_file_dir or os.getcwd()
        self.verbose = verbose
    
    def run(self, root):
        load_dotenv('.env')
        cdn_url = os.getenv('CDN_URL', 'https://your-amazing-non-existant-cdn.com')
        
        if self.verbose:
            print("STARTING, SCRIPT IS RUNNING FROM : ", os.getcwd())
        
        for img in root.iter('img'):
            image_name_cleanup(self.input_file_dir)
            
            bucket_name = os.getenv('STORAGE_BUCKET_NAME')
            if bucket_name:
                try:

                    if SCRIPT_DIR not in sys.path:
                        sys.path.insert(0, SCRIPT_DIR)

                    images_to_upload_list = images_to_upload(self.input_file_dir)
                    if self.verbose:
                        if images_to_upload_list:
                            print(f"Found {len(images_to_upload_list)} new images to upload")
                        else:
                            print("No new images to upload - all images already in bucket")
                    
                    for image in images_to_upload_list:
                        if self.verbose:
                            print(f"Uploading -> {image}")
                        upload(image, self.verbose)
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
            if self.verbose:
                print(f"Image src set to: {cdn_url}/{cleaned_name}")
            
            dimensions = self.config.get('image_dimensions', {})
            default_width = str(dimensions.get('width', 800))
            default_height = str(dimensions.get('height', 500))
            
            if 'width' not in img.attrib:
                img.set('width', default_width)
            if 'height' not in img.attrib:
                img.set('height', default_height)
        
        return root


class DefaultImageSizeExtension(Extension):
    def __init__(self, config=None, input_file_dir=None, verbose=False, **kwargs):
        self.config = config
        self.input_file_dir = input_file_dir
        self.verbose = verbose
        super().__init__(**kwargs)
    
    def extendMarkdown(self, md):
        processor = DefaultImageSizeProcessor(md, self.config, self.input_file_dir, self.verbose)
        md.treeprocessors.register(processor, 'default_image_size', 15)


# === RENDER & SERVE ===

def render(markdown_content, root_location="https://google.com", css=None, input_file_path=None, verbose=False):
    """
    Convert markdown content to styled HTML.
    
    Args:
        markdown_content: The markdown text to render (string, not a file path).
        root_location: URL for the home button.
        css: Optional custom CSS string. Uses package default if None.
        input_file_path: Path to source file (for relative image paths).
        verbose: Enable verbose output.
    
    Returns:
        Complete HTML string ready to be written to a file.
    
    Example usage:
        html = render(open('post.md').read())
        open('output.html', 'w').write(html)
    """
    if css is None:
        css = read_stylsheet()
    config = load_config()
    
    input_file_dir = None
    if input_file_path:
        input_file_dir = os.path.dirname(os.path.abspath(input_file_path))
    
    output_html = ui_components.html_header_with_stylesheet(css)

    extensions = ['fenced_code', 'codehilite', 'nl2br', 'tables', 'attr_list', DefaultImageSizeExtension(config, input_file_dir, verbose)]
    
    output_html += markdown.markdown(markdown_content, extensions=extensions)

    output_html += ui_components.not_an_ssg_footer()
    output_html += ui_components.return_home_btn(root_location)

    return output_html

def serve(output_html_path='/generated.html', port=6969, open_browser=True):
    """
    Start a local HTTP server to serve an HTML file.
    
    Args:
        output_html_path: Path to the HTML file to serve (must start with /).
        port: Port number for the server.
        open_browser: Automatically open browser.
    
    Note:
        The file must exist before calling serve(). This function serves
        files from the current directory, not HTML content directly.
    
    Example:
        serve('/output.html', port=8080)
    """
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

def read_stylsheet(path_to_stylesheet=None, read_mode="read"):
    """
    Read a stylesheet file. 
    If path_to_stylesheet is None -> read the default CSS from the package.
    Else, read from file path.
    """
    if path_to_stylesheet is None: # Use default package css
        resource = get_package_resource("articles_css.css")
        with resource.open('r') as file:
            func = getattr(file, read_mode)
            return func()
    else: # Read from given stylesheet path
        with open(path_to_stylesheet, 'r') as file:
            func = getattr(file, read_mode)
            return func()

def write_stylsheet(css_content, path_to_stylesheet, write_mode="write") -> None:
    """
    Write content to a stylesheet file.
    
    Note: path_to_stylesheet is required since package resources are read-only.
    Use export_default_css() to create a writable copy of the default CSS first.
    """
    if path_to_stylesheet is None:
        raise ValueError("path_to_stylesheet is required. Package resources are read-only. "
                        "Use export_default_css() to create a writable copy first.")
    with open(path_to_stylesheet, 'w') as file:
        func = getattr(file, write_mode)
        func(css_content)


def export_default_css(output_path="articles_css.css"):
    """
    Export the default CSS to a file in the current directory.
    
    This creates a writable copy that can then be modified with set_theme().
    """
    css_content = read_stylsheet()  # Reads from package
    with open(output_path, 'w') as f:
        f.write(css_content)
    return output_path

@verbose_decorator
def set_theme(style_sheet_path=None, theme_name="stata-dark", verbose=False):
    """
    Set syntax highlighting theme on a stylesheet.
    
    If style_sheet_path is None, exports default CSS to 'articles_css.css' in CWD first. (creating a writable copy; refer to README: Breaking Changes[1])
    """
    if style_sheet_path is None:
        # Create writable copy of default CSS in current directory
        style_sheet_path = export_default_css()
        if verbose:
            print(f"Created {style_sheet_path} from package defaults")
    css = remove_theme(style_sheet_path, verbose=verbose)
    css_generated = generate_theme_css(theme_name).splitlines(keepends=True)
    write_stylsheet(css + css_generated, style_sheet_path, write_mode="writelines")

@verbose_decorator    
def remove_theme(style_sheet_path, verbose=False) -> list:
    """
    Remove syntax highlighting theme from a stylesheet.
    
    Returns the remaining CSS content as a list of lines.
    Note: style_sheet_path is required since we need to write to it. (create a writable copy for css first; refer to README: Breaking Changes[1])
    """
    css = read_stylsheet(style_sheet_path, read_mode="readlines")
    new_css, read_flag = [], True

    for line in css:
        if "/* Start syntax highlighting for code fences */" in line:
            read_flag = False
        elif "/* End syntax highlighting for code fences */" in line:
            read_flag = True
            continue

        if read_flag:
            new_css.append(line)
    write_stylsheet(new_css, style_sheet_path, write_mode="writelines")
    return new_css

@verbose_decorator
def list_themes(verbose = False):
    return list(get_all_styles())


'''
# === TESTING ===
f = open("demo_comprehensive.md","r")
markdown_content = f.read()
f.close()

f = open("generated.html","w")
f.write(render(markdown_content))
f.close()
'''

#render(markdown_content)
#serve()










# === CLI INTERFACE ===
import argparse

def cli_main():
    """
    Main CLI interface for Not An SSG
    """
    # Import version from package
    from . import __version__
    
    parser = argparse.ArgumentParser(
        prog='not_an_ssg',
        description="Not An SSG - This is not an SSG. It's a jackfruit",
        epilog='''
Examples:
  %(prog)s render my_article.md                           # Render markdown to HTML
  %(prog)s render my_article.md --output blog.html        # Render with custom output
  %(prog)s render my_article.md -v                        # Render with verbose output
  %(prog)s build ./articles -o ./public                   # Build directory (incremental)
  %(prog)s build ./articles -o ./public --force           # Force rebuild all files
  %(prog)s build -v                                       # Build with defaults and verbose
  %(prog)s serve --port 8080                              # Start server on port 8080
  %(prog)s serve -v                                       # Start server with verbose output
  %(prog)s run my_article.md                              # Render and serve in one command
  %(prog)s run my_article.md --watch                      # Render, serve, and watch for changes
  %(prog)s run my_article.md --port 8080 --watch -v       # Custom port with file watching and verbose
  %(prog)s themes list                                    # List available themes
  %(prog)s themes set monokai -v                          # Set syntax highlighting theme with verbose
  %(prog)s themes generate dracula --output dark.css      # Generate theme CSS
  %(prog)s config setup -v                                # Run setup wizard with verbose output

Getting additional info on commands:
  %(prog)s render -h                                      # Show help for render command
  %(prog)s build -h                                       # Show help for build command
  %(prog)s serve -h                                       # Show help for serve command
  %(prog)s run -h                                         # Show all options for run command
  %(prog)s themes list -h                                 # Show help for themes list subcommand
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add version flag
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # === RENDER COMMAND ===
    render_parser = subparsers.add_parser(
        'render', 
        help='Render markdown file to HTML',
        description='Convert a markdown file to styled HTML. Example: not_an_ssg render blog.md -o blog.html'
    )
    render_parser.add_argument('input', help='Input markdown file path')
    render_parser.add_argument('-o', '--output', default='generated.html',
                              help='Output HTML file path (default: generated.html)')
    render_parser.add_argument('-c', '--css', help='Custom CSS file path')
    render_parser.add_argument('-r', '--root', default='https://mebin.in',
                              help='Root URL for the return home button (default: https://mebin.in)')
    render_parser.add_argument('--no-images', action='store_true',
                              help='Skip image processing and uploading')
    render_parser.add_argument('-v', '--verbose', action='store_true',
                              help='Enable verbose output for debugging')
    
    # === SERVE COMMAND ===
    serve_parser = subparsers.add_parser(
        'serve', 
        help='Start development server',
        description='Start a local HTTP server. Example: not_an_ssg serve -f /blog.html -p 8080'
    )
    serve_parser.add_argument('-p', '--port', type=int, default=6969,
                             help='Server port (default: 6969)')
    serve_parser.add_argument('-f', '--file', default='/generated.html',
                             help='HTML file to serve (default: /generated.html)')
    serve_parser.add_argument('--no-browser', action='store_true',
                             help="Don't automatically open browser")
    serve_parser.add_argument('-v', '--verbose', action='store_true',
                             help='Enable verbose output for debugging')
    
    # === RUN COMMAND ===
    run_parser = subparsers.add_parser('run', help='Render markdown and start development server')
    run_parser.add_argument('input', help='Input markdown file path')
    run_parser.add_argument('-o', '--output', default='generated.html',
                           help='Output HTML file path (default: generated.html)')
    run_parser.add_argument('-c', '--css', help='Custom CSS file path')
    run_parser.add_argument('-r', '--root', default='https://mebin.in',
                           help='Root URL for the return home button (default: https://mebin.in)')
    run_parser.add_argument('-p', '--port', type=int, default=6969,
                           help='Server port (default: 6969)')
    run_parser.add_argument('--no-browser', action='store_true',
                           help="Don't automatically open browser")
    run_parser.add_argument('--no-images', action='store_true',
                           help='Skip image processing and uploading')
    run_parser.add_argument('--watch', action='store_true',
                           help='Watch markdown file for changes and auto-rebuild')
    run_parser.add_argument('--watch-interval', type=float, default=1.0,
                           help='Watch interval in seconds (default: 1.0)')
    run_parser.add_argument('-v', '--verbose', action='store_true',
                           help='Enable verbose output for debugging')
    
    # === THEMES COMMAND ===
    themes_parser = subparsers.add_parser('themes', help='Manage syntax highlighting themes')
    themes_subparsers = themes_parser.add_subparsers(dest='theme_action', help='Theme actions')
    
    # List themes
    list_themes_parser = themes_subparsers.add_parser('list', help='List all available themes')
    list_themes_parser.add_argument('-v', '--verbose', action='store_true',
                                   help='Enable verbose output for debugging')
    
    # Set theme
    set_theme_parser = themes_subparsers.add_parser('set', help='Set active syntax highlighting theme')
    set_theme_parser.add_argument('theme_name', help='Theme name to set')
    set_theme_parser.add_argument('-s', '--stylesheet', default=None,
                                 help='CSS file to modify (default: articles_css.css in script directory)')
    set_theme_parser.add_argument('-v', '--verbose', action='store_true',
                                 help='Enable verbose output for debugging')
    
    # Generate theme CSS
    generate_theme_parser = themes_subparsers.add_parser('generate', help='Generate theme CSS')
    generate_theme_parser.add_argument('theme_name', help='Theme name to generate')
    generate_theme_parser.add_argument('-o', '--output', help='Output CSS file (prints to stdout if not specified)')
    generate_theme_parser.add_argument('-v', '--verbose', action='store_true',
                                      help='Enable verbose output for debugging')
    
    # Remove theme
    remove_theme_parser = themes_subparsers.add_parser('remove', help='Remove current theme from stylesheet')
    remove_theme_parser.add_argument('-s', '--stylesheet', default=None,
                                    help='CSS file to modify (default: articles_css.css in script directory)')
    remove_theme_parser.add_argument('-v', '--verbose', action='store_true',
                                    help='Enable verbose output for debugging')
    
    # === CONFIG COMMAND ===
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_subparsers = config_parser.add_subparsers(dest='config_action', help='Config actions')
    
    # Show config
    show_config_parser = config_subparsers.add_parser('show', help='Show current configuration')
    show_config_parser.add_argument('-v', '--verbose', action='store_true',
                                   help='Enable verbose output for debugging')
    
    # Setup
    setup_config_parser = config_subparsers.add_parser('setup', help='Run setup wizard')
    setup_config_parser.add_argument('-v', '--verbose', action='store_true',
                                    help='Enable verbose output for debugging')
    
    # === IMAGES COMMAND ===
    images_parser = subparsers.add_parser('images', help='Image management')
    images_subparsers = images_parser.add_subparsers(dest='images_action', help='Image actions')
    
    # List images
    list_images_parser = images_subparsers.add_parser('list', help='List all images in project')
    list_images_parser.add_argument('-p', '--path', default='',
                                   help='Relative path to search (default: current directory)')
    list_images_parser.add_argument('-v', '--verbose', action='store_true',
                                   help='Enable verbose output for debugging')
    
    # Clean image names
    clean_images_parser = images_subparsers.add_parser('clean', help='Clean up image file names')
    clean_images_parser.add_argument('-p', '--path', default='',
                                    help='Relative path to clean (default: current directory)')
    clean_images_parser.add_argument('-v', '--verbose', action='store_true',
                                    help='Enable verbose output for debugging')
    
    # Upload images
    upload_images_parser = images_subparsers.add_parser('upload', help='Upload images to bucket')
    upload_images_parser.add_argument('-v', '--verbose', action='store_true',
                                     help='Enable verbose output for debugging')
    
    # === BUILD COMMAND ===
    build_parser = subparsers.add_parser(
        'build',
        help='Build all markdown files in a directory (incremental)',
        description='''Build all markdown files in a directory to HTML.
        
Uses hash-based change detection to only rebuild modified files.
Hash tracker is stored as .not_an_ssg_hashes.json in the input directory.

Examples:
  not_an_ssg build ./articles -o ./public           # Build with defaults
  not_an_ssg build ./articles -o ./public --force   # Force rebuild all
  not_an_ssg build                                  # Use default directories
''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    build_parser.add_argument('input_dir', nargs='?', default='./articles',
                             help='Input directory containing markdown files (default: ./articles)')
    build_parser.add_argument('-o', '--output', default='./output',
                             help='Output directory for HTML files (default: ./output)')
    build_parser.add_argument('-f', '--force', action='store_true',
                             help='Force rebuild all files (ignore hash cache)')
    build_parser.add_argument('--hash-file',
                             help='Custom path for hash tracker JSON (default: input_dir/.not_an_ssg_hashes.json)')
    build_parser.add_argument('-c', '--css', help='Custom CSS file path')
    build_parser.add_argument('-r', '--root', default='https://mebin.in',
                             help='Root URL for the return home button (default: https://mebin.in)')
    build_parser.add_argument('-v', '--verbose', action='store_true',
                             help='Enable verbose output for debugging')
    
    args = parser.parse_args()
    
    # Handle no command
    if not args.command:
        parser.print_help()
        return
    
    # === COMMAND HANDLERS ===
    
    if args.command == 'render':
        handle_render_command(args)
    elif args.command == 'serve':
        handle_serve_command(args)
    elif args.command == 'run':
        handle_run_command(args)
    elif args.command == 'themes':
        handle_themes_command(args)
    elif args.command == 'config':
        handle_config_command(args)
    elif args.command == 'images':
        handle_images_command(args)
    elif args.command == 'build':
        handle_build_command(args)


def handle_render_command(args):
    try:
        # Import frontmatter module
        from .frontmatter import open_article
        
        with open(args.input, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Extract slug from frontmatter if output not explicitly specified
        output_file = args.output
        if args.output == 'generated.html':  # Default value, not user-specified
            article = open_article(args.input)
            output_file = f"{article.slug}.html"
            if args.verbose:
                print(f"Using slug from frontmatter: {article.slug}")
        
        css = None
        if args.css:
            try:
                with open(args.css, 'r', encoding='utf-8') as f:
                    css = f.read()
            except FileNotFoundError:
                print(f"Error: CSS file '{args.css}' not found")
                sys.exit(1)
        
        if args.verbose:
            print(f"Rendering {args.input} -> {output_file}")
            print(f"Root URL: {args.root}")
            if args.css:
                print(f"Using custom CSS: {args.css}")
            if args.no_images:
                print("Skipping image processing")
        
        html_output = render(markdown_content, args.root, css, args.input, args.verbose)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        print(f"Successfully rendered {args.input} to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error rendering file: {e}")
        sys.exit(1)



def handle_serve_command(args):
    if args.verbose:
        print(f"Starting server on port {args.port}")
        print(f"Serving file: {args.file}")
        print(f"Auto-open browser: {not args.no_browser}")
    
    serve(args.file, args.port, not args.no_browser)


def handle_run_command(args):
    import time
    import threading
    from pathlib import Path
    from .frontmatter import open_article
    
    # Determine output file based on slug if using default
    output_file = args.output
    if args.output == 'generated.html':  # Default value
        article = open_article(args.input)
        output_file = f"{article.slug}.html"
        if args.verbose:
            print(f"Using slug from frontmatter: {article.slug}")
    
    def render_file():
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            css = None
            if args.css:
                try:
                    with open(args.css, 'r', encoding='utf-8') as f:
                        css = f.read()
                except FileNotFoundError:
                    print(f"Warning: CSS file '{args.css}' not found, using default")
            
            if args.verbose:
                print(f"Rendering {args.input} -> {output_file}")
            
            html_output = render(markdown_content, args.root, css, args.input, args.verbose)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_output)
            
            print(f"Rendered {args.input} to {output_file}")
            return True
            
        except FileNotFoundError:
            print(f"Error: Input file '{args.input}' not found")
            return False
        except Exception as e:
            print(f"Error rendering file: {e}")
            return False
    
    def watch_file():
        if not args.watch:
            return
        
        input_path = Path(args.input)
        css_path = Path(args.css) if args.css else None
        
        if not input_path.exists():
            print(f"Warning: Cannot watch non-existent file {args.input}")
            return
        
        last_md_mtime = input_path.stat().st_mtime
        last_css_mtime = css_path.stat().st_mtime if css_path and css_path.exists() else 0
        
        print(f"Watching {args.input} for changes")
        if css_path:
            print(f"Also watching {args.css} for changes")
        
        while True:
            try:
                time.sleep(args.watch_interval)
                
                current_md_mtime = input_path.stat().st_mtime if input_path.exists() else 0
                current_css_mtime = css_path.stat().st_mtime if css_path and css_path.exists() else 0
                
                if (current_md_mtime > last_md_mtime or 
                    current_css_mtime > last_css_mtime):
                    
                    print(f"File changed, rebuilding")
                    if render_file():
                        last_md_mtime = current_md_mtime
                        last_css_mtime = current_css_mtime
                        print(f"Rebuild complete at {time.strftime('%H:%M:%S')}")
                    
            except KeyboardInterrupt:
                print("\n File watching stopped")
                break
            except Exception as e:
                print(f"Error during file watching: {e}")
                time.sleep(1) 
    
    if not render_file():
        print("Failed to render file. Exiting.")
        sys.exit(1)
    
    try:
        output_path = Path(output_file)
        if not output_path.exists() or output_path.stat().st_size == 0:
            print(f"Error: Output file {output_file} is empty or doesn't exist")
            sys.exit(1)
    except Exception as e:
        print(f"Error checking output file: {e}")
        sys.exit(1)
    
    if args.watch:
        watcher_thread = threading.Thread(target=watch_file, daemon=True)
        watcher_thread.start()
    
    server_file_path = f"/{output_file}" if not output_file.startswith('/') else output_file
    
    if args.verbose:
        print(f"Starting server on port {args.port}")
        print(f"Serving file: {server_file_path}")
        print(f"Auto-open browser: {not args.no_browser}")
        if args.watch:
            print("File watching enabled - press Ctrl+C to stop")
    
    try:
        serve(server_file_path, args.port, not args.no_browser)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)


def handle_themes_command(args):
    if not args.theme_action:
        print("Error: No theme action specified. Use 'list', 'set', 'generate', or 'remove'")
        sys.exit(1)
    
    if args.theme_action == 'list':
        themes = list_themes(verbose=args.verbose)
        print("Available syntax highlighting themes:")
        for i, theme in enumerate(themes, 1):
            print(f"  {i:2d}. {theme}")
        print(f"\nTotal: {len(themes)} themes available")
    
    elif args.theme_action == 'set':
        try:
            if args.verbose:
                print(f"Setting theme '{args.theme_name}' in {args.stylesheet}")
            set_theme(args.stylesheet, args.theme_name, verbose=args.verbose)
            print(f"Successfully set theme '{args.theme_name}'")
        except Exception as e:
            print(f"Error setting theme: {e}")
            sys.exit(1)
    
    elif args.theme_action == 'generate':
        try:
            if args.verbose:
                print(f"Generating CSS for theme '{args.theme_name}'")
            theme_css = generate_theme_css(args.theme_name, verbose=args.verbose)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(theme_css)
                print(f"Theme CSS saved to {args.output}")
            else:
                print(theme_css)
        except Exception as e:
            print(f"Error generating theme CSS: {e}")
            sys.exit(1)
    
    elif args.theme_action == 'remove':
        try:
            stylesheet_path = args.stylesheet
            if stylesheet_path is None:
                # Export default CSS first, then remove theme from it (creating a writable copy; refer to README: Breaking Changes[1])
                stylesheet_path = export_default_css()
                if args.verbose:
                    print(f"Created {stylesheet_path} from package defaults")
            if args.verbose:
                print(f"Removing theme from {stylesheet_path}")
            remove_theme(stylesheet_path, verbose=args.verbose)
            print(f"Successfully removed theme from {stylesheet_path}")
        except Exception as e:
            print(f"Error removing theme: {e}")
            sys.exit(1)


def handle_config_command(args):
    if not args.config_action:
        print("Error: No config action specified. Use 'show' or 'setup'")
        sys.exit(1)
    
    if args.config_action == 'show':
        print("=== Not An SSG Configuration ===")
        
        # Show .env config
        load_dotenv()
        print("\nStorage Configuration (.env):")
        bucket_name = os.getenv('STORAGE_BUCKET_NAME')
        endpoint_url = os.getenv('STORAGE_ENDPOINT_URL')
        if bucket_name:
            print(f"  Bucket Name: {bucket_name}")
            print(f"  Endpoint URL: {endpoint_url}")
            print(f"  Access Key ID: {'*' * 10}[HIDDEN]")
            print(f"  Secret Key: {'*' * 10}[HIDDEN]")
        else:
            print("  No storage bucket configured")
        
        # Show config.json
        print("\nGeneral Configuration (config.json):")
        try:
            config = load_config()
            if 'image_dimensions' in config:
                dims = config['image_dimensions']
                print(f"  Default image width: {dims.get('width', 'Not set')}")
                print(f"  Default image height: {dims.get('height', 'Not set')}")
            else:
                print("  No image dimensions configured")
        except:
            print("  Configuration file not found")
    
    elif args.config_action == 'setup':
        print("Running setup wizard...")
        from .setup import setup_cli
        setup_cli()


def handle_images_command(args):
    if not args.images_action:
        print("Error: No images action specified. Use 'list', 'clean', or 'upload'")
        sys.exit(1)
    
    if args.images_action == 'list':
        images = get_images_all(args.path)
        if images:
            print(f"Images found in '{args.path or 'current directory'}':")
            for i, img in enumerate(images, 1):
                print(f"  {i:2d}. {img}")
            print(f"\nTotal: {len(images)} images")
        else:
            print(f"No images found in '{args.path or 'current directory'}'")
    
    elif args.images_action == 'clean':
        if args.verbose:
            print(f"Cleaning image names in '{args.path or 'current directory'}'")
        image_name_cleanup(args.path)
        print("Image name cleanup completed")
    
    elif args.images_action == 'upload':
        if SCRIPT_DIR not in sys.path:
            sys.path.insert(0, SCRIPT_DIR)
        images = images_to_upload('')
        if images:
            if args.verbose:
                print(f"Uploading {len(images)} new images to bucket...")
            for img in images:
                if args.verbose:
                    print(f"  Uploading: {img}")
                upload(img, args.verbose)
            print("All new images uploaded successfully")
        else:
            print("No new images to upload - all images already in bucket")


def handle_build_command(args):
    """Handle the build command for batch building directories."""
    from .build import build_directory
    
    # Load custom CSS if provided
    css = None
    if args.css:
        try:
            with open(args.css, 'r', encoding='utf-8') as f:
                css = f.read()
        except FileNotFoundError:
            print(f"Error: CSS file '{args.css}' not found")
            sys.exit(1)
    
    if args.verbose:
        print(f"Building directory: {args.input_dir}")
        print(f"Output directory: {args.output}")
        if args.force:
            print("Force rebuild enabled - rebuilding all files")
        if args.hash_file:
            print(f"Using custom hash file: {args.hash_file}")
    
    try:
        result = build_directory(
            input_dir=args.input_dir,
            output_dir=args.output,
            tracker_path=args.hash_file,
            force_rebuild=args.force,
            root_location=args.root,
            css=css,
            verbose=args.verbose
        )
        
        # Print summary
        print(f"\n=== Build Complete ===")
        print(f"Built: {len(result['built'])} file(s)")
        print(f"Skipped (unchanged): {len(result['skipped'])} file(s)")
        
        if result['errors']:
            print(f"Errors: {len(result['errors'])} file(s)")
            for err in result['errors']:
                print(f"  - {err['file']}: {err['error']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error during build: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()

