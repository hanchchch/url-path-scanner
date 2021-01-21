import json

class PageMap:
    def __init__(self, domain: str, breadth: int=15):
        self.domain = domain
        self.root = {domain: {}}
        self.paths = set()
        self.too_many = set()
        self.breadth = 15

    def __str__(self):
        return json.dumps(self.root, indent=4, ensure_ascii=False)

    def paths_startwith(self, path):
        result = 0
        for path_hay in self.paths:
            if path_hay.startswith(path):
                result += 1
        
        return result

    def insert(self, path: str):
        path_parts = path.split('/')
        if path_parts[0] == '':
            path_parts = path_parts[1:]
        
        current = self.root[self.domain]
        current_path = ''

        for part in path_parts:
            current_path += f'/{part}'
            paths_startwith_count = self.paths_startwith(current_path)
            if paths_startwith_count == 0:
                self.paths.add(current_path)

            elif paths_startwith_count > self.breadth:
                if current_path != '/':
                    self.too_many.add(current_path)

            if part not in current.keys():
                current.update({part: {}})
            current = current[part]
