
import cmd
from ..version import __version__
from ..agent import Agent

class PromptClient(cmd.Cmd):
  intro = 'pytlas prompt v%s' % __version__
  prompt = '> '

  def __init__(self, interpreter):
    super(PromptClient, self).__init__()

    self._agent = Agent(interpreter, self)
  
  def ask(self, slot, text, choices):
    print (text)

  def answer(self, text, cards):
    print (text)

  def done(self):
    pass

  def do_exit(self, msg):
    return True

  def default(self, msg):
    self._agent.parse(msg)