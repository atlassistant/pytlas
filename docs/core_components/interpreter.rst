.. _interpreter:

Interpreter
===========

Interpreter allow pytlas to categorize user intents and to extract slots from raw text. Whatever interpreter you decide to use, it will need training data to be able to understand what's the user intent behind an input sentence.

Intent
------

An intent represents a user intention.

For example, when I say *what's the weather like?*, my intent is something as *get weather*. When I say *please tell me what's the weather like today*, it maps to the same intent *get weather*.

Slot
----

A slot is like a parameter value for a function. It represents an entity in the context of an intent.

So when I say *what's the weather like in Paris?*, my intent is *get weather* and the slot *city* should be *Paris*.