# Format Patterns

A format pattern is a string provided to `hyper-bump-it` that goes through a text formatting
process before it is used. This is done using Python's [format string syntax][format-string].
While the link covers the full syntax, the key point is that values are referenced by enclosing 
the name in curly braces (positional references are not supported). Text outside the curly braces
will be left unaltered. If you need to include a brace character in the text, it can be escaped by
doubling the brace character (`{{` or `}}`). As a basic example, if the current version is `1.2.3`
and the new version is `4.5.6`

```text
"From {current_version} to {new_major}.{new_minor} {{new_major}}"
```

would become

```text
"From 1.2.3 to 4.5 {new_major}"
```

## Supported Keys

### Version Keys

| Name               | Description                              | Type           |
|--------------------|------------------------------------------|----------------|
| current_version    | Full current version                     | `Version`[^1]  |
| current_major      | Major part of current version            | `int`          |
| current_minor      | Minor part of current version            | `int`          |
| current_patch      | Patch part of current version            | `int`          |
| current_prerelease | Pre-release part of current version [^2] | `str`          |
| current_build      | Build part of current version [^2]       | `str`          |
| new_version        | Full new version                         | `Version` [^1] |
| new_major          | Major part of new version                | `int`          |
| new_minor          | Minor part of new version                | `int`          |
| new_patch          | Patch part of new version                | `int`          |
| new_prerelease     | Pre-release part of new version [^2]     | `str`          |
| new_build          | Build part of new version [^2]           | `str`          |

### General Context Keys

When a format pattern is being used as a search or replacement pattern, there are an additional set
of keys that may be used. Depending on the context, each key acts as an alias for one of the keys
listed above.

| Name       | Alias For (Search) | Alias For (Replace) |
|------------|--------------------|---------------------|
| version    | current_version    | new_version         |
| major      | current_major      | new_major           |
| minor      | current_minor      | new_minor           |
| patch      | current_patch      | new_patch           |
| prerelease | current_prerelease | new_prerelease      |
| build      | current_build      | new_build           |

As a basic example, if the current version is `1.2.3` and the new version is `4.5.6` and the format
pattern is `"version='{version}'"`.

When used as a search pattern it would become

```text
"version='1.2.3'"
```

But when used as a replacement pattern it would become

```text
"version='4.5.6'"
```

It is very common that the only differences between the search and replacement format patterns is
which version value they are referencing. These general context keys can be used for these cases to
reduce duplication in the configuration. (See [File Configuration][file-configuration])

### Helper Keys

So far, all the supported keys have been directly related to the version information for a specific
execution. However, `hyper-bump-it` is not limited to those type of values. The following are also
supported.

| Name          | Description                   | Type                |
|---------------|-------------------------------|---------------------|
| today         | Current date                  | `datetime.date`[^3] |

## Keystone File Considerations

When utilizing the [keystone file functionality][keystone-file], `hyper-bump-it` converts the
search format pattern into a regular expression that can be used to parse the current version from
the file.

### Key Precedence

General context keys take precedence over the explicit version keys. As an example, if the search
format string was `"{version} - {current_version}"`, only `version` would be used.

If the search format string contains `version` or `current_version`, no other keys will be used.

### Limitations

This conversion process imposes limitations on the search format pattern that can be used
for a keystone file. The most basic limitation is that if the search format pattern does **not**
contain `version` or `current_version`, the format pattern **must** contain keys to capture the
major, minor and patch part of the version.

Before getting into the specifics, format patterns that only use basic name only references (as
demonstrated earlier on this page) are **fully supported**.

* Attribute access and element indexes are **not** supported.
* Conversion flags are ignored.
* [Format specifications][format-specs] are only supported for `today`. Furthermore, the only
    supported specifications are the [date specific format code][date-format-code]. Within that
    set, codes that are dependent on the machine's locale are **not** supported.

[^1]:
    `Version` is equivalent to
    ```python
    @dataclass
    class Version:
        major: int
        minor: int
        patch: int
        prerelease: tuple[str, ...]
        build: tuple[str, ...]
    ```
[^2]:
    A period delimited string of each part of the value. If the version does not contain this
    value, the result will be an empty string.
[^3]:
    The [date][date] type supports defaults to the form of `YYYY-MM-DD`. This can be customized
    using [formatting codes][date-format-code].

[format-string]: https://docs.python.org/3/library/string.html#formatstrings
[file-configuration]: configuration.md#files
[keystone-file]: configuration.md#current-version
[format-specs]: https://docs.python.org/3/library/string.html#format-specification-mini-language
[date-format-code]: https://docs.python.org/3/library/datetime.html?highlight=strftime#strftime-and-strptime-format-codes
[date]: https://docs.python.org/3/library/datetime.html?highlight=strftime#datetime.date
