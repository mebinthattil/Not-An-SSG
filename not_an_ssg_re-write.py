import markdown
import os
import ui_components
from pygments.formatters import HtmlFormatter



def render(markdown_content,css = None):
    if css is None:
        css = read_stylsheet()
    output_html = ui_components.html_header_with_stylesheet(css)

    output_html += markdown.markdown(markdown_content, extensions=['fenced_code', 'codehilite', 'nl2br'])

    output_html += ui_components.not_an_ssg_footer()
    output_html += ui_components.return_home_btn("https://mebin.in")

    return output_html


# === CSS RELATED FUNCTIONS ===
def generate_theme_css(theme_name='monokai'):
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

def set_theme(style_sheet_path, theme_name):
    css = remove_theme(style_sheet_path)
    css_generated = generate_theme_css(theme_name).splitlines(keepends=True)
    print(css_generated)
    write_stylsheet(css + css_generated, style_sheet_path, write_mode="writelines")
    
def remove_theme(sytle_sheet_path) -> str: # Removes the theme and also returns the remaining css contents
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


f = open("syntax_test.md","r")
markdown_content = f.read()
f.close()

f = open("generated10.html","w")
f.write(render(markdown_content))
f.close()


#print(generate_theme_css())
set_theme("./articles_css.css", "dracula")
#remove_theme("./articles_css.css")
