"""Userconf abstract syntax tree data structures and functions.
"""
from .scan import Token, TokenKind

class AbstractNode:
    pass

class String(AbstractNode):
    def __init__(self, data):
        assert isinstance(data, str)
        self._data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data 

class Node(AbstractNode):
    def __init__(self, /, child_types=AbstractNode):
        self._children = []
        self._child_types = child_types

    def add_child(self, child):
        assert isinstance(child, self._child_types)
        self._children.append(child)

    @property
    def children(self):
        return self._children

class Document(Node):
    def __init__(self):
        super().__init__(child_types=RecordItem)

class Record(Node):
    def __init__(self):
        super().__init__(child_types=RecordItem)

class Array(Node):
    def __init__(self):
        super().__init__(child_types=(Record, String, Array))

class RecordItem(Node):
    def __init__(self, key, value):
        super().__init__()
        assert isinstance(key, String)
        assert isinstance(value, (Record, Array, String))
        self._key = key
        self._value = value

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value

    def __iter__(self):
        return iter((self.key, self.value))

    @value.setter
    def value(self, value):
        assert isinstance(value, (Record, Array, String))
        self._value = value

    @property
    def children(self):
        return [self.key, self.value]

class ASTDecoder:
    """Decodes a userconf AST into a Python object."""
    def __init__(self, root):
        """Initialises the AST decoder with the AST subtree rooted at `root`.
        """
        pass

def pretty_print(node):
    """Pretty-prints an AST subtree rooted at `node`.
    Returns a string containing the pretty-printed AST subtree.
    """
    lines = []
    _pretty_print_impl(node, lines)
    return '\n'.join(lines)

def _pretty_print_impl(node, lines, prefix='', is_last_node=True):
    """Implementation function for `pretty-print`.
    Implements the pretty-printing algorithm by recursively appending
    pretty-printed lines of text to the list `lines`.
    """
    if isinstance(node, String):
        child_count = 0
        node_string = f'String {repr(node.data)}'
    else:
        child_count = len(node.children)
        node_string = node.__class__.__name__

    lines.append(f'{prefix}{"`- " if is_last_node else "|- "}{node_string}')
    if is_last_node:
        prefix += '   '
    else:
        prefix += '|  '

    if child_count == 0:
        return

    for i,child in enumerate(node.children):
        if i == child_count - 1:
            is_last_node = True
        else:
            is_last_node = False

        _pretty_print_impl(child, lines, prefix, is_last_node)

