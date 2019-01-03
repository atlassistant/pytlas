Coming next
===

- [ ] Remote training of the interpreter for when you have large training data and you are deploying pytlas on a small device
- [ ] Try to use the new [snips parsing API](https://github.com/snipsco/snips-nlu/pull/724) for parsing slots when in ask state and see if it works as expected when released
- [ ] Add `AgentMock` used for testing skills
- [x] Add `additional_lookup` property to `settings.get` which will take precedence over `os.environ`. With this modification, we can use `settings.get('a key', additional_lookup=r.agent.meta)` in skills to allow agent overriding of global settings.
- [ ] Add cli command `pytlas train` and remove the `--dry` flag
- [ ] Add cli command `pytlas parse` and remove the `--parse` arg
