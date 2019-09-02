# pylint: disable=C0111,R0903

import uuid
import logging
from babel.dates import format_date, format_datetime, format_time

AGENT_SILENTED_METHODS = ['ask', 'answer', 'done', 'context']


class AgentProxy:
    """Returns an agent proxy to silent down some methods (ask, answer and done) for skills
    that has been canceled. This is easier that running in subprocess and work well.

    So a skill may launch its own async task in a thread and reply back with the agent
    when it's done and if the user has cancel the action, its reply will be silented by
    this proxy.

    """

    def __init__(self, request, agent):
        self._request = request
        self._agent = agent

    def unwrap(self):
        """Retrieve the underlying agent for this proxy. Use it with caution since the
        proxy is here to silent cancelled requests.

        Returns:
          Agent: wrapped agent for this proxy

        """
        return self._agent

    def empty_func(self, *args, **kwargs): # pragma: no cover
        pass

    def __getattr__(self, attr):
        if self._agent._is_current_request(self._request) or attr not in AGENT_SILENTED_METHODS: # pylint: disable=W0212
            return getattr(self._agent, attr)

        logging.debug('Silented "%s" call from the stub', attr)
        return self.empty_func


class Request:
    """Tiny wrapper which represents a request sent to a skill handler.
    """

    def __init__(self, agent, intent, module_translations=None):
        self.intent = intent
        """Intent associated with the request"""
        self.id = uuid.uuid4().hex # pylint: disable=C0103
        """Unique id of the request"""
        self.agent = AgentProxy(self, agent)
        """Agent proxy used to communicate back with the agent"""
        self.lang = agent.lang
        """Request language as extracted from the agent"""

        self._module_translations = module_translations or {}

    def _d(self, date, date_only=False, time_only=False, **options):
        """Helper to localize given date using the agent current language.

        Args:
          date (datetime): Date to format accordingly to the user language
          date_only (bool): Only format the date part
          time_only (bool): Only format the time part
          options (dict): Additional options such as `format` to give to Babel

        Returns:
          str: Localized string representing the date

        """
        func = format_date if date_only else format_time if time_only else format_datetime

        return func(date, locale=self.lang, **options)

    def _(self, text):
        """Gets the translated value of the given text.

        Args:
          text (str): Text to translate

        Returns:
          str: Translated text or source text if no translation has been found

        """
        return self._module_translations.get(text, text)
