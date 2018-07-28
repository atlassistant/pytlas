class Card:
  """Simple class to hold card properties.
  """
  
  def __init__(self, header, text, subhead=None, header_link=None, media=None):
    """Instantiates a new card.

    Args:
      header (str): Card header
      text (str): Content text to show
      subhead (str): Subheader
      header_link (str): Optional link tied to the header
      media (str): Media tied to this card

    """
    
    self.header = header
    self.text = text
    self.subhead = subhead
    self.header_link = header_link
    self.media = media