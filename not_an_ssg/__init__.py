"""
Not An SSG - A minimal static site generator for technical blogs.

This package provides:
- render(): Convert Markdown to styled HTML
- serve(): Start a development server
- cli_main(): CLI interface (also available as 'not_an_ssg' command)
- Theme management functions
- Image upload to S3/R2 compatible storage
- Batch building with hash-based caching

Example usage:
    from not_an_ssg import render, serve
    
    # Single file rendering
    html = render(markdown_content)
    serve('/output.html')
    
    # Build single file
    from not_an_ssg import build
    result = build('./article.md', './output')
    
    # Batch build directory
    from not_an_ssg import build_directory
    result = build_directory('./articles', './output')
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
from . import frontmatter
from . import build as build_module
from .build import (
    build,
    build_directory,
    get_files_to_rebuild,
    get_markdown_files,
    get_file_hash,
    load_hash_tracker,
    save_hash_tracker,
)

__version__ = "2.2.0"
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
    "frontmatter",
    "build_module",
    # Build functions
    "build",
    "build_directory",
    "get_files_to_rebuild",
    "get_markdown_files",
    "get_file_hash",
    "load_hash_tracker",
    "save_hash_tracker",
]