##### This code is heavily based on my mkdocs-backlinks-section-plugin #####
from typing import NamedTuple, Optional
from html.parser import HTMLParser
import re
from urllib.parse import unquote
from html import unescape

# local
from . import logger

# Regular expression for anchor tags (excludes autoref tags)
LINK_START_TAG_REGEX = re.compile(r"<a(?:\s[^>]*)?>", re.MULTILINE)

class LinkData(NamedTuple):
    text: str
    href: str


class ListingData(NamedTuple):
    text: str
    html: str
    language: str # empty string if not set


def parse_links_from_html(html: str, page_name: str) -> list[LinkData]:
    results = []
    for link_start_tag in LINK_START_TAG_REGEX.findall(html):
        link_data = parse_data_from_anchor_tag(link_start_tag, page_name)
        if link_data and is_external_link(link_data.href, page_name):
            results.append(link_data)

    return results

def is_external_link(url: str, page_name: str) -> bool:
    url = url.lower()
    if url.startswith("http://") or url.startswith("https://"):
        # Explicit link, likely to to self. @TODO: but we could check?
        return True
    elif url.startswith("/") or url.startswith(".") or url.startswith("#"):
        # Relative link
        return False
    else:
        first_path_element = url.split("/")[0]
        if ":" not in first_path_element:
            # Does not have a protocol, thus it is a relative link like "some-page.html"
            return False

        proto = url.split(":")[0]
        if proto in ["tel", "smsto", "mailto", "javascript"]:
            # Common protocol handlers
            return False
        
        # If I am not sure what is going on, print a warning so I can investigate and properly categorize them later
        # For now just ignore them
        logger.info(f"On page '{page_name}' could not determine if URL is external: {url}")
        return False

# This should handle all edge cases properly, since it is a full HTML parser. But it luckily needs no external dependencies
class AnchorHrefExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = ""
        self.id = ""
        self.text = ""
        self.in_a_tag = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.in_a_tag = True
            for attr_name, attr_value in attrs:
                if attr_name == "href":
                    self.href = attr_value
                if attr_name == "id":
                    self.id = attr_value
    
    def handle_data(self, data):
        if self.in_a_tag:
            self.text += data.strip()

    def handle_endtag(self, tag):
        if tag == "a":
            self.in_a_tag = False


def parse_data_from_anchor_tag(anchor_tag: str, page_name: str) -> Optional[LinkData]:
    parser = AnchorHrefExtractor()
    parser.feed(anchor_tag)
    if parser.href:
        return LinkData(text=unescape(parser.text), href=unquote(parser.href))
    elif parser.id and parser.id.startswith("__codelineno-"):
        # These are created when you enable line numbers in listings (linenums="1"). We can silently ignore them
        return None
    else:
        logger.warning(f"On page '{page_name}' an anchor tag has no href: {anchor_tag}")
        return None

