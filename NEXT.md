Coming next
===

- [x] Support markdown in the answer and ask `text` property and automatically add a `raw_text` property containing the text without formatting (same goes for cards properties)
- [ ] Add a meta() for skills to define skill metadata, this will be pretty useful to query available skills and their needed configurations (need some more keys such as configs)
- [ ] Add support for **contexts** with sub intents
- [x] Add `require_input` in the `agent.done` method to indicates that a skill has done its work but the client should listen to user inputs right now (it will be useful when working with contexts)
- [x] Updated snips-nlu dependency
- [x] Add `skills` args to `fit_from_skill_data` to restrict which training data should be loaded
- [x] You can now use a `pytlas.conf` file and it will be read by the cli in the current working directory
- [ ] Introduce a `pytlas.settings` namespace which will handle all global settings used by skills. It will read settings from a configuration file and environment variables (should replace `pytlas.cli.conf`)
- [ ] Defer all loadings (training and localization) by storing only a function handler and calling it at runtime. It will make easy to add dynamic trainings at runtime (such as available rooms or devices needed in training entities)
- [ ] Skills manager (need tests!!)
- [ ] Remote training of the interpreter for when you have large training data and you are deploying pytlas on a small device
