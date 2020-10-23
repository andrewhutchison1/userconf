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

```
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
```
