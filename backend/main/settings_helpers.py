import os


def get_bool(key: str) -> bool:
    """Get boolean value from environment variable.

    Only accepts explicit 'True' or 'False' strings.

    Args:
        key: Environment variable name

    Returns:
        True if env var is 'True', False if 'False'

    Raises:
        ValueError: If env var is not set or has invalid value

    Example:
        >>> os.environ['DEBUG'] = 'True'
        >>> get_bool('DEBUG')
        True
        >>> os.environ['TESTING'] = 'False'
        >>> get_bool('TESTING')
        False
    """
    value = os.environ.get(key)
    if value is None:
        raise ValueError(f'{key} environment variable is required')
    if value == 'True':
        return True
    if value == 'False':
        return False
    raise ValueError(f'{key} must be "True" or "False", got "{value}"')
