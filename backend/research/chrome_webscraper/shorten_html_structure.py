# FULL CONTEXT ON WRITING THIS:
# https://chat.openai.com/share/5a47992e-b6c7-4927-93f1-07ffd9e212fb
"""
Script useful for chat gpt prompts like:
* Given this large html boilerplate
* Write a python script which outputs the actual (profile) data in a structured manner.
"""
import os

from bs4 import BeautifulSoup


def shorten_class_names(_soup):
    for tag in _soup.find_all(True):
        if "class" in tag.attrs:
            new_classes = [cls.split("-")[0] for cls in tag["class"]]
            tag["class"] = new_classes
        for attr in list(tag.attrs.keys()):
            if attr not in ["class", "id"]:
                del tag[attr]
    return _soup


input_filepath = "output.html"
with open(input_filepath, "r") as f:
    html = f.read()

# NOTE: This won't render that nicely
base, ext = os.path.splitext(input_filepath)
output_filepath = f"{base}-short{ext}"
with open(output_filepath, "w") as f:
    soup = BeautifulSoup(html, "html.parser")
    new_soup = shorten_class_names(soup)
    new_content = new_soup.prettify()
    print(f"shortened {output_filepath} from {len(html)} to {len(new_content)}")
    f.write(new_content)
