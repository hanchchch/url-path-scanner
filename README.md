# list_scan
## Feature
Finds all paths of url which can be accessible with "a" tag and javascript.

+ pass_list, have_list
    + pass_list: gathers only if the path does not contain the element of pass_list
    + have_list: gathers only if the path contains the element of have_list

## example
```python
from urlpathscanner import list_scan

r = list_scan(URL, with_paths={'/','login','service'}, pass_list=PASS_LIST, have_list=HAVE_LIST)
print(r)
```

# make_page_map
## Feature
Make page map (dict) using list_scan

+ class PageMap
    + Trie algorithm

+ breadth
    + Set the breadth of search
+ depth
    + Set the depth of recersive search

## example
```python
from urlpathscanner import make_page_map

result = make_page_map(URL, breadth=15, depth=10, pass_list=PASS_LIST, have_list=HAVE_LIST)
with open('./page_map/page_map.json', 'a') as f:
    f.write(json.dumps(result, indent=4, ensure_ascii=False))
