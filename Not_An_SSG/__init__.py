import os, sys

files_to_copy = [
    'config.json',
    'articles_css.css',
    'setup.py',
    'ui_components.py',
    'r2_bucket.py',
    'not_an_ssg.py'
]

def files_exist():
    for file in files_to_copy:
        if not os.path.exists(file):
            return False
    return True

def _setup_user_files():
    """Copy necessary files from package to user's working directory if they don't exist"""
    try:
        try:
            from importlib.resources import files
        except ImportError:
                return #TODO
        
        package_files = files('Not_An_SSG')
        
        for filename in files_to_copy:
            if not os.path.exists(filename):
                try:
                    source_file = package_files / filename
                    if source_file.exists():
                        with source_file.open('rb') as src:
                            with open(filename, 'wb') as dst:
                                dst.write(src.read())
                except Exception:
                    pass # TODO
        
        if not os.path.exists('templates'):
            try:
                templates_dir = package_files / 'templates'
                if templates_dir.exists():
                    os.makedirs('templates/assets/img', exist_ok=True)
                    
                    for item in templates_dir.rglob('*'):
                        if item.is_file():
                            relative_path = item.relative_to(templates_dir)
                            
                            # skip imgs in assets/img
                            if 'assets/img' in str(relative_path):
                                continue
                                
                            dest_path = os.path.join('templates', str(relative_path))
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                            with item.open('rb') as src:
                                with open(dest_path, 'wb') as dst:
                                    dst.write(src.read())
            except Exception:
                pass # TODO
                
    except Exception:
        pass # TODO


if not files_exist():
    consent = input("Not An SSG works best when all the files are present in the directory you want to host your webserver in. Do you consent to cloning source code to your PWD? [y/n]: ")
    if consent.lower() == "y":
        _setup_user_files()
    else:
        print("Exiting")
        sys.exit(1)


from .not_an_ssg import render, serve, cli_main, generate_theme_css, read_stylsheet, write_stylsheet, set_theme, remove_theme, list_themes, images_to_upload, image_name_cleanup, load_config, verbose_decorator
from .r2_bucket import upload, get_bucket_contents