from urllib.parse import urlparse, ParseResult

def cut_path(path: str, no_cut: bool):
    if no_cut:
        return path
    
    return  path[:-1] if path.endswith('/') else path

def check_list(parsed_url: ParseResult, pass_list: list=[], have_list: list=[]):
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc

    for pas in pass_list:
        if pas in netloc:
            return True
    
    if 'http' in scheme:
        for have in have_list:
            if have in netloc:
                return False
        return True
    
    return False

def is_domain_self(parsed_url_self: ParseResult, parsed_url: ParseResult):
    if parsed_url.netloc == parsed_url_self.netloc:
        return True

    elif parsed_url.netloc == '':
        if parsed_url.scheme == '':
            return True
    
    return False