from colorlog import ColoredFormatter, escape_codes
import re, logging

class CustomFormatter(ColoredFormatter): # pragma: no cover
  """Custom formatter used to highlight every words wrapped in quotes.
  """

  def __init__(self):
    super(CustomFormatter, self).__init__('%(log_color)s%(levelname)s%(reset)s\t%(name)s\t%(reset)s%(message)s', 
    log_colors={
      'DEBUG': 'green',
      'INFO': 'cyan',
      'WARNING': 'yellow',
      'ERROR': 'red',
    })

    self._pattern = re.compile('"(.*?)"')

  def format(self, record):
    msg = super(CustomFormatter, self).format(record)

    return self._pattern.sub(r'%s\1%s' % (escape_codes['cyan'], escape_codes['reset']), msg) + escape_codes['reset']

def install_logs(verbose, debug=False): # pragma: no cover
  """Install a custom colored formatter in the root logger.

  Args:
    verbose (bool): Verbose output?
    debug (bool): Debug output?

  """

  log = logging.getLogger()
  formatter = CustomFormatter()
  stream = logging.StreamHandler()
  stream.setLevel(logging.DEBUG)
  stream.setFormatter(formatter)

  log.addHandler(stream)
  log.setLevel(logging.DEBUG if debug else logging.INFO if verbose else logging.WARNING)