import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from tqdm import tqdm
from .utils import cut_path, check_list, is_domain_self


def gather_links(url: str, **kwargs):
    """
    Gathers all links of single url which can be accessible with "a" tag.

    :param url: start url
    
    :param no_cut: does not remove the last slash of paths

    :param self_only: gathers only if the link starts with start url

    :param path_only: returns path only if the link starts with start url

    :param pass_list: gathers only if the link does not contain the element of pass_list

    :param have_list: gathers only if the link contains the element of have_list

    :return: list of found paths
    """
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    parsed_url_self = urlparse(url)
    no_cut = True if kwargs.get('no_cut') else False
    path_self = cut_path(parsed_url_self.path, no_cut)

    pass_list = kwargs.get('pass_list') if kwargs.get('pass_list') is not None else []
    have_list = kwargs.get('have_list') if kwargs.get('have_list') is not None else []

    links = []
    for a in soup.find_all('a'):
        try:
            raw_link = a.attrs['href']
        except KeyError:
            continue
        parsed_url = urlparse(raw_link)
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc
        path = cut_path(parsed_url.path, no_cut)
        domain_self = False

        if check_list(parsed_url, pass_list, have_list):
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

def urllist_path_scan(urls: list, pass_list: list=[], have_list: list=[]):
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

def url_path_scanner(url: str, depth: int=100, pass_list: list=[], have_list: list=[]):
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
        scan_result = urllist_path_scan(urls, pass_list, have_list)
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
