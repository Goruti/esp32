# Hardware Mapping
#PORT_PIN_MAPPING = {
#    "A": {"pin_sensor": 39, "pin_pump": 25, "dry_value": 3350, "water_value": 1200},
#    "B": {"pin_sensor": 34, "pin_pump": 23, "dry_value": 3400, "water_value": 1200},
#    "C": {"pin_sensor": 35, "pin_pump": 22, "dry_value": 3100, "water_value": 600},
#    "D": {"pin_sensor": 32, "pin_pump": 21, "dry_value": 3150, "water_value": 550},
#    "E": {"pin_sensor": 33, "pin_pump": 19, "dry_value": 3300, "water_value": 1640},
#}

PORT_PIN_MAPPING = {
    "A": {"pin_sensor": 39, "pin_pump": 25, "dry_value": 3350, "water_value": 1200},
    "B": {"pin_sensor": 34, "pin_pump": 26, "dry_value": 3400, "water_value": 1200},
    "C": {"pin_sensor": 35, "pin_pump": 22, "dry_value": 3100, "water_value": 600},
    "D": {"pin_sensor": 32, "pin_pump": 21, "dry_value": 3150, "water_value": 550},
    "E": {"pin_sensor": 33, "pin_pump": 14, "dry_value": 3300, "water_value": 1640},
}
WATER_LEVEL_SENSOR_PIN = 27


# Software Configuration
TEMPLATES_DIR = "irrigation_templates"
AP_SSID = "My Awesome Irrigation System"
AP_PWD = "My@wesomeP@sword"
WEBREPL_PWD = "S@mu3l"
SD_MOUNTING = "/sd"
#DB Location
DB_DIR = "{}/db".format(SD_MOUNTING)
DB_FILENAME = "irrigation.db"
#Logs
LOG_DIR = "{}/logs".format(SD_MOUNTING)
LOG_FILENAME = "irrigation.log"


