"""Userconf parser classes and functions.
"""
from functools import wraps

from . import ast
from .scan import TokenKind

class ParseResult:
    def __init__(self, succeeded, data=None):
        self._succeeded = succeeded
        self._data = data

    def __bool__(self):
        return self._succeeded

    @property
    def data(self):
        return self._data

def production(f):
    @wraps(f)
    def wrapper(self):
        state = self._save()
        result = f(self)
        if result is not False:
            return ParseResult(True, result)
        else:
            self._restore(state)
            return ParseResult(False)

    return wrapper

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self._tokens = tokens
        self._pos = 0

    def _save(self):
        return self._pos

    def _restore(self, state):
        self._pos = state

    def _accept(self, kind):
        if self.at_end:
            return False

        if self.cur.kind == kind:
            cur = self.cur
            self._pos += 1
            return cur

        return False

    def _expect(self, kind):
        if self.at_end:
            raise ParseError(f'Expected {kind.name}, got end of input')

        if cur := self._accept(kind):
            return cur
        else:
            raise ParseError(f'Expected {kind.name}, found {self.cur.kind}')

    def _accept_item_separator(self):
        if self.at_end:
            return False
        return self._accept(TokenKind.COMMA) or self.cur.leading_newline

    def reset(self, tokens):
        """Resets the state of the parser, with a new token list.
        """
        self._tokens = tokens
        self._pos = 0

    @production
    def parse(self):
        """Parses the top-level of a Userconf file.
        Returns a ParseResult that contains ast.Document if successful.
        """
        record_content = self.parse_record_content()

        if record_content and self.at_end:
            document = ast.Document()
            for record_item in record_content.data:
                document.add_child(record_item)

            return document

        raise ParseError(f'Expected end of input, got {self.cur.kind.name}')

    @production
    def parse_record(self):
        """Parses a record.
        Returns a ParseResult that contains ast.Record if successful.
        """
        if not self._accept(TokenKind.BRACE_OPEN):
            return False

        record_content = self.parse_record_content()
        self._expect(TokenKind.BRACE_CLOSE)

        record = ast.Record()
        for record_item in record_content.data:
            record.add_child(record_item)

        return record

    @production
    def parse_record_content(self):
        """Parses the contents of a record, which is also the top-level document syntax.
        On success, returns a ParseResult that contains a list of ast.RecordItem objects
        representing each record item, in the order they were specified.
        """
        record_item = self.parse_record_item()
        if not record_item:
            return []

        record_item_data = [record_item.data]
        while self._accept_item_separator():
            if record_item := self.parse_record_item():
                record_item_data.append(record_item.data)
            else:
                break

        return record_item_data

    @production
    def parse_record_item(self):
        """Parses a record item, which are the elements in which a record is composed of.
        On success, returns a ParseResult contains an ast.RecordItem object representing
        the key and value of the record item.
        """
        key = self.parse_record_key()
        if not key:
            return False

        value = self.parse_value()
        if not value:
            return False

        return ast.RecordItem(key.data, value.data)

    @production
    def parse_record_key(self):
        """Parses a record key, returning a ParseResult containing an ast.String object
        on success.
        """
        if quoted_string := self._accept(TokenKind.QUOTED_STRING):
            return ast.String(quoted_string.spelling)
        elif unquoted_string := self._accept(TokenKind.UNQUOTED_STRING):
            return ast.String(unquoted_string.spelling)

        return False

    @production
    def parse_value(self):
        """Parses a value, which is a string, record or array. On success, returns a ParseResult
        containing one of ast.String, ast.Record or ast.Array.
        """
        if quoted_string := self._accept(TokenKind.QUOTED_STRING):
            return ast.String(quoted_string.spelling)
        elif unquoted_string := self._accept(TokenKind.UNQUOTED_STRING):
            return ast.String(unquoted_string.spelling)
        elif multiline_string := self._accept(TokenKind.MULTILINE_STRING):
            return ast.String(multiline_string.spelling)
        elif record := self.parse_record():
            return record.data
        elif array := self.parse_array():
            return array.data

        return False

    @production
    def parse_array(self):
        """Parses an array, returning a ParseResult containing an ast.Array object on success.
        """
        if not self._accept(TokenKind.BRACK_OPEN):
            return False

        array_content = self.parse_array_content()
        self._expect(TokenKind.BRACK_CLOSE)

        array = ast.Array()
        for array_item in array_content.data:
            array.add_child(array_item)

        return array
    
    @production
    def parse_array_content(self):
        """Parses the contents of an array, returning a ParseResult containing a list of
        either ast.String, ast.Array or ast.Record objects on success.
        """
        value = self.parse_value()
        if not value:
            return []

        array_value_data = [value.data]
        while self._accept_item_separator():
            if value := self.parse_value():
                array_value_data.append(value.data)
            else:
                break

        return array_value_data

    @property
    def cur(self):
        return self._tokens[self._pos]

    @property
    def at_end(self):
        return self._pos == len(self._tokens)
