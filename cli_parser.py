from __future__ import annotations
import sys
from typing import Any, Optional
from dataclasses import dataclass, field
from abc import ABC
from typing_extensions import Self


class CLIParser(ABC):
    def __init__(self) -> None:
        """Parses the command-line arguments given by `token`s. Use `sys.argv` to acquire these from console."""
        self.arguments: dict[str, CLIArgument] = {}
        self.flags: dict[str, CLIFlag] = {}

    @classmethod
    def from_dict(cls, args: dict) -> Self:
        new = cls()
        for name, arg in args.items():
            if isinstance(arg, CLIFlag):
                new.add_flag(name, arg)
            elif isinstance(arg, CLIArgument):
                new.add_argument(name, arg)
            else:
                print("error: command-line setting is invalid; it must be type CLIFlag or CLIArgument")
        return new

    def add_argument(self, name, arg: CLIArgument) -> None:
        """Adds a named argument to the command line parser.
            It is stored in the parser under `name`. """
        self.arguments[name] = arg

    def add_flag(self, name, flag: CLIFlag) -> None:
        """Adds a flag to the command line parser.
            If the given flag is set in the command,
            its value will be `True` when parsed and False if not."""
        self.flags[name] = flag

    def parse(self, tokens: list = None) -> None:
        """
        Parses the command line arguments passed in as a list of strings.
        If the CLI strings passed is None, it will read from sys.argv[1:].
        """
        if tokens is None:
            tokens = sys.argv[1:]

        self._non_switches = {key: value for key, value in self.arguments.items() if not value.switch}

        self._results = self._parse(tokens) # Represents the actual passed arguments by the user
        self._post_parsing_check()

    def get(self, arg_name: str, default: Optional[Any] = None) -> Any:
        """Retrieve a parsed argument from the parser, optionally supplying a value to return if none is found."""
        if arg_name in self._results:
            return self._results[arg_name]
        else:
            return default            

    def _parse(self, tokens: list[str]) -> dict:
        # Initialise results to default values
        results: dict[list | Any] = {flag_name: False for flag_name in self.flags.keys()} | {arg_name: None for arg_name in self.arguments.keys()}

        token_stream = iter(tokens)
        for token in token_stream:
            if token.startswith("--"):
                remainder = token[2:]

                # If we have a flag-type argument, consider it satisfied and move on, e.g. --help
                if remainder in self.flags:
                    results[remainder] = True
                    continue

                # If the paramter is neither a flag, nor a registered argument, consider the user input erroneous
                if remainder not in self.arguments:
                    print(f"uncrecognised argument '{remainder}'")

                argument = self.arguments[remainder]
                for i in range(argument.nargs):
                    try:
                        subsequent = next(token_stream)
                    except:
                        print(f"argument '{remainder}' ended abruptly")
                        return results

                    self._cast_argument_and_set(subsequent, argument, results, remainder)

            elif token.startswith("-"):
                for i in token[1:]:
                    # Goes through all single-character flags, e.g. -lisa, and sets all of their values in the dict to True.
                    if i not in self.flags:
                        print(f"unrecognised flag {i}")
                    results[i] = True
            else:
                for name, arg in self._non_switches.items():
                    if not arg.satisfied:
                        self._cast_argument_and_set(token, arg, results, name)
                        break

                # There is a command-line argument, but no formal argument to store it => there is an error
                else:
                    print(f"no remaining arguments in which to store '{token}'")

        return results

    def _cast_to_desired_type(self, token: str, argument: CLIArgument) -> Any:
        """Turns a string argument into whatever that argument type is declared as, e.g. an int;
            example is converting "1234" to the integer 1234."""
        arg_type = argument.arg_type
        DIGITS = (1,2,3,4,5,6,7,8,9)
        if isinstance(arg_type, str):
            return token
        elif isinstance(arg_type, int):
            try:
                if token.startswith(DIGITS):
                    # Validates that string is in fact an integer (has no other symbols besides digits)
                    for char in token[1:]:
                        if char not in (0, *DIGITS):
                            raise TypeError()
            except TypeError:
                print(f"value {token} cannot be converted to type int")
            else:
                return int(token)
        else:
            # Attempt to cast to whatever other type the argument may represent
            try:
                cast_value = arg_type(token)
                return cast_value
            except ValueError:
                print(f"argument {argument.name} requires arguments of type {arg_type}, but received unconvertible argument {token}")

    def _set_argument_value(self, results_dict: dict, value: Any, arg: CLIArgument, name: str) -> None:
        if arg.nargs == 1:
            results_dict[name] = value
        elif results_dict.get(name):
            results_dict[name].append(value)
        else:
            results_dict[name] = [value]
        arg.current_args += 1

    def _cast_argument_and_set(self, token: str, arg: CLIArgument, results_dict: dict, name: str):
        cast_token = self._cast_to_desired_type(token, arg)
        self._set_argument_value(results_dict, cast_token, arg, name)

    def _post_parsing_check(self):
        for name, argument in self.arguments.items():
            if not argument.satisfied and not argument.optional:
                pass

    def print_help(self, title: Optional[str] = None) -> None:
        if title is None:
            title = "Command line parser"

        details = f"{title}:\n\tArguments:"

        if self.arguments:
            for name, argument in self.arguments.items():
                details += f"\n\t\t{'--' if argument.switch else ''}{name} (nargs: {argument.nargs}"
                if argument.switch:
                    details += ", switch"
                details += f")\t{argument.help_str if argument.help_str else ''}\tResults: {self._get_result_if_present(name)}"
        else:
            details += "\n\t\t(None)"

        details += "\n\tFlags:"

        if self.flags:
            for name, flag in self.flags.items():
                prefixed_name = ("-" if len(name) == 1 else "--") + name
                details += f"\n\t\t{prefixed_name}\t{flag.help_str}\tStatus: {self._get_result_if_present(name)}"
        else:
            details += "\n\t\t(None)"

        print(details)

    def _get_result_if_present(self, param_name: str) -> str:
        """Returns the value of the formal argument stored in the parser.
        If the parser has not received input to parse yet, then it returns
        [not parsed] for the given field."""
        return self._results.get(param_name, "[not parsed]")


# The below represent the data for different types of formal parameters in a CLI application.
# The actual results obtained from parsing the command-line input is stored elsewhere, namely in the
# parser object instance itself.
@dataclass
class CLIArgument:
    arg_type: type
    nargs: int = 1
    switch: bool = field(default_factory=bool)  # If this is True, it must be used with a hyphen or two preceding its name, e.g. `program.py --number-of-args 2` instead of `program.py 2`. 
    current_args: int = field(default=0, init=False)  # Used for when arguments are being parsed; indicates the number of args this Argument type has consumed already.
    optional: bool = field(default=False)
    help_str: str = field(default=None)

    @property
    def satisfied(self) -> bool:
        return self.current_args >= self.nargs


@dataclass
class CLIFlag:
    """A flag on the command-line is prefixed by one or two - (hyphen-minus characters), e.g. `-o`, `--help`."""
    help_str: str = field(default=None)