import markdown

#reading default css
with open('./articles_css.css', 'r') as file:
    defaultcss = file.read()

def gen_static_page(markdown_content,css = defaultcss):
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
    output_html += markdown.markdown(markdown_content, extensions=['fenced_code'])
    output_html += """

    <br><br><br>
    <center> <p><i> Powered <a href="https://github.com/mebinthattil/Not-An-SSG">Not An SSG </a></i>😎</p> </center> 
                        </body>
                        </html>
                        """
    return output_html
    