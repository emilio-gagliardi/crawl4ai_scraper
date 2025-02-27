import json
import os
import sys
from typing import Any, Dict, List


def badly_formatted_function(
    x: int, y: int, z: str = 'test'
) -> Dict[str, Any]:
    """This docstring demonstrates proper formatting.

    It includes a properly capitalized summary line,
    followed by a blank line and description.
    """
    result = {'x': x, 'y': y, 'z': z}

    if x > 10:
        result['status'] = 'greater'
    else:
        result['status'] = 'lesser'

    return result


def unused_function():
    """Demonstrate proper docstring for unused function."""
    pass


if __name__ == '__main__':
    print(badly_formatted_function(15, 20, 'example'))
