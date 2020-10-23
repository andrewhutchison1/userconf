"""Userconf lexical analysis types and functions.
"""
from enum import Enum, auto

WHITESPACE  = (' ', '\t')
NEWLINE     = ('\r\n', '\n')
RESERVED    = ('{', '}', '[', ']', ',', ';')

class TokenKind(Enum):
    BRACE_OPEN = auto()
    BRACE_CLOSE = auto()
    BRACK_OPEN = auto()
    BRACK_CLOSE = auto()
    COMMA = auto()
    UNQUOTED_STRING = auto()
    QUOTED_STRING = auto()
    MULTILINE_STRING = auto()

    @property
    def is_string(self):
        return self in (
                TokenKind.UNQUOTED_STRING,
                TokenKind.QUOTED_STRING,
                TokenKind.MULTILINE_STRING)

class Token:
    def __init__(self, kind, leading_newline, spelling=None):
        """Initialises the Token object with a TokenKind, an optional spelling if `kind` is
        a string token kind, and a boolean indicating whether the token contains leading
        (preceding) newline characters (used for automatic comma insertion in the parser).
        """
        assert isinstance(kind, TokenKind)
        if kind.is_string:
            assert spelling is not None and isinstance(spelling, str)
        else:
            assert spelling is None

        self._kind = kind
        self._spelling = self._escape_string(spelling) if self.kind.is_string else spelling
        self._leading_newline = leading_newline

    def _escape_string(self, spelling):
        return spelling.replace('\\n', '\n')

    def __str__(self):
        leading_nl = ' [leading newline]' if self._leading_newline else ''
        if self.kind.is_string:
            return f'{self._kind.name} {repr(self._spelling)}{leading_nl}'
        else:
            return f'{self._kind.name}'

    def __bool__(self):
        return True

    @property
    def kind(self):
        return self._kind

    @property
    def spelling(self):
        return self._spelling

    @property
    def leading_newline(self):
        return self._leading_newline

class ScanError(Exception):
    pass

