# pylint: disable=C0111,R0201,W0613,W0212

import cmd
import sys
from pytlas.__about__ import __version__


class Prompt(cmd.Cmd):  # pragma: no cover
    """Tiny REPL to interact with a pytlas agent.
    """

    intro = 'pytlas prompt v%s (type exit to leave)' % __version__
    prompt = '> '

    def __init__(self, agent, parse_message=None):
        super(Prompt, self).__init__()

        self._agent = agent
        self._agent.model = self
        self._exit_on_done = False

        if parse_message:
            self._exit_on_done = True
            self._agent.parse(parse_message)

    def on_done(self, require_input):
        if self._exit_on_done and not self._agent._request:
            sys.exit()

    def on_ask(self, slot, text, choices, **meta):
        print(text)

        if choices:
            for choice in choices:
                print('\t-' + choice)

    def on_answer(self, text, cards, **meta):
        print(text)

        if cards:
            for card in cards:
                print(card)

    def do_exit(self, msg):
        return True

    def default(self, line):
        self._agent.parse(line)
