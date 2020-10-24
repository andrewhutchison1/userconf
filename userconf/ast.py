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

    @value.setter
    def value(self, value):
        assert isinstance(value, (Record, Array, String))
        self._value = value

    @property
    def children(self):
        return [self.key, self.value]

def pretty_print(node):
    """Pretty-prints an AST subtree rooted at `node`.
    Returns a string containing the pretty-printed AST subtree.
    """
    lines = []
    _pretty_print_impl(node, lines)
    return '\n'.join(lines)

def _pretty_print_impl(node, lines=None, prefix='', is_last_node=True):
    """Implementation function for `pretty-print`.
    Implements a pretty-printing algorithm, returning a list of strings that
    should be joined with newlines to form the final output string.
    """
    pass
