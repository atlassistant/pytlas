class Card:
  """Simple class to hold card properties which the primary way for skill to communicate
  visual data to the end user.
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
    self.text = text
    self.subhead = subhead
    self.header_link = header_link
    self.media = media

  def __str__(self):
    return '%s (%s) - %s' % (self.header, self.subhead, self.text)