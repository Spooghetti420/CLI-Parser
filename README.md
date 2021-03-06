# CLI Parser
This is a program to generate a command-line parser in Python, effectively mirroring the built-in `argparse` module.
I find this more modern method to be easier to understand than the `argparse` approach, as it has fewer features
and focuses on only the most basic features; this allows the generator to be described very simply.

## Creating a generator
Create a class that inherits from the `CLIParser` class, and decorate it using the @parser decorator:
```
@parser
class TestCLIParser(CLIParser):
        help: CLIFlag(help_str="Prints help message as to how to use the program.")
        n: CLIArgument(arg_type=int, nargs=1, switch=True)
        data: CLIArgument(arg_type=int, nargs=4)
        l: CLIFlag(help_str="Flag l.")
        i: CLIFlag()
        s: CLIFlag()
        a: CLIFlag()
```
By doing this, you define a new type of class from which you can create command-line parsers with those parameters. E.g. now running `parser=TestCLIParser()` will create a new parser with these formal parameters available. `parser.parse(sys.argv[1:])` will then send the arguments to the parser, which will figure out what arguments were actually passed, give warnings about misconstructions, etc.
Finally, you can access the paramters of the parser after it has parsed the arguments using `parser[<key_name>]`, e.g. `parser["help"]` for the above parser returns the value of the boolean flag `help`. If `--help` was passed as a command-line argument, then it will be true, else false. All non-flag arguments, i.e. those that accept parameters (e.g. `n` above), need an argument; if they are not passed, the parser will give a warning, and if they are accessed in the program anyway, it will raise an error.


### A neater layout of the above parser (result of __repr__)
```
Command line parser TestCLIParser:
        Arguments:
                --n (nargs: 1, switch)          Results: 54
                --data (nargs: 4)               Results: [1, 2, 3, 4]
        Flags:
                --help  Prints help message as to how to use the program.       Status: False
                -l      Flag l. Status: False
                -i      Flag i. Status: False
                -s      Flag s. Status: False
                -a      Flag a. Status: False
```
The "results" and "status" parts will show `[not parsed]` if the parsing has not been invoked,
else like above, it will show whatever parameters were passed into the parser.

## Dependencies
There are none :)

## To do
- [] Make optional paramters
- [] Make parameters of arbitrary number of arguments (argparse equivalent of `*`)