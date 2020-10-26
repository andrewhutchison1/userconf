"""Userconf abstract syntax tree data structures and functions.
"""
from .scan import Token, TokenKind

class AbstractNode:
    def __init__(self):
        self._parent = None

    def _is_transitive_array_element(self):
        """Returns True if this AST node or any of its ancestors are elements of an array AST
        node, and False otherwise. This is used in determining whether an AST node has a merge
        path.
        """
        return any(isinstance(ancestor, Array) for ancestor in self._ancestors())

    def _ancestors(self):
        """Returns a list of the ancestors of this AST node, ordered in ascending order
        of degree of separation."""
        node = self.parent
        result = []
        while node is not None:
            result.append(node)
            node = node.parent

        return result

    @property
    def has_path(self):
        """Returns True if this node has a merge path, and False otherwise."""
        # Transitive array elements do not have merge paths because arrays do not merge, they
        # overwrite. Only strings, records and arrays can possibly have merge paths
        if not isinstance(self, (String, Record, Array)) or self._is_transitive_array_element():
            return False

        # String nodes have merge paths only when they are the values of a record or document,
        # not the key.
        if isinstance(self, String) and self is not self.parent.value:
            return False

        return True

    @property
    def path(self):
        """Returns the merge path of this AST node if it has one; and None otherwise.
        The merge path is returned as a tuple of strings.
        """
        if not self.has_path:
            return None

        path = []
        node = self
        while node.parent is not None:
            if isinstance(node.parent, RecordItem):
                path.append(node.parent.key.data)

            node = node.parent

        return tuple(reversed(path))

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

def iter_preorder(root):
    """Performs a preorder traversal of the AST subtree rooted at `root`."""
    yield root

    if isinstance(root, String):
        return

    for child in root.children:
        yield from iter_preorder(child)

def _path_common_prefix(first, second):
    """Returns the common prefix of two merge paths, or None if there is no common prefix."""
    result = []
    for f,s in zip(first, second):
        if f == s:
            result.append(f)
        else:
            break

    return tuple(result) if len(result) != 0 else None

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

class Document(Node):
    def __init__(self):
        super().__init__(child_types=RecordItem)

class Record(Node):
    def __init__(self):
        super().__init__(child_types=RecordItem)

    @property
    def keys(self):
        return [key.data for key,_ in self.children]

class Array(Node):
    def __init__(self):
        super().__init__(child_types=(Record, String, Array))

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

class Decoder:
    """Decodes an AST into a Python data structure."""
    def __init__(self, root):
        self._root = root
        self._data = {}

    def decode(self):
        for node in iter_preorder(self._root):
            if node.has_path:
                self._data[node.path] = node

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
