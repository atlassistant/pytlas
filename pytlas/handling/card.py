from pytlas.utils import strip_format

class Card:
  
  """Simple class to hold card properties which the primary way for skill to communicate
  visual data to the end user.

  header, text, subhead support rich formatting as the agent answer/ask methods. If
  you wish to retrieve the raw values without formatting, you can use raw_header, raw_text and
  raw_subhead instead.
  
  """
  
  def __init__(self, header, text, subhead=None, header_link=None, media=None):
    """Instantiates a new card.

    Args:
      header (str): Card header
      text (str): Content text to show
      subhead (str): Subheader
      header_link (str): Optional link tied to the header
      media (str): Media tied to this card, ideally you should give a base64 string

    """
    
    self.header = header
    self.raw_header = strip_format(header)

    self.text = text
    self.raw_text = strip_format(text)

    self.subhead = subhead
    self.raw_subhead = strip_format(subhead)

    self.header_link = header_link
    self.media = media

  def __str__(self):
    return '%s (%s) - %s' % (self.raw_header, self.raw_subhead, self.raw_text)