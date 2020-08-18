import ujson as json
import btree
from ucontextlib import contextmanager


@contextmanager
def _get_db():
    """
    Context manager to return an instance of a database
    """
    try:
        db_file = open('/irrigation.db', 'r+b')
    except OSError:
        db_file = open('/irrigation.db', 'w+b')
    db = btree.open(db_file)
    yield db
    db.close()
    db_file.close()

def _get_db_entry(key, default=None, as_json=True):
    """
    Get a value out of the database

    :param key: The key to look up
    :param default: The default value if the key doesn't exist
    :param as_json: The value is stored as json, load it into a dict
    :returns: The value in teh database, or None
    """
    if isinstance(key, str):
        key = key.encode('utf8')
    with _get_db() as db:
        value = db.get(key)
    if value and as_json:
        value = json.loads(value.decode('utf8'))
    elif not value:
        value = default
    return value

def _save_db_entry(key, value):
    """
    Save a value to the database

    :param key: The key to save the data under
    :param value: The value to save, must either be a dict or a str
    """
    if isinstance(key, str):
        key = key.encode('utf8')
    if isinstance(value, str):
        value = value.encode('utf8')
    elif isinstance(value, dict):
        value = json.dumps(value).encode('utf8')
    with _get_db() as db:
        db[key] = value

"""
    DB STRUCTURE
    
    {
        'network': {
                    'ssid': yyyyy,
                    'password': xxxx
        },
        'irrigation_config': {
                    "total_pumps": 3,
                    "pump_info": {
                        1: { 
                            "moisture_threshold": 31,
                            "connected_to_port": "B"
                        },
                        2: {
                            "moisture_threshold": 23,
                            "connected_to_port": "C"
                        },
                        3: {
                            "moisture_threshold": 65,
                            "connected_to_port": "F"
                        }
                    },
                    "water_level": "good"
        },
        "WebRepl": False 
    }
"""
def get_network_config():
    """
    Get the WiFi config. If there is none, return None.
    """
    return _get_db_entry('network')


def save_network(**kwargs):
    """
    Write the network config to file
    """
    _save_db_entry('network', kwargs)


def read_irrigation_config():
    """
    Load the irrigation configuration
    """
    return _get_db_entry('irrigation_config')


def save_irrigation_config(**kwargs):
    """
    Save the irrigation configuration
    """
    _save_db_entry('irrigation_config', kwargs)


def read_webrepl_config():
    """
    Load the irrigation configuration
    """
    return _get_db_entry('WebRepl')


def save_webrepl_config(**kwargs):
    """
    Save the irrigation configuration
    """
    _save_db_entry('WebRepl', kwargs)
