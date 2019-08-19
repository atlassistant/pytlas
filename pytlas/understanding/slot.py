class SlotValue:
  """Represents a single slot value.

  This class adds some utility methods to ease the process when working with skills.

  """
  
  def __init__(self, raw_value, **meta):
    self.value = raw_value
    self.meta = meta

  def __str__(self):
    if isinstance(self.value, tuple):
      return ', '.join(str(v) for v in self.value)

    return str(self.value)

class SlotValues(list):
  """Represents a list of SlotValue.

  It exposes some utility methods used to ease the process of developing skills.

  """

  def __init__(self, iterable=[]):
    # Force iterable
    if not isinstance(iterable, list):
      iterable = [iterable]

    # Convert every item to SlotValue
    super(SlotValues, self).__init__([v if isinstance(v, SlotValue) else SlotValue(v) for v in iterable])

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

class UnitValue:
  """Basic class to represents a value which is in a relative unit format in a slot,
  such as a temperature or a currency.

  It also override common comparison and arithmetic operators to make it easier.

  """

  def __init__(self, value, unit):
    # Maybe we should use decimal instead :/
    self.value = value
    self.unit = unit

  def __str__(self):
    return '%.2g%s' % (self.value, self.unit)

  def __get_other_value(self, other):
    if isinstance(other, UnitValue):
      if other.unit != self.unit:
        raise ArithmeticError('Unit are not the same!')

      return other.value
    
    return other

  def __add__(self, other):
    return UnitValue(self.value + self.__get_other_value(other), self.unit)

  def __sub__(self, other):
    return UnitValue(self.value - self.__get_other_value(other), self.unit)

  def __mul__(self, other):
    return UnitValue(self.value * self.__get_other_value(other), self.unit)

  def __truediv__(self, other):
    return UnitValue(self.value / self.__get_other_value(other), self.unit)

  def __eq__(self, other):
    try:
      return self.value == self.__get_other_value(other)
    except ArithmeticError:
      return False

  def __ne__(self, other):
    try:
      return self.value != self.__get_other_value(other)
    except ArithmeticError:
      return False

  def __lt__(self, other):
    try:
      return self.value < self.__get_other_value(other)
    except ArithmeticError:
      return False

  def __le__(self, other):
    try:
      return self.value <= self.__get_other_value(other)
    except ArithmeticError:
      return False

  def __gt__(self, other):
    try:
      return self.value > self.__get_other_value(other)
    except ArithmeticError:
      return False

  def __ge__(self, other):
    try:
      return self.value >= self.__get_other_value(other)
    except ArithmeticError:
      return False