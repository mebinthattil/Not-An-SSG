import yaml
from datetime import datetime
def open_article(article_path):
    """
    Open articles using this function. It returns an article object.
    The frontmatter can have the following keys:
    - title
    - author
    - description
    - publish_date
    - tags
    - slug
    - last_modified
    - layout
    - published
    """
    class article:
        def __init__(self, article_path):
            self.article_path = article_path
            self.file_base_name = article_path.split("/")[-1].split(".")[0]
            self.raw_contents = open(article_path, "r").read().strip()

            if self.raw_contents.startswith("---"):
                parts = self.raw_contents.split("---")
                # parts[0] is empty, parts[1] is frontmatter, parts[2] is content
                frontmatter_raw = parts[1]
                self.contents = parts[2].strip() if len(parts) > 2 else ""
                self.frontmatter = yaml.safe_load(frontmatter_raw)
            else: # No frontmatter found
                self.contents = self.raw_contents
                self.frontmatter = {}
        
            self.title = self.frontmatter.get("title", self.file_base_name)
            self.author = self.frontmatter.get("author")
            self.description = self.frontmatter.get("description")
            self.publish_date = self.frontmatter.get("publish_date", datetime.now().strftime("%Y-%m-%d"))
            self.tags = self.frontmatter.get("tags")
            self.slug = self.frontmatter.get("slug", self.file_base_name.replace(" ", "-"))
            self.last_modified = self.frontmatter.get("last_modified")
            self.layout = self.frontmatter.get("layout")
            self.published = self.frontmatter.get("published")

    return article(article_path)
            

# testing
if __name__ == "__main__":
    import os
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    article = open_article(os.path.join(script_dir, "demo_comprehensive.md"))
    print(article.title)
    print(article.author)
    print(article.description)
    print(article.publish_date)
    print(article.tags)
    print(article.slug)
    print(article.last_modified)
    print(article.layout)
    print(article.published)
