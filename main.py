import sys
from cli_parser import CLIArgument, CLIFlag, parser, CLIParser


@parser
class LanguageCLIParser(CLIParser):
    help: CLIFlag()


def main():
    parser = LanguageCLIParser()
    parser.parse(sys.argv[1:])
    if parser["help"]:
        print("usage: main.py <INPUT FILE>")
    else:
        print("main.py running normally")
    
if __name__ == "__main__":
    main()