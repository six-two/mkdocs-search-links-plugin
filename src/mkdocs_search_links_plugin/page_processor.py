from typing import NamedTuple
from mkdocs.structure.pages import Page
# local
from . import logger, ListingsConfig
from .html_parser import LinkData, parse_links_from_html

# class PageData(NamedTuple):
#     page_name: str
#     page_url: str
#     links: list[LinkData]


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
            seen[key] = link  # store original capitalization
        else:
            stored = seen[key].href.lower()
            new = link.href.lower()
            if stored.startswith("http://") and new.startswith("https://"):
                # Prefer HTTPS links over HTTP
                seen[key] = link
    return list(seen.values())


def normalize_url(url: str) -> str:
    # Ignore case when sorting
    url = url.lower()

    # Pretend all links are using HTTPS for sake of sorting
    if url.startswith("http://"):
        url = "https://" + url[7:]

    return url


def get_page_url(page: Page) -> str:
    page_url = page.url
    # This SHOULD fix the duplicate slash display bug (like '//readthedocs/')
    for _ in range(3):
        page_url = page_url.replace("//", "/")

    # Remove leading slash
    if page_url.startswith("/"):
        page_url = page_url[1:] or "index.html"

    if page_url.startswith("http://") or page_url.startswith("https://"):
        logger.warning(f"page_url is expected to be just a path, but it is a full URL: '{page_url}'")
        # No clue if it can happen. If it can, I should parse the path from the URL (and maybe remove the base URL).
    
    return page_url
