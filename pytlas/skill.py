def intent(intent_name):
  def new(func):
    print ('Registered %s.%s which should handle %s intent' % (func.__module__, func.__name__, intent_name))

    return func
    
  return new