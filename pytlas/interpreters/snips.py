from .interpreter import Interpreter

class SnipsInterpreter(Interpreter):

  def __init__(self, training_filepath, output_directory):
    """Instantiates a new Snips interpreter.

    Args:
      training_filepath (str): Path to the training file
      output_directory (str): Directory where to put computed file and checksum

    """

    super(SnipsInterpreter, self).__init__(training_filepath)