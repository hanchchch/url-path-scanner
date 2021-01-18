# url_path_scanner
## Feature
Finds all paths of url which can be accessible with "a" tag.

+ depth
    + Set the depth of recersive search
+ pass_list, have_list
    + pass_list: gathers only if the path does not contain the element of pass_list
    + have_list: gathers only if the path contains the element of have_list

## example
```python
from urlpathscanner import url_path_scanner

r = url_path_scanner('https://www.google.com', depth=2, pass_list=PASS_LIST, have_list=HAVE_LIST)
print(r)
```
