# cppgen

A command-line utility to generate boilerplate C/C++ code.

```
pip install --user cppgen
```

## `cppgen`

Generates C/C++ definition files from header files.

### Usage

```
usage: cppgen [-h] [--cpp CPP] [--ipp IPP] [-c {default,gnu,google}]
              [-i {convention,space,tab}] [-t TABSIZE] [--no-todo]
              FILE [FILE ...]

Generate definitions from headers

positional arguments:
  FILE                  A header file

optional arguments:
  -h, --help            show this help message and exit
  --cpp CPP             Suffix for files containing function definitions
                        (default: .cpp)
  --ipp IPP             Suffix for files containing inline/template function
                        definitions (default: .ipp)
  -c {default,gnu,google}, --convention {default,gnu,google}
                        Specify coding convention (default: default)
  -i {convention,space,tab}, --indent {convention,space,tab}
                        Specify indentation character (default: follow
                        convention)
  -t TABSIZE, --tabsize TABSIZE
                        Specify tab size (default: 0; follow convention)
  --no-todo             Do not insert todo comments
```

### Example

Header:

```cpp
// example.hpp
namespace example {
    class Test {
    public:
        Test ();
        ~Test ();
        int get ();
    };
}
```

Run:

```sh
$ cppgen example.hpp
Generate: example.hpp -> example.cpp
```

And result (`example.cpp`):

```cpp
#include "example.hpp"

namespace example {

Test::Test () {
    // TODO
}

Test::~Test () {
    // TODO
}

int Test::get () {
    // TODO
}

} /* namespace example */
```

## `hppgen`

Generates a header file.

### Usage

```
usage: hppgen [-h] [--suffix SUFFIX] [-f {snake_case,hyphen-case,lowercase,UPPERCASE,camelCase,PascalCase,CONST_CASE}] [-c {default,gnu,google}] [-i {convention,space,tab}] [-t TABSIZE] [TYPE] NAME

Generate a header

positional arguments:
  TYPE                  Type: class, struct, or enum (default: class)
  NAME                  (<NAMESPACE>::)*<NAME>

optional arguments:
  -h, --help            show this help message and exit
  --suffix SUFFIX       Suffix for the generated header file (default: .hpp)
  -f {snake_case,hyphen-case,lowercase,UPPERCASE,camelCase,PascalCase,CONST_CASE}, --file-convention {snake_case,hyphen-case,lowercase,UPPERCASE,camelCase,PascalCase,CONST_CASE}
                        Specify file naming convention (default: snake_case)
  -c {default,gnu,google}, --convention {default,gnu,google}
                        Specify coding convention (default: default)
  -i {convention,space,tab}, --indent {convention,space,tab}
                        Specify indentation character (default: follow convention)
  -t TABSIZE, --tabsize TABSIZE
                        Specify tab size (default: 0; follow convention)
```

### Example

Run:

```sh
$ hppgen foo::Bar
Generate: foo/bar.hpp
```

And result (`foo/bar.hpp`):

```cpp
#ifndef FOO_BAR_HPP
#define FOO_BAR_HPP

namespace foo {

class Bar {
public:
    Bar ();
    ~Bar ();
    Bar (const Bar &other);
    Bar (Bar &&other);

private:
};

} /* namespace foo */

#endif /* FOO_BAR_HPP */
```

