from dateutil.parser import parse as parseDate

class SlotValue:
  """Represents a single slot value.

  This class adds some utility methods to ease the process when working with skills.

  """
  
  def __init__(self, raw_value, **meta):
    self.value = raw_value
    self.meta = meta

  @property
  def value_as_date(self):
    """Retrieve the value casted to a datetime.

    Returns:
      datetime: The slot value as a datetime object

    """

    try:
      return parseDate(self.value) if self.value else None
    except:
      return None

  def __str__(self):
    return self.value

class SlotValues(list):
  """Represents a list of SlotValue.

  It exposes some utility methods used to ease the process of developing skills.

  """

  def __init__(self, iterable=[]):
    # Force iterable
    if type(iterable) is not list:
      iterable = [iterable]

    # Convert every item to SlotValue
    super(SlotValues, self).__init__([v if type(v) is SlotValue else SlotValue(v) for v in iterable])

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
