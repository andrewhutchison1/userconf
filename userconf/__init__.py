from .scan import Scanner
from .parse import Parser

def loads(s):
    if 'scanner' not in loads.__dict__:
        loads.scanner = Scanner(s)
    else:
        loads.scanner.reset(s)

    tokens = loads.scanner.scan_all()

    if 'parser' not in loads.__dict__:
        loads.parser = Parser(tokens)
    else:
        loads.parser.reset(tokens)

    return loads.parser.parse().data

def load(fp):
    return loads(fp.read())
