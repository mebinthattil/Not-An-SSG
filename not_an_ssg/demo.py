#!/usr/bin/env python3
"""
Not-An-SSG V2.0.0 Python SDK Demo

This script demonstrates the key features of the Not-An-SSG Python SDK.
It uses demo_comprehensive.md as the input file to showcase rendering capabilities.
"""

import os
from pathlib import Path

from not_an_ssg import (
    render,
    serve,
    export_default_css,
    set_theme,
    generate_theme_css,
    get_images_all,
    image_name_cleanup
)


def main():
    """Demonstrate Not-An-SSG V2.0.0 SDK features"""
    
    print("\n" + "="*60)
    print("Not-An-SSG V2.0.0 Python SDK Demo")
    print("="*60)
    
    # Get the markdown file path
    markdown_file = Path(__file__).parent / 'demo_comprehensive.md'
    
    # 1. Export and customize CSS
    print("\n1. Exporting default CSS...")
    css_path = export_default_css('demo_style.css')
    print(f"   Exported to: {css_path}")
    
    # 2. Apply a theme
    print("\n2. Applying 'monokai' theme...")
    set_theme(css_path, 'monokai')
    print(f"   Theme applied to {css_path}")
    
    # 3. Read markdown content
    print("\n3. Reading markdown file...")
    with open(markdown_file, 'r') as f:
        markdown_content = f.read()
    print(f"   Read {len(markdown_content)} characters from {markdown_file.name}")
    
    # 4. Render to HTML
    print("\n4. Rendering to HTML...")
    html_output = render(
        markdown_content,
        root_location="https://myblog.com",
        css=css_path,
        input_file_path=str(markdown_file),
        verbose=False
    )
    print(f"   Generated {len(html_output)} characters of HTML")
    
    # 5. Save output
    print("\n5. Saving output...")
    output_file = 'demo_output.html'
    with open(output_file, 'w') as f:
        f.write(html_output)
    print(f"   Saved to: {output_file}")
    
    # 6. Show available themes
    print("\n6. Other available features:")
    print("   • Generate theme CSS: generate_theme_css('github-dark')")
    print("   • Find images: get_images_all('./path')")
    print("   • Clean filenames: image_name_cleanup('./path')")
    print("   • Start server: serve('/output.html', port=8080)")
    
    # Success message
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60)
    print(f"\nOpen {output_file} in your browser to see the result!")
    print("\nTo start a development server:")
    print(f"  python -c \"from not_an_ssg import serve; serve('/{output_file}', port=8080)\"")
    
    # Cleanup option
    print("\n" + "="*60)
    cleanup = input("Clean up generated files? (y/n): ").strip().lower()
    if cleanup == 'y':
        for file in [css_path, output_file]:
            if os.path.exists(file):
                os.remove(file)
                print(f"Removed: {file}")
        print("\nCleanup complete!")
    else:
        print("\nFiles preserved for inspection")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
