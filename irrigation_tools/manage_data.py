import ujson as json
import btree
import os

from ucontextlib import contextmanager
from irrigation_tools import conf


@contextmanager
def _get_db():
    """
    Context manager to return an instance of a database
    """
    try:
        db_file = open("{}/{}".format(conf.DB_DIR, conf.DB_FILENAME), 'r+b')
    except OSError:
        db_file = open("{}/{}".format(conf.DB_DIR, conf.DB_FILENAME), 'w+b')
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
                    }
        },
        "irrigation_state": {
                        "running": True
        },
        "WebRepl": {
                        "enabled": False,
                        "password": "asdas"
        },
        "smartThings": {
                        "enabled": True,
                        "st_ip": "x.x.x.x"
                        "st_port": "39500"
        }
    }
"""


def save_network(**kwargs):
    """
    Write the network config to file
    """
    _save_db_entry('network', kwargs)


def get_network_config():
    """
    Get the WiFi config. If there is none, return None.
    """
    return _get_db_entry('network')


def save_irrigation_config(**kwargs):
    """
    Save the irrigation configuration
    """
    _save_db_entry('irrigation_config', kwargs)


def read_irrigation_config():
    """
    Load the irrigation configuration
    """
    return _get_db_entry('irrigation_config')


def save_webrepl_config(**kwargs):
    """
    Save the webrepl configuration
    """
    _save_db_entry('WebRepl', kwargs)


def read_webrepl_config():
    """
    Load the webrepl configuration
    """
    return _get_db_entry('WebRepl')


def save_smartthings_config(**kwargs):
    """
    Save the SmartThings configuration
    """
    _save_db_entry('smartThings', kwargs)


def read_smartthings_config():
    """
    Load the SmartThings configuration
    """
    return _get_db_entry('smartThings')


def save_irrigation_state(**kwargs):
    """
    Save the irrigation status
    """
    _save_db_entry('irrigation_state', kwargs)


def read_irrigation_state():
    """
    Load the irrigation status
    """
    return _get_db_entry('irrigation_state')


def create_dir(directory):
    folds = directory.split("/")
    root = ""
    try:
        for fld in folds:
            if fld.strip() != "":
                if fld not in os.listdir(root):
                    root = "{}/{}".format(root, fld)
                    os.mkdir(root)
                else:
                    root = "{}/{}".format(root, fld)
    except Exception as e:
        raise e
