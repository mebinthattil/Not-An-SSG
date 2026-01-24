"""
Batch building module

Provides incremental building with hash-based change detection:
- Only rebuilds files that have changed
- Stores hashes in .not_an_ssg_hashes.json in the input directory
- Supports force rebuild to ignore hashes
"""

import os
import json
import hashlib
from typing import Optional

from .not_an_ssg import render
from .frontmatter import open_article


HASH_TRACKER_FILENAME = ".not_an_ssg_hashes.json"


def get_file_hash(filepath: str) -> Optional[str]:
    """
    Compute SHA-256 hash of a file.
    """
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(4096):  # Read file in chunks
                hasher.update(chunk)
    except FileNotFoundError:
        return None
    return hasher.hexdigest()


def load_hash_tracker(tracker_path: str) -> dict:
    if not os.path.exists(tracker_path):
        return {}
    try:
        with open(tracker_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_hash_tracker(tracker_path: str, hashes: dict) -> None:
    os.makedirs(os.path.dirname(tracker_path) or ".", exist_ok=True)
    with open(tracker_path, "w") as f:
        json.dump(hashes, f, indent=2)


def detect_file_changes(filepath: str, hashes: dict) -> bool:
    current_hash = get_file_hash(filepath)
    if current_hash is None:
        return False  # File doesn't exist
    
    # Use filename as key
    key = os.path.basename(filepath)
    stored_hash = hashes.get(key)
    
    return current_hash != stored_hash


def update_hash(filepath: str, hashes: dict) -> dict:

    current_hash = get_file_hash(filepath)
    if current_hash:
        key = os.path.basename(filepath)
        hashes[key] = current_hash
    return hashes


def get_markdown_files(input_dir: str, extensions: list = ['.md']) -> list:
    """
    Get all markdown files from a directory.
    
    Args:
        input_dir: Directory to search
        extensions: List of file extensions to include (default: ['.md']) This is so that any other file types can be included later.
        
    Returns:
        List of *absolute file paths*, sorted by modification time (newest first)
    """
    if not os.path.exists(input_dir):
        return []
    
    files = []
    try:
        with os.scandir(input_dir) as entries:
            for entry in entries:
                if entry.is_file():
                    _, ext = os.path.splitext(entry.name)
                    if ext.lower() in extensions:
                        files.append(entry)
        
        # Sort by modification time, newest first
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return [os.path.abspath(f.path) for f in files]
    except Exception as e:
        print(f"Error scanning directory {input_dir}: {e}")
        return []


def get_files_to_rebuild(input_dir: str, tracker_path: str = None, force: bool = False) -> list:

    if tracker_path is None:
        tracker_path = os.path.join(input_dir, HASH_TRACKER_FILENAME)
    
    all_files = get_markdown_files(input_dir)
    
    if force: # Ignore cache, rebuild all.
        return all_files
    
    hashes = load_hash_tracker(tracker_path)
    return [f for f in all_files if detect_file_changes(f, hashes)]


def build(
    input_path: str,
    output_dir: str = "./output",
    root_location: str = "https://google.com",
    css: str = None,
    verbose: bool = False
) -> dict:
    """
    Build a single file        
    Returns:
        Dictionary with build result: {"success": bool, "output_path": str, "error": str or None}
    """
    try:
        # Parse frontmatter for slug
        article = open_article(input_path)
        output_filename = f"{article.slug}.html"
        output_path = os.path.join(output_dir, output_filename)
        
        html = render(
            article.contents,
            root_location=root_location,
            css=css,
            input_file_path=input_path,
            verbose=verbose
        )
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        if verbose:
            print(f"Built: {input_path} -> {output_path}")
        
        return {"success": True, "output_path": output_path, "error": None}
        
    except Exception as e:
        error_msg = str(e)
        if verbose:
            print(f"Error building {input_path}: {error_msg}")
        return {"success": False, "output_path": None, "error": error_msg}


def build_directory(
    input_dir: str = "./articles",
    output_dir: str = "./output",
    tracker_path: str = None,
    force_rebuild: bool = False,
    root_location: str = "https://google.com",
    css: str = None,
    verbose: bool = False
) -> dict:
    """
    Build all *changed* markdown files in a directory.
    
    Uses hash-based change detection to only rebuild modified files.
    Hash tracker is stored as .not_an_ssg_hashes.json in the input directory.
    
    Args:
        input_dir: Directory containing markdown files (default: ./articles)
        output_dir: Directory to write HTML output (default: ./output)
        tracker_path: Custom path for hash tracker (default: input_dir/.not_an_ssg_hashes.json)
        force_rebuild: If True, rebuild all files ignoring hashes
        root_location: URL for the home button
        css: Optional custom CSS string
        verbose: Enable verbose output
        
    Returns:
        Dictionary with build results:
        {
            "built": [list of successfully built file paths],
            "skipped": [list of unchanged file paths],
            "errors": [{"file": path, "error": message}, ...]
        }
    """
    # Set default tracker path
    if tracker_path is None:
        tracker_path = os.path.join(input_dir, HASH_TRACKER_FILENAME)
    
    # Validate input directory
    if not os.path.exists(input_dir):
        return {"built": [], "skipped": [], "errors": [{"file": input_dir, "error": "Input directory does not exist"}]}
    
    hashes = load_hash_tracker(tracker_path)
    all_files = get_markdown_files(input_dir)
    
    if verbose:
        print(f"Found {len(all_files)} markdown file(s) in {input_dir}")
    
    # Determine which files need building
    if force_rebuild:
        files_to_build = all_files
        files_to_skip = []
        if verbose:
            print("Force rebuild enabled - building all files")
    else:
        files_to_build = [f for f in all_files if detect_file_changes(f, hashes)]
        files_to_skip = [f for f in all_files if f not in files_to_build]
    
    if verbose:
        print(f"Files to build: {len(files_to_build)}")
        print(f"Files to skip: {len(files_to_skip)}")
    
    built = []
    errors = []
    
    for filepath in files_to_build:
        result = build(filepath, output_dir, root_location=root_location, css=css, verbose=verbose)
        
        if result["success"]:
            built.append(filepath)
            update_hash(filepath, hashes)
        else:
            errors.append({"file": filepath, "error": result["error"]})
    
    if built:
        save_hash_tracker(tracker_path, hashes)
        if verbose:
            print(f"Updated hash tracker: {tracker_path}")

    if verbose:
        print(f"\n=== Build Summary ===")
        print(f"Built: {len(built)} file(s)")
        print(f"Skipped: {len(files_to_skip)} file(s)")
        if errors:
            print(f"Errors: {len(errors)} file(s)")
    
    return {
        "built": built,
        "skipped": files_to_skip,
        "errors": errors
    }


if __name__ == "__main__":
    build_directory(verbose=True)