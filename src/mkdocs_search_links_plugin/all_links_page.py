import os
from html import escape
from urllib.parse import quote

# pip
from mkdocs.config.defaults import MkDocsConfig
# local
from .page_processor import LinkData
from . import ListingsConfig


def update_all_links_page(link_data_list: list[LinkData], plugin_config: ListingsConfig, config: MkDocsConfig) -> None:
    # We write the data in post-build -> listings should not be re-indexed and all pages were processed
    if plugin_config.listings_file:
        path = os.path.join(config.site_dir, plugin_config.listings_file)
        path = markdown_path_to_html_path(config, path)

        with open(path, "r") as f:
            html = f.read()

        listings_html_content = get_listings_html(link_data_list)
        html = html.replace(plugin_config.placeholder, listings_html_content)

        with open(path, "w") as f:
            f.write(html)


def get_listings_html(link_data_list: list[LinkData]) -> str:
    html = "<ul>"
    for link in link_data_list:
        text = link.text or link.href
        html += f'<li><a href="{quote_url_without_breaking_it(link.href)}">{escape(text)}</a>'
    html += "</ul>"

    return html


def quote_url_without_breaking_it(url):
    url = quote(url)
    # Links like https%3A//example.com are interpreted as relative links, so we need to unescape it here
    url = url.replace("%3A", ":").replace("%3a", ":")
    return url

def markdown_path_to_html_path(config: MkDocsConfig, markdown_path: str) -> str:
    if markdown_path.endswith(".md"):
        path_without_extension = markdown_path[:-3]
        if config.use_directory_urls:
            file_name = os.path.basename(markdown_path)
            if file_name == "index.md":
                return f"{path_without_extension}.html"
            else:
                return os.path.join(path_without_extension, "index.html")
        else:
            return f"{path_without_extension}.html"
    else:
        return markdown_path

