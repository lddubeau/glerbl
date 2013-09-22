
class CheckBase(object):
    """
    Base class for checks.

    """

    hooks = []
    # pylint: disable=W0105
    """Git hooks to which this class applies. A list of strings."""

    def execute(self, hook):
        """
        Executes the check.

        :param hook: The name of the hook being run.
        :type hook: :class:`str`
        :returns: ``True`` if the check passed, ``False`` if not.
        :rtype: :class:`bool`

        """
        pass