class Scanner:
    def __init__(self, source):
        """Initialises the Scanner at position 0 of the given source string.
        """
        self._source = source
        self._pos = 0

    def _advance(self, count=1):
        """Advances the Scanner position by `count` characters. If this would
        exceed the length of the source, then an AssertionError is raised.
        """
        assert self._pos + count <= len(self._source)
        self._pos += count

    def _peek(self, count=1):
        """Returns the next `count` characters starting from and including the
        Scanner's position. If this would exceed the length of the source,
        then None is returned.
        """
        if self._pos + count > len(self._source):
            return None
        else:
            return self._source[self._pos : self._pos + count]

    def _test(self, what):
        """Tests the Scanner for a string, returning True if found and False otherwise.
        Does not modify the Scanner position.
        """
        return self._peek(len(what)) == what

    def _test_any(self, testers):
        """Given an iterable containing strings, tests each string in order,
        returning True after the first test success. Returns False if none of the
        strings are found. Does not modify the Scanner position.
        """
        for tester in testers:
            if self._test(tester):
                return True

        return False

    def _accept(self, what):
        """Accepts a string. Peeks the source at the current position and compares
        it to the string `what`. If they are equal, then the Scanner's position is
        advanced by the length of `what` and `what` is returned. If they are not
        equal, False is returned and the Scanner's position is not modified.
        If `what` is an empty string, then an AssertionError will be raised.
        """
        assert what != ''
        if self._test(what):
            self._advance(len(what))
            return what
        else:
            return False

    def _accept_any(self, acceptors):
        """Given an iterable containing strings, attempts to accept each string
        in order, stopping after the first string is accepted and returning the
        accepted string. Returns False if no strings were accepted.
        """
        for acceptor in acceptors:
            if accepted := self._accept(acceptor):
                return accepted

        return False

    def _skip_whitespace(self):
        """Advances the Scanner position while it refers to any character in `WHITESPACE`.
        Returns True if the position was modified.
        """
        skipped = False
        while not self.at_end and self._accept_any(WHITESPACE):
            skipped = True

        return skipped

    def _skip_newline(self):
        """Advances the Scanner position while it refers to any character in `NEWLINE`.
        Returns True if the position was modified.
        """
        skipped = False
        while not self.at_end and self._accept_any(NEWLINE):
            skipped = True

        return skipped

    def _skip_comment(self):
        """Skips a line comment. Returns True if the Scanner's position was modified.
        """
        if not self._accept(';'):
            return False

        while not self.at_end and not self._accept_any(NEWLINE):
            self._advance()

        return True

    def _ignore_leading(self):
        """Combines the behaviour of `_skip_whitespace`, `_skip_newline` and `_skip_comment`
        to ignore irrelevant leading characters when scanning a token. Returns True if one
        or more of the skipped characters were newlines or comments, and False otherwise.
        """
        ws, nl, cmt = self._skip_whitespace(), self._skip_newline(), self._skip_comment()
        if not(any((ws, nl, cmt))):
            return False

        leading_newline = nl or cmt
        while any((ws, nl, cmt)):
            ws = self._skip_whitespace()
            nl = self._skip_newline()
            cmt = self._skip_comment()
            leading_newline = leading_newline or nl or cmt

        return leading_newline

    def _scan_quoted_string(self, leading_newline):
        """Attempts to scan a quoted string, returning it on success. If a quoted string was
        not scanned, None is returned. If an error is encountered, then ScanError is raised
        (for example, when the quoted string is not terminated).
        """
        if not self._accept('"'):
            return None

        string = []
        while not self.at_end and not self._accept('"'):
            if self.at_end:
                raise ScanError('EOF when scanning quoted string')
            elif self._test_any(NEWLINE):
                raise ScanError('Illegal newline in quoted string at {self._pos}')
            elif self._test('\\"'):
                string.append('"')
                self._advance(2)
            else:
                string.append(self._peek())
                self._advance()

        return Token(TokenKind.QUOTED_STRING, leading_newline, ''.join(string))

    def _scan_multiline_string_line(self):
        if not self._accept('>'):
            return None

        string = []
        while not self.at_end and not self._accept_any(NEWLINE):
            string.append(self._peek())
            self._advance()

        return ''.join(string)

    def _scan_multiline_string(self, leading_newline):
        """Attempts to scan a multiline string, returning a Token representing the multiline
        string if successful, and None otherwise.
        """
        line = self._scan_multiline_string_line()
        if line is None:
            return None

        multiline = []
        while line is not None:
            multiline.append(line)
            self._skip_whitespace()
            line = self._scan_multiline_string_line()

        return Token(TokenKind.MULTILINE_STRING, leading_newline, ''.join(multiline))

    def _scan_unquoted_string(self, leading_newline):
        """Attempts to scan an unquoted string, returning a Token representing the unquoted
        string if successful, and None otherwise.
        """
        # The set of characters that can terminate an unquoted string
        TERMINATORS = WHITESPACE + NEWLINE + RESERVED

        string = []
        while not self.at_end and not self._test_any(TERMINATORS):
            string.append(self._peek())
            self._advance()

        if len(string) == 0:
            return None

        return Token(TokenKind.UNQUOTED_STRING, leading_newline, ''.join(string))

    def reset(self, source):
        """Resets the state of the scanner, with a new source.
        """
        self._source = source
        self._pos = 0

    def scan_one(self):
        """Scans input until a single token is recognised, end of input is reached, or a syntax
        error is encountered. If a token is recognised, it is returned; if end of input is reached
        then None is returned; and if a syntax error is encountered then a ScanError will be
        raised containing the appropriate diagnostic information.
        """
        leading_newline = self._ignore_leading()
        if self.at_end:
            return None

        if self._accept('{'):
            return Token(TokenKind.BRACE_OPEN, leading_newline)
        elif self._accept('}'):
            return Token(TokenKind.BRACE_CLOSE, leading_newline)
        elif self._accept('['):
            return Token(TokenKind.BRACK_OPEN, leading_newline)
        elif self._accept(']'):
            return Token(TokenKind.BRACK_CLOSE, leading_newline)
        elif self._accept(','):
            return Token(TokenKind.COMMA, leading_newline)

        if quoted_string := self._scan_quoted_string(leading_newline):
            return quoted_string

        if multiline_string := self._scan_multiline_string(leading_newline):
            return multiline_string

        if unquoted_string := self._scan_unquoted_string(leading_newline):
            return unquoted_string

        raise ScanError(f'Unrecognised character {repr(self._peek())} at position {self._pos}')

    def scan_all(self):
        """Scans input until the end of file is reached, or an error occurs, returning the
        scanned tokens in a list.
        """
        tokens = []
        while token := self.scan_one():
            tokens.append(token)

        return tokens

    @property
    def at_end(self):
        """True if the Scanner's position is at the end of the source.
        """
        return self._pos == len(self._source)
