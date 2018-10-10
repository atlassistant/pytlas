from sure import expect
from unittest.mock import patch, mock_open
from pytlas.training import register, training, module_trainings

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
    expect(module_trainings['amodule']['en']['intents']).to.have.length_of(1)
    expect(module_trainings['amodule']['en']['entities']).to.have.length_of(1)

  def test_it_should_be_imported_with_the_register_function_with_dict(self):
    register ('fr', """
%[some_intent]
  with training data

%[another one]
  with another data

@[and_entity]
  with some value
""", 'amodule')

    expect(module_trainings).to.have.key('amodule')
    expect(module_trainings['amodule']).to.have.key('fr')
    expect(module_trainings['amodule']['fr']['intents']).to.have.length_of(2)
    expect(module_trainings['amodule']['fr']['entities']).to.have.length_of(1)

  def test_it_should_be_imported_with_the_register_function_with_filepath(self):
    with patch('builtins.open') as mock:
      mock_open(mock, """
%[some_intent]
  with training data

%[another one]
  with another data

@[and_entity]
  with some value
""")

      with patch('pytlas.utils.get_module_path', return_value='/home/pytlas/amodule'):
        with patch('os.path.isfile', return_value=True):
          register('it', './a_path', 'amodule')

          expect(module_trainings).to.have.key('amodule')
          expect(module_trainings['amodule']).to.have.key('it')
          expect(module_trainings['amodule']['it']['intents']).to.have.length_of(2)
          expect(module_trainings['amodule']['it']['entities']).to.have.length_of(1)
