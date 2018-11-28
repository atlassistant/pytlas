Coming next
===

- [x] Support markdown in the answer and ask `text` property and automatically add a `raw_text` property containing the text without formatting (same goes for cards properties)
- [ ] Add a setup() for skills to define skill metadata, this will be pretty useful to query available skills and their needed configurations
- [ ] Add support for **contexts** with sub intents
- [x] Add `require_input` in the `agent.done` method to indicates that a skill has done its work but the client should listen to user inputs right now (it will be useful when working with contexts)
- [x] Updated snips-nlu dependency
- [x] Add `skills` args to `fit_from_skill_data` to restrict which training data should be loaded
- [ ] Skills manager
- [ ] Remote training of the interpreter for when you have large training data and you are deploying pytlas on a small device
