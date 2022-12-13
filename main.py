import sys
from cli_parser import CLIArgument, CLIFlag, CLIParser


def main():
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
    parser.parse(sys.argv[1:])
    print(parser)

if __name__ == "__main__":
    main()