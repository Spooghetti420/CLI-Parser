import sys
from cli_parser import CLIArgument, CLIFlag, parser, CLIParser


if __name__ == "__main__":
    @parser
    class TestCLIParser(CLIParser):
        help: CLIFlag(help_str="Prints help message as to how to use the program.")
        n: CLIArgument( arg_type=int, nargs=1, switch=True)
        data: CLIArgument(arg_type=int, nargs=4)
        l: CLIFlag(help_str="Flag l.")
        i: CLIFlag(help_str="Flag i.")
        s: CLIFlag(help_str="Flag s.")
        a: CLIFlag(help_str="Flag a.")


def main():
    parser = TestCLIParser()
    parser.parse(sys.argv[1:])

if __name__ == "__main__":
    main()