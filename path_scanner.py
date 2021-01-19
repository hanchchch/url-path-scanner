import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from tqdm import tqdm
from .utils import check_list, is_domain_self

INVAL_PATHS = ['=', '?', ' ', '<', '>']

def gather_links(url: str, **kwargs):
    """
    Gathers all links of single url which can be accessible with "a" tag.

    :param url: start url
    
    :param self_only: gathers only if the link starts with start url

    :param path_only: returns path only if the link starts with start url

    :param pass_list: gathers only if the link does not contain the element of pass_list

    :param have_list: gathers only if the link contains the element of have_list

    :return: list of found paths
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

    pass_list = kwargs.get('pass_list') if kwargs.get('pass_list') is not None else []
    have_list = kwargs.get('have_list') if kwargs.get('have_list') is not None else []

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

        if check_list(parsed_url, pass_list, have_list, INVAL_PATHS):
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

        if not domain_self and kwargs.get('self_only'):
            continue

        if domain_self and kwargs.get('path_only'):
            link = path
        
        links.append(link)

    links = list(set(links))
    return links

def list_scan(urls: list, pass_list: list=[], have_list: list=[]):
    """
    Finds paths of url list which can be accessible with "a" tag.

    :param urls: list of start urls

    :param pass_list: gathers only if the path does not contain the element of pass_list

    :param have_list: gathers only if the path contains the element of have_list
    
    :return: {... url: [paths]}
    """
    result = {}
    for url in tqdm(urls):
        path_list = gather_links(url, self_only=True, path_only=True, pass_list=pass_list, have_list=have_list)
        result.update({url: path_list})
    
    return result

def scanner(url: str, depth: int=100, pass_list: list=[], have_list: list=[]):
    """
    Finds all paths of url which can be accessible with "a" tag.

    :param url: start url

    :param depth: depth of search

    :param pass_list: gathers only if the path does not contain the element of pass_list

    :param have_list: gathers only if the path contains the element of have_list

    :return: [paths]
    """

    parsed_url_self = urlparse(url)
    base_url = f"{parsed_url_self.scheme}://{parsed_url_self.netloc}"

    urls = [url]
    paths = set()
    for _ in range(0, depth):
        new_paths = set()
        scan_result = list_scan(urls, pass_list, have_list)
        for key in scan_result.keys():
            new_paths |= set(scan_result[key])

        urls = []
        delete_paths = set()
        for new_path in new_paths:
            self_path = urlparse(base_url+new_path).path
            if parsed_url_self.path == self_path:
                delete_paths |= {new_path}
                continue
            urls.append(base_url+new_path)

        new_paths -= delete_paths
        if len(new_paths - paths) == 0:
            break

        paths |= new_paths

    return list(paths)
