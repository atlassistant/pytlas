from .slot import SlotValues

class Intent:
  """Represents a single intent with multiple slot values attached to it.
  """
  
  def __init__(self, name, **kwargs):
    self.name = name
    self.slots = { k: SlotValues(v) for (k, v) in kwargs.items() }

  def slot(self, slot_name):
    """Retrieve slot values for the given slot name.

    Args:
      slot_name (str): Name of the slot
    
    Returns:
      SlotValues: Parsed values for the slot

    """

    return self.slots.get(slot_name, SlotValues())

  def update_slots(self, **kwargs):
    self.slots.update({ k: SlotValues(v) for (k, v) in kwargs.items() })

  def __str__(self):
    return '"%s" with %s slot(s): %s' % (self.name, len(self.slots), ', '.join(self.slots.keys()))