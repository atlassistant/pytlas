class SlotValue:
  """Represents a single slot value.

  This class adds some utility methods to ease the process when working with skills.

  """
  
  def __init__(self, value, **kwargs):
    self.value = value
    self.data = kwargs

class SlotValues(list):
  """Represents a list of SlotValue.

  It exposes some utility methods used to ease the process of developing skills.

  """

  def is_empty(self):
    """Returns true if it does not have any value.

    Returns:
      bool: True if empty, false otherwise
    
    """

    return len(self) == 0
  
  def first(self):
    """Returns the first slot value if any.

    Returns:
      SlotValue: first slot value

    """

    return self[0] if not self.is_empty() else SlotValue(None)

  def last(self):
    """Returns the last slot value if any.

    Returns:
      SlotValue: last slot value

    """

    return self[len(self) - 1] if not self.is_empty() else SlotValue(None)