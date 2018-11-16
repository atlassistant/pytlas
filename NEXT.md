Coming next
===

- [ ] Support markdown in the answer and ask `text` property and automatically add a `raw_text` property containing the text without formatting
- [ ] Add a setup() for skills to define skill metadata, this will be pretty useful to query available skills and their needed configurations
- [ ] Add support for **contexts** with sub intents
- [x] Add `require_input` in the `agent.done` method to indicates that a skill has done its work but the client should listen to user inputs right now (it will be useful when working with contexts)
- [ ] Skills manager
- [ ] Remote training of the interpreter for when you have large training data and you are deploying pytlas on a small device