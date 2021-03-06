# pylint: disable=missing-module-docstring

from typing import List
from unittest.mock import MagicMock
from pytlas.testing.attrdict import AttrDict


class ModelMock(MagicMock):
    """Represents a particular mocking object used to make assertions easier on the
    agent model.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._args_map = []

    def has_arguments_mapping(self, mapping: List[str]) -> 'ModelMock':
        """Adds arguments names to this instance to be able to test against them. Maybe
        there is a better way to handle it, I don't know yet.

        Args:
          mapping (list of str): List of keys in the order of arguments

        """
        self._args_map = mapping
        return self

    def get_call(self, number=-1) -> AttrDict:
        """Retrieve call args for the given call number. With this tiny method, you can
        call a mock multiple times and assert against a specific one.

        By default, it will returns the last call.

        It will returns an AttrDict which contains each argument name and their respective value
        so order is not an issue.

        Args:
          number (int): Call order

        Returns:
          AttrDict: AttrDict with argument names as keys

        """
        try:
            call_args = self.call_args_list[number][0]
        except IndexError:
            raise AssertionError(
                'Mock has been called less than %d times!' % number)

        result = AttrDict()

        for (i, arg) in enumerate(call_args):
            try:
                result[self._args_map[i]] = arg
            except IndexError:
                pass

        for (k, v) in self.call_args_list[number][1].items(): # pylint: disable=invalid-name
            result[k] = v

        return result


class AgentModelMock: # pylint: disable=too-few-public-methods
    """Represents an agent model targeted at testing skills easily.
    """

    def __init__(self) -> None:
        self.on_answer = ModelMock().has_arguments_mapping(['text', 'cards'])
        self.on_ask = ModelMock().has_arguments_mapping(
            ['slot', 'text', 'choices'])
        self.on_done = ModelMock().has_arguments_mapping(['require_input'])
        self.on_context = ModelMock().has_arguments_mapping(['context_name'])
        self.on_thinking = ModelMock().has_arguments_mapping([])

    def reset(self) -> None:
        """Resets all magic mocks calls. Basically, you should call it in your test
        setup method to make sure each instance starts from a fresh state.
        """
        self.on_answer.reset_mock()
        self.on_ask.reset_mock()
        self.on_done.reset_mock()
        self.on_context.reset_mock()
        self.on_thinking.reset_mock()
