from .slot import SlotValues

class Intent:
  """Represents a single intent with multiple slot values attached to it.
  """
  
  def __init__(self, name, **kwargs):
    self.name = name
    self.slots = {}
    self.meta = {}
    self.update_slots(**kwargs)

  def slot(self, slot_name):
    """Retrieve slot values for the given slot name.

    Args:
      slot_name (str): Name of the slot
    
    Returns:
      SlotValues: Parsed values for the slot

    """

    return self.slots.get(slot_name, SlotValues())

  def update_slots(self, **kwargs):
    """Update the intent slots with given keyword args.

    Values will be wrapped in a SlotValues object for easier use.

    """

    self.slots.update({ k: SlotValues(v) for (k, v) in kwargs.items() })

  def __str__(self):
    return '"%s" (%s)' % (self.name, ', '.join([ '"%s"=%s' % (k, ['"%s"' % vv.value for vv in v]) for k, v in self.slots.items() ]))