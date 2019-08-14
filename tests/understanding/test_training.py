from sure import expect
from pytlas.understanding.training import global_trainings, TrainingsStore, training

class TestTraining:

  def teardown(self):
    global_trainings.reset()

  def test_it_should_register_funcs(self):
    s = TrainingsStore()

    def en_data(): return """
%[get_forecast]
  will it rain in @[city]

@[city]
  paris
  london
"""

    s.register('en', en_data, 'amodule')

    expect(s._data).to.equal({
      'amodule': {
        'en': en_data,
      },
    })

  def test_it_should_be_registered_with_the_decorator_in_the_given_store(self):
    s = TrainingsStore()

    @training ('en', store=s, package='amodule')
    def en_data(): return """
%[get_forecast]
  will it rain in @[city]

@[city]
  paris
  london
"""

    expect(s._data).to.equal({
      'amodule': {
        'en': en_data,
      },
    })
  
  def test_it_should_be_registered_with_the_decorator_in_the_global_store(self):
    @training ('en', package='amodule')
    def en_data(): return """
%[get_forecast]
  will it rain in @[city]

@[city]
  paris
  london
"""

    expect(global_trainings._data).to.equal({
      'amodule': {
        'en': en_data,
      },
    })

  def test_it_should_retrieve_trainings_for_a_given_language(self):
    s = TrainingsStore()
    s.register('it', lambda: """
%[some_intent]
  con dati di allenamento

%[another one]
  con un altro dato

@[and_entity]
  con un certo valore
""", 'amodule')
    s.register('en', lambda: """
%[some_intent]
  with training data

%[another one]
  with another data

@[and_entity]
  with some value
""", 'amodule')

    expect(s.all('it')).to.equal({
      'amodule': """
%[some_intent]
  con dati di allenamento

%[another one]
  con un altro dato

@[and_entity]
  con un certo valore
""",
    })

  def test_it_should_retrieve_trainings_for_a_particular_package(self):
    s = TrainingsStore()
    s.register('en', lambda: """
%[get_weather]
  what's the weather like
""", 'mymodule')
    s.register('en', lambda: """
%[some_intent]
  with training data

%[another one]
  with another data

@[and_entity]
  with some value
""", 'amodule')

    expect(s.get('mymodule', 'en')).to.equal("""
%[get_weather]
  what's the weather like
""")
    expect(s.get('mymodule', 'it')).to.be.none
