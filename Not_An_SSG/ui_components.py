def return_home_btn(home_page_link):
    return f"""
<center>
   <a href={home_page_link} style="text-decoration: none; color: black;">
      <button class="button">
         <div class="button-box">
            <span class="button-elem">
               <svg viewBox="0 0 46 40" xmlns="http://www.w3.org/2000/svg">
                  <path
                     d="M46 20.038c0-.7-.3-1.5-.8-2.1l-16-17c-1.1-1-3.2-1.4-4.4-.3-1.2 1.1-1.2 3.3 0 4.4l11.3 11.9H3c-1.7 0-3 1.3-3 3s1.3 3 3 3h33.1l-11.3 11.9c-1 1-1.2 3.3 0 4.4 1.2 1.1 3.3.8 4.4-.3l16-17c.5-.5.8-1.1.8-1.9z"
                     ></path>
               </svg>
            </span>
            <span class="button-elem">
               <svg viewBox="0 0 46 40">
                  <path
                     d="M46 20.038c0-.7-.3-1.5-.8-2.1l-16-17c-1.1-1-3.2-1.4-4.4-.3-1.2 1.1-1.2 3.3 0 4.4l11.3 11.9H3c-1.7 0-3 1.3-3 3s1.3 3 3 3h33.1l-11.3 11.9c-1 1-1.2 3.3 0 4.4 1.2 1.1 3.3.8 4.4-.3l16-17c.5-.5.8-1.1.8-1.9z"
                     ></path>
               </svg>
            </span>
         </div>
      </button>
   </a>
</center>
"""

def html_header_with_stylesheet(css):
    return f"""
<!DOCTYPE html>
<html lang="en">
   <head>
      <meta charset="utf-8">
      <style type="text/css">
         {css}  
      </style>
   </head>
   <body>
"""

def html_footer():
    return """
   </body>
</html>
"""

def not_an_ssg_footer():
    return """
<br><br><br>
<center>
   <p><i> Powered <a href="https://github.com/mebinthattil/Not-An-SSG">Not An SSG </a></i>😎</p>
</center>
<br>
"""
    
