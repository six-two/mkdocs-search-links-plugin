import json
import os
# pip
from mkdocs.config.defaults import MkDocsConfig
# local
from . import SCRIPT_DIR, logger
from .page_processor import LinkData


def get_javascript_file_source_code(link_data_list: list[LinkData], plugin_config, offline: bool, script_or_page_path: str, config: MkDocsConfig) -> str:
    src_path = os.path.join(SCRIPT_DIR, "listing-search.js")
    with open(src_path, "r") as f:
        js = f.read()

    js = js.replace("DEFAULT_SEARCH_MODE=null;", f'DEFAULT_SEARCH_MODE="{plugin_config.default_search_mode}";')
    if plugin_config.default_css:
        with open(os.path.join(SCRIPT_DIR, "default.css")) as f:
            css = f.read()
        js = js.replace("STYLE=``;", f"STYLE=`{css}`;")

    # We traverse from the JSON file up to the root directory
    path_to_root = "../" * script_or_page_path.count("/")
    if config.use_directory_urls:
        path_to_root += "../"
    if offline:
        json_data = get_json_data(link_data_list, path_to_root)
        js = js.replace("OFFLINE_JSON_DATA=null;", f"OFFLINE_JSON_DATA={json.dumps(json_data)};")
    else:
        write_json_file(link_data_list, plugin_config, config, path_to_root)

    return js


def write_javascript_file(link_data_list: list[LinkData], plugin_config, config: MkDocsConfig) -> None:
    dst_path = os.path.join(config.site_dir, plugin_config.javascript_search_file)
    dst_path_parent = os.path.dirname(dst_path)
    if not os.path.exists(dst_path_parent):
        os.makedirs(dst_path_parent)

    js = get_javascript_file_source_code(link_data_list, plugin_config, plugin_config.offline, plugin_config.javascript_search_file, config)

    with open(dst_path, "w") as f:
        f.write(js)


def write_json_file(link_data_list: list[LinkData], plugin_config, config: MkDocsConfig, url_prefix: str) -> None:
    # We use a relative path to the script file (script file + ".json" extension)
    dst_path = os.path.join(config.site_dir, plugin_config.javascript_search_file) + ".json"
    json_data = get_json_data(link_data_list, url_prefix)
    with open(dst_path, "w") as f:
        json.dump(json_data, f, indent=2)


def get_json_data(link_data_list: list[LinkData], url_prefix: str) -> list[dict]:
    json_data = []
    for link in link_data_list:
        json_data.append({
            "text": link.text,
            "href": link.href,
        })
    return json_data
