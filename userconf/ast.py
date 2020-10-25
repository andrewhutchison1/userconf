"""Userconf abstract syntax tree data structures and functions.
"""
from .scan import Token, TokenKind

class AbstractNode:
    def __init__(self):
        self._parent = None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

class String(AbstractNode):
    def __init__(self, data):
        super().__init__()
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
        super().__init__()
        self._children = []
        self._child_types = child_types

    def add_child(self, child):
        assert isinstance(child, self._child_types)
        self._children.append(child)
        child.parent = self

    @property
    def children(self):
        return self._children

class KeyValueNode(Node):
    def __init__(self):
        super().__init__(child_types=RecordItem)

    def keys(self):
        result = []
        for child in self.children:
            result.append(child.key.data)

        return result

    def __getitem__(self, key):
        result = []
        for child in self.children:
            if child.key.data == key:
                result.append(child.value)

        return result

    def __contains__(self, key):
        for child in self.children:
            if child.key.data == key:
                return True

        return False

class Document(KeyValueNode):
    def __init__(self):
        super().__init__()

class Record(KeyValueNode):
    def __init__(self):
        super().__init__()

class Array(Node):
    def __init__(self):
        super().__init__(child_types=(Record, String, Array))

    def __getitem__(self, index):
        return self.children[index]

    def __len__(self):
        return len(self.children)

class RecordItem(Node):
    def __init__(self, key, value):
        super().__init__()
        assert isinstance(key, String)
        assert isinstance(value, (Record, Array, String))
        self.add_child(key)
        self.add_child(value)

    @property
    def key(self):
        return self.children[0]

    @property
    def value(self):
        return self.children[1]

    def __iter__(self):
        return iter((self.key, self.value))

    @value.setter
    def value(self, value):
        assert isinstance(value, (Record, Array, String))
        self.children[1] = value

def decode(root):
    """Decodes an AST subtree rooted at `root` into a Python data structure.
    """
    if isinstance(root, String):
        return root.data
    elif isinstance(root, Array):
        decoded_children = [decode(child) for child in root.children]
    elif isinstance(root, (Document, Record)):
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

def _array_index_of_node(node):
    """Returns the (0-based) index of `node` if it is an array element.
    If it is not an array element, then None is returned.
    """
    if not isinstance(node.parent, Array):
        return None

    for i,child in enumerate(node.parent.children):
        if child is node:
            return i
