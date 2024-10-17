# recompylr

`recompylr` is a simple Python script which will compile C programs many times
for different values of specified definitions. A TOML file is used to specify
the build configuration, including the names to be defined and the values those
names should take in each binary.

`recompylr` is provided within an example use case repository, where the C
program computes a numerical integration task. `recompylr` is used here to
generate binaries from the source file, varying the number of threads the
program may use to complete the computation.

The TOML specification file must contain the following properties:

```toml
[compilation]
# Where to look for C files
source_file_directory = "src"

# How to compile and link the C files
compiler = "gcc"
compilation_flags = ["-Wall", "-Werror", "-Wextra", "-Wpedantic"]
linker_flags = ["-lm", "-lpthread"]

# How the binaries should be named
binary_file_definition_delimeter = "-"
binary_file_extension = ".out"
binary_output_directory = "bin"

# Names and values to be defined the programs
[compilation.definitions]
NUMBER_OF_THREADS = [1, 2, 3]
MAX_CHILDREN = [1, 2, 3]
LOGGING = true
```

All properties defined within the `[compilation.definitions]` table will be
passed to the compiler using the `-D` flag. Definition values can be anything
that when passed as a string to the preprocessor, will be accepted by the
compiler (integers, floats, strings).
Note that booleans are a little tricky as Python capitalises the first letter
of each boolean value. Currently, as values are passed straight through to the
compiler as the string value of their python objects booleans values create
compiler errors if their values are read any way other than `#ifdef`.

When values are given as lists (as shown in above example), one binary is
generated for each value in the list. When multiple definitions have list
values, one binary is compiled for each item in the Cartesian product of these
lists. For the above example, a binary is generated for each of:

```csv
(1, 1, true),
(1, 2, true),
(1, 3, true),
(2, 1, true),
(2, 2, true),
(2, 3, true),
(3, 1, true),
(3, 2, true),
(3, 3, true)
```

Where the values in each tuple represent the values of
`NUMBER_OF_THREADS, MAX_CHILDREN, LOGGING`.
