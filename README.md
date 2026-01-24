# Not-An-SSG

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-Not--An--SSG-black?logo=github)](https://github.com/mebinthattil/Not-An-SSG)

A minimal, fast static site generator focused on technical blogs and documentation. Not-An-SSG converts Markdown to beautifully styled HTML with excellent syntax highlighting, automatic image optimization, and cloud storage integration.

This evolved out of a basic SSG I wrote to power my own [website](https://mebin.in). It was not initially built to be distributed as a Python package. So this is a re-write of the original SSG with more features and a more robust CLI interface. This is my first Python package, so distributions are not guaranteed to work. Use at your own risk.

## Features

- **Fast & Lightweight**: Decently performant, yet to benchmark. But don't use this if you want the fastest SSG
- **Beautiful Themes**: Modern dark theme optimized for technical content, try `not_an_ssg themes list`
- **Rich Markdown Support**: Tables, code blocks, math expressions and more
- **Frontmatter Support**: YAML frontmatter for metadata
- **Batch Building**: Builds with hash-based caching to prevent unnecessary rebuilds (v2.2.0+)
- **Image Handling**: Smart optimizations, CDN integration and cloud uploads
- **CLI + Imports**: CLI tools, Python API, and extensive customization options
- **Responsive Design**: Works on mobile devices (yet to extensively test, but typography should be better)
- **Server mode**: Run HTML site in a server with file-watch and auto-rebuilds
- **Code Highlighting**: 100+ syntax highlighting themes powered by Pygments

## Quick Start

### Installation

```bash
pip install not_an_ssg
```

### Basic Usage

1. **Create your first blog post:**
```bash
echo "# Hello World\nThis is my first blog post!" > my-post.md
```

2. **Set up the project (REQUIRED):**
```bash
not_an_ssg config setup
```
This step is essential - it creates the necessary configuration files and directory structure that Not-An-SSG needs to function properly.

3. **Render and serve:**
```bash
not_an_ssg run my-post.md
```
> Your blog will be available at `http://localhost:6969` with automatic browser opening. 
> Port 6969 and auto browswer open is default behavior, both can be changed with flags.

4. **Learn more:**
```bash
not_an_ssg -h
```



## CLI Reference

### Core Commands

#### `render` - Convert Markdown to HTML
```bash
not_an_ssg render input.md [options]
```

**Options:**
- `-o, --output FILE`: Output HTML file (default: uses slug from frontmatter or auto-generates from filename)
- `-c, --css FILE`: Custom CSS file path
- `-r, --root URL`: Root URL for home button (default: https://google.com)
- `--no-images`: Skip image processing and uploading
- `-v, --verbose`: Enable verbose output

**Examples:**
```bash
# Basic rendering
not_an_ssg render blog-post.md
# Output: blog-post.html (or custom slug if specified in frontmatter)

# Custom output file and CSS
not_an_ssg render blog-post.md -o index.html -c custom.css

# Skip image processing
not_an_ssg render blog-post.md --no-images

# Verbose output for debugging
not_an_ssg render blog-post.md -v
```

> **Note**: By default, the output filename is determined by the `slug` field in your markdown's frontmatter. If no slug is specified, it's auto-generated from the filename.

#### `serve` - Start Development Server
```bash
not_an_ssg serve [options]
```

**Options:**
- `-p, --port PORT`: Server port (default: 6969)
- `-f, --file FILE`: HTML file to serve (default: /generated.html)
- `--no-browser`: Don't automatically open browser

**Examples:**
```bash
# Start server on default port
not_an_ssg serve

# Custom port and file
not_an_ssg serve -p 8080 -f /my-blog.html

# Server without opening browser
not_an_ssg serve --no-browser

# Verbose output for debugging
not_an_ssg serve -v
```

#### `run` - Render and Serve (You're prolly here for this)
```bash
not_an_ssg run input.md [options]
```

**Options:**
- All `render` options &
- All `serve` options &
- `--watch`: Watch for file changes and auto-rebuild
- `--watch-interval SECONDS`: Watch interval (default: 1.0)

**Examples:**
```bash
# Render and serve with live reload
not_an_ssg run blog-post.md --watch

# Custom port with file watching
not_an_ssg run blog-post.md -p 8080 --watch

# Verbose mode for debugging
not_an_ssg run blog-post.md -v --watch
```

#### `build` - Batch Build Directory (v2.2.0+)
```bash
not_an_ssg build [input_dir] [options]
```

Build all markdown files in a directory with incremental hash-based caching.

**Options:**
- `input_dir`: Input directory (default: ./articles)
- `-o, --output DIR`: Output directory (default: ./output)
- `-f, --force`: Force rebuild all files (ignore hash cache)
- `--hash-file FILE`: Custom path for hash tracker JSON
- `-c, --css FILE`: Custom CSS file path
- `-r, --root URL`: Root URL for home button
- `-v, --verbose`: Enable verbose output

**Examples:**
```bash
# Build with defaults (./articles -> ./output)
not_an_ssg build

# Custom directories
not_an_ssg build ./content -o ./public

# Force rebuild all files
not_an_ssg build ./articles -o ./output --force

# Verbose output
not_an_ssg build ./articles -o ./output -v
```

> **Note**: Hashes are stored in `.not_an_ssg_hashes.json` in the input directory. Only changed files are rebuilt on subsequent runs.

### Theme Management

#### `themes list` - List Available Themes
```bash
not_an_ssg themes list
```

#### `themes set` - Apply Syntax Highlighting Theme
```bash
not_an_ssg themes set THEME_NAME [options]
```

**Options:**
- `-s, --stylesheet FILE`: CSS file to modify

> By default sets theme (override theme part only) to the default `articles_css.css` file in the script directory.

**Examples:**
```bash
# Set monokai theme
not_an_ssg themes set monokai

# Set theme for specific stylesheet
not_an_ssg themes set dracula -s custom.css

# Verbose output for debugging
not_an_ssg themes set monokai -v
```

#### `themes generate` - Generate Theme CSS
```bash
not_an_ssg themes generate THEME_NAME [options]
```

**Options:**
- `-o, --output FILE`: Output CSS file (prints to stdout if not specified)

**Examples:**
```bash
# Generate and print theme CSS
not_an_ssg themes generate github-dark

# Save theme to file
not_an_ssg themes generate monokai -o monokai-theme.css

# Verbose output for debugging
not_an_ssg themes generate monokai -v
```

#### `themes remove` - Remove Current Theme
```bash
not_an_ssg themes remove [options]
```

### Configuration Management

#### `config show` - Display Current Configuration
```bash
not_an_ssg config show

# Verbose output for debugging
not_an_ssg config show
```

#### `config setup` - Run Setup Wizard
```bash
not_an_ssg config setup

# Verbose output for debugging
not_an_ssg config setup
```

### Image Management

#### `images list` - List Project Images
```bash
not_an_ssg images list [options]

# List all images in project
not_an_ssg images list

# List images in specific path with verbose output
not_an_ssg images list -p ./v_secret_folder
```

**Options:**
- `-p, --path PATH`: Search path (default: current directory)
- `-v, --verbose`: Enable verbose output

#### `images clean` - Clean Image Filenames
```bash
not_an_ssg images clean [options]

# Clean image names in current directory
not_an_ssg images clean

# Clean specific path with verbose output
not_an_ssg images clean -p ./assets -v
```

**Options:**
- `-p, --path PATH`: Path to clean (default: current directory)
- `-v, --verbose`: Enable verbose output

#### `images upload` - Upload Images to Cloud Storage
```bash
# Upload all images to configured bucket
not_an_ssg images upload

# Upload with verbose output
not_an_ssg images upload -v
```

**Options:**
- `-v, --verbose`: Enable verbose output (highly reccomend using this)

### Common Options

- `-v, --verbose`: Enable verbose output (available on all commands)
- `-h, --help`: Show help message for any command

## Project Structure

```
your-blog/
├── templates/
│   └── assets/
│       └── img/          # Images (auto-uploaded to CDN during render, unless specified otherwise)
├── .env                  # Environment configuration (auto genned by config setup - this is for storage buckets)
├── config.json           # Project configuration (right now only for default image dimensions)
├── articles_css.css      # Main stylesheet (has all the styling and the theme - themes are swappable and auto-generated)
├── your-post.md          # Your markdown files (can be renamed)
└── generated.html        # Generated output (can be renamed)
```

## Configuration

**Important**: Before using Not-An-SSG, you must run the setup wizard. This setup is also directory dependent, so if you want to use Not-An-SSG in a different directory, you'll need to run the setup wizard again. It's not ideal, I know. Will fix this later.

```bash
not_an_ssg config setup
```

This interactive setup process will:
- Create the necessary configuration files (`config.json`, `.env`)
- Set up the required directory structure (`templates/assets/img/`)
- Configure cloud storage settings if desired
- Generate the base CSS file

### Environment Variables (.env)

The setup wizard will create and configure your `.env` file for cloud storage and CDN integration. You don't need to manually edit this file unless you want to change settings later.

Example configuration (automatically generated by setup):

```env
# Cloudflare R2 / AWS S3 Configuration
STORAGE_BUCKET_NAME=your-bucket-name
STORAGE_ACCESS_KEY_ID=your-access-key
STORAGE_SECRET_ACCESS_KEY=your-secret-key
STORAGE_ENDPOINT_URL=https://your-endpoint.com
STORAGE_REGION_NAME=auto
STORAGE_ACCOUNT_ID=your-account-id
CDN_URL=https://your-cdn.com
```
> Note: I use Cloudflare R2 for my bucket, but in theory any S3 compatible storage should work. I am however yet to test this out with S3.

### Project Configuration (config.json)

The setup wizard also creates this file with default settings:

```json
{
  "image_dimensions": {
    "width": 800,
    "height": 500
  }
}
```

You can modify these values manually if needed, or re-run `not_an_ssg config setup` to change them interactively.

## Python API

### Basic Usage

```python
from not_an_ssg import render, serve


# Read markdown content
with open('blog-post.md', 'r') as f:
    markdown_content = f.read()

# Render to HTML
html_output = render(
    markdown_content,
    root_location="https://yourblog.com",
    input_file_path="blog-post.md"
)

# Save output
with open('output.html', 'w') as f:
    f.write(html_output)

# Start development server
serve('/output.html', port=8080)
```

### Advanced Usage

```python
from not_an_ssg import (
    render, 
    generate_theme_css, 
    set_theme,
    get_images_all,
    image_name_cleanup,
    export_default_css
)

# Export default CSS to create a writable copy (V2.0.0+)
css_file = export_default_css('my_custom.css')
print(f"Exported CSS to: {css_file}")

# Custom CSS with theme
custom_css = generate_theme_css('github-dark')
set_theme(css_file, 'github-dark')  # Now modifies the exported file

# Render with custom options
html = render(
    markdown_content,
    root_location="https://yourblog.com",
    css=css_file,  # Use the exported CSS file path
    input_file_path="blog-post.md",
    verbose=True
)

# Image management
images = get_images_all('/path/to/project')
image_name_cleanup('/path/to/project')

```

### Working with Themes (V2.0.0+)

```python
from not_an_ssg import export_default_css, generate_theme_css, set_theme

# Step 1: Export the default CSS to a writable location
css_path = export_default_css('articles_css.css')

# Step 2: Apply a theme to the exported CSS
set_theme(css_path, 'monokai')

# Step 3: Use the themed CSS for rendering
from not_an_ssg import render

with open('blog.md', 'r') as f:
    content = f.read()

html = render(
    content,
    css=css_path,
    input_file_path='blog.md',
    root_location='https://myblog.com'
)

with open('output.html', 'w') as f:
    f.write(html)
```

### Batch Building (v2.2.0+)

```python
from not_an_ssg import build, build_directory

# Build a single file
result = build('./article.md', './output')
print(f"Built: {result['output_path']}")

# Build all files in a directory (incremental)
result = build_directory('./articles', './output')
print(f"Built: {len(result['built'])} files")
print(f"Skipped: {len(result['skipped'])} files")

# Force rebuild all files
result = build_directory('./articles', './output', force_rebuild=True)

# With custom options
result = build_directory(
    input_dir='./content',
    output_dir='./public',
    root_location='https://myblog.com',
    verbose=True
)
```


## Frontmatter Support

Not-An-SSG supports YAML frontmatter for metadata and controlling output behavior. Frontmatter is optional but provides powerful features like custom slugs and metadata.

### Supported Fields

```yaml
---
title: "Your Article Title"           # Article title (optional, defaults to filename)
slug: "custom-url-slug"               # Output filename slug (optional, auto-generated if not specified)
author: "Author Name"                 # Article author (optional)
description: "Article description"    # Meta description (optional)
publish_date: "24-01-2026"           # Publication date (optional, defaults to current date)
tags: ["tag1", "tag2"]               # Article tags (optional)
last_modified: "24-01-2026"          # Last modification date (optional)
layout: "post"                       # Layout type (optional)
published: true                      # Publication status (optional)
---
```

### Slug-Based Output

The `slug` field controls the output HTML filename:

```markdown
---
slug: my-awesome-post
---

# My Awesome Post
```

**Output:** `my-awesome-post.html`

If no slug is specified, it's auto-generated from the filename:
- `my article.md` → `my-article.html`
- `What's New?.md` → `What's-New?.html`

### Complete Example

```markdown
---
title: "Getting Started with Not-An-SSG"
slug: getting-started
author: "John Doe"
description: "A comprehensive guide to using Not-An-SSG for your blog"
publish_date: "24-01-2026"
tags: ["tutorial", "ssg", "markdown"]
published: true
---

# Heading 1

lmao lmao lmao
```

### Using Frontmatter Programmatically

```python
from not_an_ssg.frontmatter import open_article

# Parse markdown with frontmatter
article = open_article('blog-post.md')

# Access frontmatter fields
print(article.title)         # "Getting Started with Not-An-SSG"
print(article.slug)          # "getting-started"
print(article.author)        # "John Doe"
print(article.tags)          # ["tutorial", "ssg", "markdown"]
print(article.contents)      # Markdown content without frontmatter
```


## Markdown Features

### Code Blocks with Syntax Highlighting

````markdown
```python
def hello_world():
    print("Hello, World!")
```
````
> You can use almost any language - powered by [Pygments](https://pygments.org/)

### Tables

```markdown
| Feature | Status |
|---------|--------|
| Cool    | Yes    |
| Pretty  | Yes    |
| Simple  | Yes    |
| Paid    | No     |
```

### Images with Auto-Processing

```markdown
![Alt text](./templates/assets/img/my-image.jpg)

<!-- With custom dimensions -->
![Alt text](./templates/assets/img/my-image.jpg){width="400" height="300"}
```

### Math Expressions

```markdown
Inline math: $E = mc^2$

Block math:
$$
\frac{d}{dx} \int_a^x f(t)dt = f(x)
$$
```

## Advanced Features

### File Watching and Live Reload

```bash
# Automatically rebuild on file changes
not_an_ssg run blog.md --watch --watch-interval 0.5
```

### Custom CSS Integration

```bash
# Use your own stylesheet
not_an_ssg run blog.md -c custom.css
```

### Cloud Storage Integration

You are expected to place all you images under `templates/assets/img/`. Then, the following features become available:
1. Cleaned filename (removes whitespaces and weird characters)
2. Uploaded to your configured cloud storage
3. Replaced img src with CDN URLs in the final HTML

### Verbose Mode for Debugging

```bash
# See detailed processing information
not_an_ssg run blog.md -v
```

## Troubleshooting

### Common Issues

1. **Images not displaying**: Ensure images are in `templates/assets/img/` directory and you've run `not_an_ssg config setup`
2. **CDN not working**: Run `not_an_ssg config setup` to configure cloud storage settings
3. **Themes not applying**: Run `not_an_ssg themes set THEME_NAME`
4. **Port already in use**: Use `-p` to specify a different port. Only applicable while using `serve`
5. **Missing files error**: Always run `not_an_ssg config setup` before using other commands, although it should automatically prompt you if it does not find the required files.

### Getting Help

```bash
# General help
not_an_ssg -h

# Command-specific help
not_an_ssg render -h
not_an_ssg run -h
```

## Requirements

- Python 3.8+
- Dependencies: `markdown`, `pygments`, `boto3`, `python-dotenv`

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! This project was built for personal use but has evolved to make it public. You can find the repo [here](https://github.com/mebinthattil/Not-An-SSG).

## Changelog

### v2.2.0
- **New**: Batch building with `not_an_ssg build` CLI command
- **New**: `build()` SDK function for single file building
- **New**: `build_directory()` SDK function for batch building with hash caching
- **New**: Incremental builds - only changed files are rebuilt
- **New**: `--force` flag to rebuild all files ignoring cache
- **Breaking**: `build.py` module completely refactored (see Breaking Changes)

### v2.1.0
- **New**: YAML frontmatter support with metadata fields
- **New**: Slug-based output filenames from frontmatter
- **New**: Auto-generated slugs from filenames when not specified

### v2.0.0
- **Breaking**: Complete re-architecture for proper Python packaging
- No longer copies source files to user's directory
- Uses `importlib.resources` for package assets
- SDK imports work cleanly: `from not_an_ssg import render, serve`
- CLI command: `not_an_ssg`
- Lazy S3 client initialization (no credentials needed at import time)
- Added `export_default_css()` for theme customization

### v0.1.0
- Initial release
- Core markdown rendering
- CLI interface
- Theme support
- Cloud storage integration
- Live development server

## Breaking Changes (v2.0.0)

### `write_stylesheet(css_content, path_to_stylesheet, write_mode)`:
`path_to_stylesheet` can no longer be `None`. Package resources are read-only.

**Fix**: Use `export_default_css()` to create a writable copy first.

### Removed `files_to_copy`, `files_exist()`, `_setup_user_files()`
These internal functions are no longer needed. SDK imports work directly.

## Developer Guide

### Building and Testing Locally

```bash
# 1. Build the wheel
cd /path/to/Not-An-SSG
pip install build
python -m build

# 2. Create a fresh test environment
cd /tmp && mkdir ssg_test && cd ssg_test
python3 -m venv .venv && source .venv/bin/activate

# 3. Install from local wheel
pip install /path/to/Not-An-SSG/dist/not_an_ssg-2.0.0-py3-none-any.whl

# 4. Test SDK
python -c "from not_an_ssg import render, serve; print('OK')"

# 5. Test CLI
not_an_ssg themes list
echo "# Test" > test.md && not_an_ssg render test.md
```

## Breaking Changes (v2.2.0)

### `build` module refactored
The old `build.py` with hardcoded paths has been completely refactored:

| Old Function | New Function | Notes |
|--------------|--------------|-------|
| `build()` | `build()` | Now builds a single file, returns result dict |
| `markdowns_to_rebuild()` | `get_files_to_rebuild()` | Configurable paths |
| N/A | `build_directory()` | **New**: Batch build with hash caching |

**New usage:**
```python
# Single file
from not_an_ssg import build
result = build('./article.md', './output')

# Batch directory
from not_an_ssg import build_directory
result = build_directory('./articles', './output')
```
