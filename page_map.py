from .path_scanner import scanner
import json

class PageMap:
    def __init__(self, domain: str):
        self.domain = domain
        self.root = {domain: {}}

    def insert(self, path_parts: list):
        current = self.root[self.domain]

        for part in path_parts:
            if part not in current.keys():
                current.update({part: {}})
            current = current[part]

    def __str__(self):
        return json.dumps(self.root, indent=4, ensure_ascii=False)

def make_page_map(url: str, pass_list: list=[], have_list: list=[]):
    paths = scanner(url, pass_list=pass_list, have_list=have_list)

    split_paths = []
    for path in paths:
        split_paths.append(path.split('/'))

    page_map = PageMap(url)
    for path_parts in split_paths:
        page_map.insert(path_parts)

    return page_map.root
