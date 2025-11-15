from typing import NamedTuple
from mkdocs.structure.pages import Page
# local
from . import logger, ListingsConfig
from .html_parser import LinkData, parse_links_from_html


class PageProcessor:
    def __init__(self, plugin_config: ListingsConfig):
        self.links: list[LinkData] = []
        self.plugin_config = plugin_config

    def process_page(self, html: str, page: Page):
        if links := parse_links_from_html(html, page.url):
            self.links += links 

    def processed_all_pages(self) -> None:
        self.links = remove_duplicates_ignore_case_and_proto(self.links)
        self.links = sorted(self.links, key=lambda x: normalize_url(x.href))

    def clear(self):
        self.links = []

def remove_duplicates_ignore_case_and_proto(links):
    seen = {}
    for link in links:
        key = normalize_url(link.href)
        if key not in seen:
            seen[key] = link  # store value
        else:
            stored = seen[key].href.lower()
            new = link.href.lower()
            # Prefer HTTPS links over HTTP
            if stored.startswith("http://") and new.startswith("https://"):
                seen[key] = link
    # Return original values
    return list(seen.values())


def normalize_url(url: str) -> str:
    # Ignore case when sorting
    url = url.lower()

    # Pretend all links are using HTTPS for sake of sorting
    if url.startswith("http://"):
        url = "https://" + url[7:]

    return url

