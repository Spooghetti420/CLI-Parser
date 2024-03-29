# CLI Parser
This is a program to generate a command-line parser in Python, effectively mirroring the built-in `argparse` module.
I find this more modern method to be easier to understand than the `argparse` approach, as it has fewer features
and focuses on only the most basic features; this allows the parser to be described very simply.

## Creating a parser
To create a new specialised command-line parser, just create an instance of the `CLIParser` class.
You can add new arguments using `add_argument(arg_name, arg)` or `add_flag(flag_name, flag)`; `arg` is a `CLIArgument`
instance, whereas `flag` is a `CLIFlag` instance. 

Flags are effectively booleans that can be triggered once, such
as `-a`, `--help`, etc., and if such an input is passed to the parameter, it stores `True` as its value in the parser's
output.

Arguments are more versatile, in that they can store any number of arguments (currently, indefinite size is not yet
supported, though), e.g. given `python main.py 1 2 3`, the arguments 1, 2, and 3 are passed into the parser. What
these are converted to (kept as `str`, turned to `int`, or a custom type) depends on the `CLIArgument`s given to the
parser.

`parser.parse()` will then send the arguments to the parser, which will figure out what arguments were actually passed, give warnings about misconstructions, etc.; you can also give an optional list of command-line tokens
(separate words), but the default that the function uses is `sys.argv[1:]`.

Finally, you can access the paramters of the parser after it has parsed the arguments using `parser.get(<key_name>)`, e.g. `parser.get("help")` for the above parser returns the value of the boolean flag `help`. If `--help` was passed as a command-line argument, then it will be true, else false. All non-flag arguments, i.e. those that accept parameters (e.g. `n` above), need an argument; if they are not passed, the parser will give a warning, and if they are accessed in the program anyway, it will raise an error. There is also the option, like `dict.get`, to pass an optional value
to be returned instead of the returned argument, in case the argument doesn't exist.

### Via `from_dict`
You can also create a parser more declaratively using a dictionary; this example comes from `main.py`:
```
parser = CLIParser.from_dict(
    {
        "help": CLIFlag(help_str="Prints help message as to how to use the program."),
        "n": CLIArgument(arg_type=int, nargs=1, switch=True),
        "data": CLIArgument(arg_type=int, nargs=4),
        "l": CLIFlag(help_str="Flag l."),
        "i": CLIFlag(help_str="Flag i."),
        "s": CLIFlag(help_str="Flag s."),
        "a": CLIFlag(help_str="Flag a.")
    }
)
```

### Printing the results of parsing (result of \_\_repr\_\_)
If the parser is fed the following input: `python main.py --n 50 1 2 3 4`, printing the parser object gives this printout:
```
Command line parser:
        Arguments:
                --n (nargs: 1, switch)          Results: 50
                --data (nargs: 4)               Results: [1, 2, 3, 4]
        Flags:
                --help  Prints help message as to how to use the program.       Status: False
                -l      Flag l. Status: False
                -i      Flag i. Status: False
                -s      Flag s. Status: False
                -a      Flag a. Status: False
```
The "results" and "status" parts will show `[not parsed]` if the parsing has not been completed for a formal parameter,
else like above, it will show whatever arguments were passed into the parser at runtime.

## Dependencies
There are none :)

## To do
- [] Make optional paramters
- [] Make parameters of arbitrary number of arguments (argparse equivalent of `*`)