from sure import expect
from pytlas.training import register, training, module_trainings, get_training_data
import pytlas.settings as settings

settings.set(settings.SETTING_LANG, []) # Allow all languages to be loaded

@training ('en', 'amodule')
def en_data(): return """
%[get_forecast]
  will it rain in @[city]

@[city]
  paris
  london
"""

class TestTraining:

  def test_it_should_be_imported_with_the_decorator(self):
    expect(module_trainings).to.have.key('amodule')
    expect(module_trainings['amodule']).to.have.key('en')

    r = module_trainings['amodule']['en']()

    expect(r).to.equal("""
%[get_forecast]
  will it rain in @[city]

@[city]
  paris
  london
""")

  def test_it_should_evaluate_translations_correctly(self):

    def it_training_data(): return """
%[some_intent]
  con dati di allenamento

%[another one]
  con un altro dato

@[and_entity]
  con un certo valore
"""

    register('it', it_training_data, 'amodule')

    t = get_training_data('it')

    expect(t).to.have.key('amodule')
    expect(t['amodule']).to.equal("""
%[some_intent]
  con dati di allenamento

%[another one]
  con un altro dato

@[and_entity]
  con un certo valore
""")

  def test_it_should_be_imported_with_the_register_function(self):

    def fr_training_data(): return """
%[some_intent]
  with training data

%[another one]
  with another data

@[and_entity]
  with some value
"""

    register('fr', fr_training_data, 'amodule')

    expect(module_trainings).to.have.key('amodule')
    expect(module_trainings['amodule']).to.have.key('fr')

    r = module_trainings['amodule']['fr']()

    expect(r).to.equal("""
%[some_intent]
  with training data

%[another one]
  with another data

@[and_entity]
  with some value
""")

