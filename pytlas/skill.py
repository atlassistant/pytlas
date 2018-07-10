import logging

handlers = {}

def intent(intent_name):
  def new(func):
    logging.info('Registered "%s.%s" which should handle "%s" intent' % (func.__module__, func.__name__, intent_name))

    if intent_name in handlers:
      logging.warning('"%s" has already been registered by someone else, it will be overriden by this one but you should review your skills! ' % intent_name)

    handlers[intent_name] = func

    return func
    
  return new