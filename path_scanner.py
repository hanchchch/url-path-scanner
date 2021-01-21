import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from tqdm import tqdm
from .page_map import PageMap
from .utils import check_path, check_list, is_domain_self

INVAL_PATHS = {'=', '?', ' ', '<', '>'}

def gather_links(url: str, self_only: bool=True, path_only: bool=True, pass_list: list=[], have_list: list=[], inval_paths: set=set()):
    """
    Gathers all links of single url which can be accessible with "a" tag.

    :param url: start url
    
    :param self_only: gathers only if the link starts with start url

    :param path_only: returns path only if the link starts with start url

    :param pass_list: gathers only if the link does not contain the element of pass_list

    :param have_list: gathers only if the link contains the element of have_list

    :return: set of found paths
    """
    try:
        r = requests.get(url)
        print(url)
    except requests.exceptions.ConnectionError:
        print("ConnectionError: "+url)
        return []
    except requests.exceptions.InvalidURL:
        print("InvalidURL: "+url)
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    parsed_url_self = urlparse(url)
    path_self = parsed_url_self.path

    inval_paths |= INVAL_PATHS

    raw_links = []
    for a in soup.find_all('a'):
        try:
            raw_link = a.attrs['href']
        except KeyError:
            continue
        if 'javascript:' in raw_link:
            try:
                raw_link = raw_link.split('(')[1][1:]
                raw_link = raw_link.split(')')[0][:-1]
            except IndexError:
                continue
        raw_links.append(raw_link)

    for script in soup.find_all('script'):
        if script.string is None:
            continue
        script_parts = script.string.split('href')
        for script_part in script_parts:
            
            if '=' not in script_part[:3]:
                continue

            try:
                raw_link = script_part.split('"')[1]
            except IndexError:
                try:
                    raw_link = script_part.split("'")[1]
                except IndexError:
                    continue

            raw_links.append(raw_link)

    links = []
    for raw_link in raw_links:
        parsed_url = urlparse(raw_link)
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc
        path = parsed_url.path
        domain_self = False

        if check_list(parsed_url, pass_list, have_list, inval_paths):
            continue

        if not parsed_url.scheme.startswith('http'):
            if not parsed_url.scheme == '':
                continue
        
        if is_domain_self(parsed_url_self, parsed_url):
            if path == path_self:
                continue
            domain_self = True
            netloc = parsed_url_self.netloc
            scheme = parsed_url_self.scheme
        
        link = f"{scheme}://{netloc}{path}"

        if not domain_self and self_only:
            continue

        if domain_self and path_only:
            link = path
        
        links.append(link)

    links = set(links)
    return links

def list_scan(base_url: str, with_paths: set=('/'), pass_list: list=[], have_list: list=[]):
    """
    Finds paths of base_url which can be accessible with "a" tag, with a set of paths to visit.

    :param base_url: f"{scheme}://{netloc}"

    :param with_paths: set of paths to visit

    :param pass_list: gathers only if the path does not contain the element of pass_list

    :param have_list: gathers only if the path contains the element of have_list
    
    :return: set of found paths
    """

    paths = set()
    
    for with_path in tqdm(with_paths):
        if not with_path.startswith('/'):
            with_path = '/'+with_path
        url = base_url+with_path
        new_paths = gather_links(url, self_only=True, path_only=True, pass_list=pass_list, have_list=have_list)

        paths |= new_paths

    return paths

def make_page_map(url: str, breadth: int=15, depth: int=100, pass_list: list=[], have_list: list=[]):
    """

    :param depth: depth of search
    """

    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    visited = set()
    too_many_paths = set()
    visited_too_many = {}
    page_map = PageMap(url, breadth)

    if parsed_url.path != '':
        if parsed_url.query != '':
            new_paths = {parsed_url.path+'?'+parsed_url.query}
        else:
            new_paths = {parsed_url.path}
    else:
        if parsed_url.query != '':
            new_paths = {'?'+parsed_url.query}
        else:
            new_paths = {'/'}
    
    for _ in range(0, depth):
        found_paths = list_scan(base_url, new_paths, pass_list=pass_list, have_list=have_list)

        new_paths = found_paths - visited
        if len(new_paths) == 0:
            break
        visited |= new_paths
        
        for path in new_paths:
            page_map.insert(path)

        too_many_paths |= page_map.too_many
        for too_many_path in too_many_paths:
            visited_too_many.update({too_many_path: False})
        
        new_paths = set()
        for new_path in (set(page_map.paths) - visited):
            included_path = check_path(new_path, too_many_paths)

            if included_path:
                if visited_too_many[included_path]:
                    continue
                visited_too_many.update({included_path: True})
            
            new_paths.add(new_path)

    return page_map.root
