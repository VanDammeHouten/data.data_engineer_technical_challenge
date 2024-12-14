"""
Application Specific Checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import logging
import pathlib
import pytest
from pyapp import checks
from pyapp.checks import Info, Critical, Error
from pyapp.conf import Settings


@checks.register
def check_tests(**kwargs):
    """Run the test suite as part of checks."""
    messages = []
    
    # Get the project root directory (where tests folder is located)
    project_root = pathlib.Path(__file__).parent.parent.parent
    test_path = project_root / "tests"
    
    try:
        # Run pytest programmatically
        result = pytest.main([str(test_path), "-v", "--no-header"])
        
        if result == 0:  # pytest.ExitCode.OK
            messages.append(Info("All tests passed successfully"))
        else:
            messages.append(Error(
                "Some tests failed",
                hint="Run 'pytest' directly for more detailed output"
            ))
    except Exception as ex:
        messages.append(Error(
            f"Failed to run tests: {str(ex)}",
            hint="Ensure pytest is installed and tests directory exists"
        ))
    
    return messages
