from __future__ import annotations

import logging
import sys
from typing import Any
from dataclasses import dataclass, field
from abc import ABC

# Set up logging: only output warnings or errors to console, but output everything to file
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.WARNING)
stream_handler.setFormatter(logging.Formatter('[%(levelname)s]: %(message)s'))
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s:%(asctime)s]: %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        stream_handler
    ]
)
logging.info("cli_parser.py started")


class CLIParser(ABC):
    arguments: dict[CLIArgument, CLIArgument] = {}
    flags: dict[CLIFlag] = {}

    def __init__(self) -> None:
        """Parses the command-line arguments given by `token`s. Use `sys.argv` to acquire these from console."""
        self._non_switches = {key: value for key, value in self.arguments.items() if not value.switch}
        self._results = {}  # Represents the actual passed arguments by the user

    def parse(self, tokens: list) -> None:
        """Parses the command line arguments passed in as a list of strings."""
        self._results = self._parse(tokens)
        self._post_parsing_check()

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
                    logging.error(f"uncrecognised argument '{remainder}'")
                    raise SystemExit(1)

                argument = self.arguments[remainder]
                for i in range(argument.nargs):
                    try:
                        subsequent = next(token_stream)
                    except:
                        logging.error(f"argument '{remainder}' ended abruptly")
                        raise SystemExit(1)
                    self._cast_argument_and_set(subsequent, argument, results)

            elif token.startswith("-"):
                for i in token[1:]:
                    # Goes through all single-character flags, e.g. -lisa, and sets all of their values in the dict to True.
                    if i not in self.flags:
                        logging.warning(f"unrecognised flag {i}")
                    results[i] = True
            else:
                for arg in self._non_switches.values():
                    if not arg.satisfied:
                        self._cast_argument_and_set(token, arg, results)
                        break

                # There is a command-line argument, but no formal argument to store it => there is an error
                else:
                    logging.error(f"no remaining arguments in which to store '{token}'")
                    raise SystemExit(1)
        
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
                logging.error(f"value {token} cannot be converted to type int")
                raise SystemExit(1)
            else:
                return int(token)
        else:
            # Attempt to cast to whatever other type the argument may represent
            try:
                cast_value = arg_type(token)
                return cast_value
            except ValueError:
                logging.error(f"argument {argument.name} requires arguments of type {arg_type}, but received unconvertible argument {token}")
                raise SystemExit(1)

    def _set_argument_value(self, results_dict: dict, value: Any, arg: CLIArgument) -> None:
        if arg.nargs == 1:
            results_dict[arg.name] = value
        elif results_dict.get(arg.name):
            results_dict[arg.name].append(value)
        else:
            results_dict[arg.name] = [value]
        arg.current_args += 1

    def _cast_argument_and_set(self, token: str, arg: CLIArgument, results_dict: dict):
        cast_token = self._cast_to_desired_type(token, arg)
        self._set_argument_value(results_dict, cast_token, arg)

    def _post_parsing_check(self):
        for argument in self.arguments.values():
            if not argument.satisfied:
                logging.warning(f"argument did not receive enough arguments: {argument.name}")

    @classmethod
    def add_argument(cls, name, arg: CLIArgument) -> None:
        """Adds a named argument to the command line parser.
            It is stored in the parser under `name`. """
        cls.arguments[name] = arg

    @classmethod
    def add_flag(cls, name, flag: CLIFlag) -> None:
        """Adds a flag to the command line parser.
            If the given flag is set in the command,
            its value will be `True` when parsed and False if not."""
        cls.flags[name] = flag

    def __getitem__(self, key) -> Any:
        """Simply allows user to type `parser["help"] instead of parser.get("help"), etc.`"""
        if key in self._results:
            return self._results[key]
        else:
            logging.error(f"logger {self.__class__.__name__} does not have parameter {key}")
            raise SystemExit(1)

    def __repr__(self) -> str:
        details = f"Command line parser {self.__class__.__name__}:\n\tArguments:"

        if self.arguments:
            for name, argument in self.arguments.items():
                details += f"\n\t\t--{argument.name} (nargs: {argument.nargs}"
                if argument.switch:
                    details += ", switch"
                details += f")\t{argument.help_str if argument.help_str else ''}\tResults: {self._get_result_if_present(name)}"
        else:
            details += "\n\t\t(None)"

        details += "\n\tFlags:"

        if self.flags:
            for name, flag in self.flags.items():
                prefixed_name = ("-" if len(flag.name) == 1 else "--") + flag.name
                details += f"\n\t\t{prefixed_name}\t{flag.help_str}\tStatus: {self._get_result_if_present(name)}"
        else:
            details += "\n\t\t(None)"

        return details

    def _get_result_if_present(self, param_name: str) -> str:
        """Returns the value of the formal argument stored in the parser.
        If the parser has not received input to parse yet, then it returns
        [not parsed] for the given field."""
        return self._results.get(param_name, "[not parsed]")


@dataclass
class CLIProperty:
    name: str = field(init=False, default=None)

@dataclass
class CLIArgument(CLIProperty):
    arg_type: type
    nargs: int = 1
    switch: bool = field(default_factory=bool)  # If this is True, it must be used with a hyphen or two preceding its name, e.g. `program.py --number-of-args 2` instead of `program.py 2`. 
    current_args: int = field(default=0, init=False)  # Used for when arguments are being parsed; indicates the number of args this Argument type has consumed already.
    help_str: str = field(default=None)

    @property
    def satisfied(self) -> bool:
        return self.current_args >= self.nargs

@dataclass
class CLIFlag(CLIProperty):
    """Effectively a synonym for 'bool'; if this is a type hint given in the
        argument class of the `parser` decorator, then the result of the parsing
        will be true if the flag was set by the user and false otherwise.
        A flag on the command-line is prefixed by one - (hyphen-minus character), e.g. `-o`."""
    help_str: str = field(default=None)

def parser(cls: CLIParser):
    """This is a decorator, which acts upon a class with some type annotations, as seen below:
        class TestCLIParser(CLIParser):
            help: CLIFlag("help")
            n: CLIArgument("n", arg_type=int, nargs=1, switch=True)
            data: CLIArgument("data", arg_type=int, nargs=4)
            ...
        etc.; the result is a parser class which has various types of argument added to it."""

    def _create_args(cls: CLIParser):
        """Use the annotations in the class body to generate a command-line parser class."""
        cls_annotations = cls.__dict__.get('__annotations__', {})
        for key, value in cls_annotations.items():
            if type(value) is str:
                # We are using "from __future__ import annotations", so values appear as strings rather than CLIArgument objects, etc.
                value = eval(value)
            value.name = key
            if isinstance(value, CLIArgument):
                cls.add_argument(key, value)
            elif isinstance(value, CLIFlag):
                cls.add_flag(key, value)
        return cls
        

    def wrap(cls):
        return _create_args(cls)
    
    return wrap(cls)