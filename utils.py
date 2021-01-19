from urllib.parse import urlparse, ParseResult

def check_list(parsed_url: ParseResult, pass_list: list=[], have_list: list=[], inval_paths: list=[]):
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc
    path = parsed_url.path

    for inval_path in inval_paths:
        if inval_path in path:
            return True

    for pas in pass_list:
        if pas in netloc:
            return True
    
    if 'http' in scheme:
        if len(have_list) == 0:
            return False
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