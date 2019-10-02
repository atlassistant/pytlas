from pytlas import training, translations, intent, meta

# Hey there o/
# Glad you're taking some times to make a skill for the pytlas assistant!
# Here is all you have to know to make your own skills, let's go!

# Start by defining training data used to trigger your skill.
# Here we are defining the intents with some training data.
# In english:


@training('en')
def en_training(): return """
%[start_vacuum_cleaner]
    start ~[vacuum_cleaner]
    would you like start ~[vacuum_cleaner] please

%[stop_vacuum_cleaner]
    stop ~[vacuum_cleaner]
    would you like stop ~[vacuum_cleaner] please

~[vacuum_cleaner]
    vacuum cleaner
    vacuum
    vacuuming
    hoover
    hoovering
    aspirator
"""

# And in other supported languages, we define the same intents with
# appropriate data:


@training('fr')
def fr_training(): return """
%[start_vacuum_cleaner]
    passe l'aspirateur
    peux-tu passer l'aspirateur
    démarrage de l'aspirateur ~[stp]

%[stop_vacuum_cleaner]
    arrête l'aspirateur
    arrête de passer l'aspirateur
    termine d'aspirer
    peux arrête d'aspirer

~[stp]
    s'il te plait
    stp
"""

# Let's define some metadata for this skill. This step is optional but enables
# pytlas to list loaded skills with more informations:


@meta()
def template_skill_meta(_): return {
    'name': _('vacuum'),
    'description': _('Home automation sample skill'),
    'author': 'atlassistant',
    'version': '1.0.0',
    'homepage': 'https://github.com/atlassistant/pytlas.git',
}

# Now, adds some translations for supported languages:


@translations('fr')
def fr_translations(): return {
    "vacuum": "Aspirateur",
    "Home automation sample skill": "Skill d'exemple pour la domotique",
    "Vacuuming started": "L'aspiration a débutée",
    "End of vacuuming, return to dock": "Fin de l'aspiration, retour à la base"
}


@intent('start_vacuum_cleaner')
def on_start_vacuum_cleaner(req):

    # put your logic here

    req.agent.answer(req._('Vacuuming started'),
                     skill="vacuum", action="start")

    return req.agent.done()


@intent('stop_vacuum_cleaner')
def on_stop_vacuum_cleaner(req):

    # put your logic here

    req.agent.answer(req._('End of vacuuming, return to dock'),
                     skill="vacuum", action="stop")

    return req.agent.done()
