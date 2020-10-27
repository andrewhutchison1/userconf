# Userconf

A Python 3.8 implementation of the userconf configuration file format.

Userconf (user configuration format) is a user-oriented configuration file
format that is designed to be:

- Simple, unsurprising and intuitive
- Easy for humans to read
- Easy for humans to modify
- Easy for machines to parse
- Programming language agnostic

## The Userconf file format

- [Example](#example)
- [Overview](#overview)
    - [Document](#document)
        - [Encoding](#encoding)
        - [Comments](#comments)
        - [Whitespace](#whitespace)
        - [Reserved characters](#reserved-characters)
    - [Records](#records)
    - [Arrays](#arrays)
    - [Strings](#strings)
        - [Unquoted strings](#unquoted-strings)
        - [Quoted strings](#quoted-strings)
        - [Multiline strings](#multiline-strings)

Userconf is a text-based format for specifying program configuration options
that are expected to be modified by a human, and read by a machine (think `.bashrc` or
`.Xresources`).
In simplest terms, a Userconf file is a *record* (dictionary, hashmap) whose keys are
*strings*, and whose values may be *strings*, *records* or *arrays*.
This means that the only atomic datatype in a userconf file is a string, and the only compound
data types are records and arrays.

### Example

Here is an example Userconf file, which showcases all of its syntactic features:

    ; Example Userconf file
    profile     "default"

    owner
    {
        name    Andrew
        role    admin
    }

    database
    {
        enabled true
        ports   [8000, 8001, 8002]
    }

    servers
    {
        alpha   {ip 10.0.0.1, role frontend},
        beta    {ip 10.0.0.2, role frontend},
    }

    welcome-banner
        >Welcome to our server!
        >\nPress any key to continue, or CTRL-C to close the current connection.
        >\nEnjoy your stay!

### Overview

#### Document

A Userconf configuration file is called a *document* and consists of a top-level
[record](#records) without the `{` and `}` delimiters.
Since a Userconf document does not require opening and closing record delimiters
(unlike, say, JSON) multiple Userconf files can be concatenated freely.
The resulting concatenated file will be a valid Userconf document if and only if
each of the constituents are themselves Userconf documents.
Userconf documents may be empty, or contain only [comments](#comments) and
[whitespace](#whitespace).
The top-level of a Userconf file is syntactically identical to the contents of a Userconf
[record](#records).

##### Encoding

Userconf documents must be encoded as UTF-8.

##### Comments

    ; This is a comment

Comments in Userconf are line comments like `//` in C++ or `#` in Python, but they begin
with the `;` character.
There are no delimited comments (like `/*`, `*/` in C) in Userconf.
In situations where it is significant (see [whitespace](#whitespace)), a line comment is treated
as a single newline character.

##### Whitespace

Whitespace is generally insignificant in Userconf.
The only times whitespace must be explicitly considered are:

- Terminating [unquoted strings](#unquoted-strings) with any whitespace
- Terminating [comments](#comments) with a newline
- Separating each line of a [multiline string](#multiline-strings) with a newline
- A literal newline that causes a missing `,` to be automatically inserted
inside [records](#records) and [arrays](#arrays)

The following characters are interpreted as whitespace:
- `\t` (ASCII Horizontal tab) and ` ` (ASCII space)
- Newlines: `\n` (LF) and `\r\n` (CRLF)

Line endings may be freely mixed in a Userconf document.
Such a situation may result from a Userconf document saved by a Windows text editor with
`\r\n` (CRLF) line endings that was concatenated with a Userconf document saved by a UNIX
text editor with LF line endings (or vice versa).

##### Reserved characters

The following characters are reserved and have special meaning unless they appear in a string
(and are also escaped, if necessary):

- `{`, `}` (Record delimiters)
- `[`, `]` (Array delimiters)
- `,` (Record/array item separator)
- `;` (Comment begin character)
- `"` (Quoted string delimiter)
- `>` (Multiline string begin character)

#### Records

    {}

    {key value}

    {
        key value,
        other-key other-value
        "final-key" {nested true},
    }

A record (sometimes referred to as a *dictionary*, *hash map*, *map*, or *associative array*)
is a container of key-value pairs.
Records are expressed with the `{` and `}` delimiters which delimit zero or more key-value
items.
Each item in a record consists of a key and a value which are separated by whitespace.
Individual items are separated by `,`, which is automatically inserted if a newline is
encountered where `,` would otherwise be expected (*cf.* automatic semicolon insertion in
some programming languages). A single trailing comma is permitted but not required, and
consecutive commas will result in a parse error.

In Userconf, record keys are always [unquoted strings](#unquoted-strings) or
[quoted strings](#quoted-strings).
There are otherwise no requirements as to the contents of a record's keys
(in particular, they may be the empty string).
Record values may be any Userconf value: [strings](#strings) (any kind), [records](#records),
and [arrays](#arrays).
Every key in a record must have an associated value.

Records may be empty, an empty record is expressed as `{}`.

#### Arrays

    []
    
    [item1, item2, item3,]

    [
        item1,
        item2
        item3
    ]

An array is a linear container of values.
Arrays are expressed with the `[` and `]` delimiters which delimit zero or more array items.
An array item may be any Userconf value ([records](#records), [arrays](#arrays) or any
[string](#strings)).
Like [records](#records), array items must be separated by the `,` character, but a newline
where a `,` is expected will trigger the `,` to be inserted automatically.
Arrays can have trailing commas, but two or more commas may not appear consecutively.

Arrays may be empty, an empty array is expressed as `[]`.

#### Strings

The only atomic datatype in Userconf is the string.
There are three different ways to specify a string: *unquoted*, *quoted* and *multiline*.

##### Unquoted strings

    unquoted_string

A contiguous sequence of characters that does not contain any whitespace or reserved characters
(`{}[],;`) is an *unquoted string*.
Escape sequences are not interpreted in any special manner in unquoted strings,
so the unquoted string `hello\nthere` will literally contain the characters `\` and `n` and not
a linefeed character.
It is not syntactically possible to express an empty unquoted string.

##### Quoted strings

    "quoted string"

A double-quote delimited sequence of characters is a *quoted string*.
Quoted strings can contain any character except literal newlines, and the following escape
sequences are interpreted specially:

- `\n` (newline)
- `\t` (tab)
- `\"` (literal double quote)
- `\uXXXX` (hexademical unicode codepoint)

Quoted strings may be the empty string, which is expressed as `""`.

##### Multiline strings

    >This is a
    > multiline string

Multiline strings allow a user to specify a string that may span more than one line of userconf
source.
Multiline strings are specified by userconf source lines that begin with the `>` character and
end in a literal newline.
When these lines appear consecutively, they are joined verbatim to form the logical string.
Multiline strings are not raw: newlines are not interpreted as literal newlines (so the example
multiline string above is exactly equal to `"This is a multiline string"`).
In particular, multiline strings interpret exactly the same escape sequences as quoted strings.
Note that multiline strings may not appear as keys in a [record](#records).
Comments are not scanned in lines that are part of a multiline string:

    >This is a
    > multiline string ; This is part of the string, *not* a comment

Multiline strings may be empty if a literal newline immediately follows the `>` character:

    >

But empty strings are better specified with a [quoted string](#quoted-strings).
