"""
Application Specific Checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import logging

from pyapp import checks
from pyapp.checks import Info, Critical
from pyapp.conf import Settings


@checks.register
def checks(settings: Settings, **_):
    try:
        raise NotImplementedError
    except NotImplementedError as e:
        return Critical(
            msg=f"You've not implemented the checks properly",
            hint="What do I need to change in order to avoid this checks failure?",
        )
