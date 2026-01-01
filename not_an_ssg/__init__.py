"""
Not An SSG - A minimal static site generator for technical blogs.

This package provides:
- render(): Convert Markdown to styled HTML
- serve(): Start a development server
- cli_main(): CLI interface (also available as 'not_an_ssg' command)
- Theme management functions
- Image upload to S3/R2 compatible storage

Example usage:
    from not_an_ssg import render, serve
    
    html = render(markdown_content)
    serve('/output.html')
"""

from .not_an_ssg import (
    render,
    serve,
    cli_main,
    generate_theme_css,
    read_stylsheet,
    write_stylsheet,
    set_theme,
    remove_theme,
    list_themes,
    export_default_css,
    images_to_upload,
    image_name_cleanup,
    get_images_all,
    load_config,
    get_package_resource )
from .r2_bucket import upload, get_bucket_contents

__version__ = "2.0.0"
__all__ = [
    "render",
    "serve",
    "cli_main",
    "generate_theme_css",
    "read_stylsheet",
    "write_stylsheet",
    "set_theme",
    "remove_theme",
    "list_themes",
    "export_default_css",
    "images_to_upload",
    "image_name_cleanup",
    "get_images_all",
    "upload",
    "get_bucket_contents",
    "load_config",
    "get_package_resource",
]