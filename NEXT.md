Coming in version v2.2.0
===

- ✨ Added `PYTLAS_LOAD_LANGUAGES` environment variable to prevent unneeded resources to be loaded. If not set, all skill resources will be loaded for all languages so it may take some unused memory space when you already know for which language(s) you want to use pytlas.
- ✨ Added `SlotValue.value_as_date` method to easily retrieved a parsed `datetime` value for a slot.