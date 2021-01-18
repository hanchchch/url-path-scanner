# path_scanner
## Feature
Finds all paths of url which can be accessible with "a" tag.

+ depth
    + Set the depth of recersive search
+ pass_list, have_list
    + pass_list: gathers only if the path does not contain the element of pass_list
    + have_list: gathers only if the path contains the element of have_list

## example
```python
from urlpathscanner import scanner

r = scanner(URL, depth=2, pass_list=PASS_LIST, have_list=HAVE_LIST)
print(r)
```

# page_map
## Feature
Make page map (dict) using path_scanner

+ class PageMap
    + Trie algorithm

## example
```python
from urlpathscanner import make_page_map

result = make_page_map(URL, pass_list=PASS_LIST, have_list=HAVE_LIST)
with open('./page_map/page_map.json', 'a') as f:
    f.write(json.dumps(result, indent=4, ensure_ascii=False))
    f.write(',\n')