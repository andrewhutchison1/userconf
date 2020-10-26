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

### Features

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

##### Quoted strings

    "quoted string"

A double-quote delimited sequence of characters is a *quoted string*.
Quoted strings can contain any character except literal newlines, and the following escape
sequences are interpreted specially:

- `\n` (newline)
- `\t` (tab)
- `\"` (literal double quote)
- `\uXXXX` (hexademical unicode codepoint)

##### Multiline strings

    >This is a
    > multiline string

Multiline strings allow a user to specify a string that may span more than one line of userconf
source.
Multiline strings are specified by userconf source lines that begin with the `>` character and
end in a literal newline.
When these lines appear consecutively, they are joined verbatim to form the logical string.
Multiline strings are not raw: newlines are not interpreted as literal newlines (so the example
multiline string above is exactly equal to "This is a multiline string").
In particular, multiline strings interpret exactly the same escape sequences as quoted strings.
Note that multiline strings may not appear as keys in a record.
