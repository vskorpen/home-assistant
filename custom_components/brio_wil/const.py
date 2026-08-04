"""Constants for the BRiO WiL integration."""

DOMAIN = "brio_wil"

MANUFACTURER = "CCEI"
MODEL = "BRiO WiL"
DEFAULT_NAME = "Pool Light"

SCAN_INTERVAL_SECONDS = 30
COMMAND_REFRESH_DELAY = 2

# Mode/pattern id <-> display name, as sent/read via the device's "prcn" field.
# Ids 11-15 are not used by the device (gap ported as-is from the Node-RED flow).
MODES: dict[int, str] = {
    0: "Warm white",
    1: "White",
    2: "Blue",
    3: "Lagoon",
    4: "Cyan",
    5: "Purple",
    6: "Magenta",
    7: "Pink",
    8: "Red",
    9: "Orange",
    10: "Green",
    16: "Gradient",
    17: "Rainbow",
    18: "Parade",
    19: "Techno",
    20: "Horizon",
    21: "Hazard",
    22: "Magical",
}
MODE_NAME_TO_ID = {name: mode_id for mode_id, name in MODES.items()}

# Sequence speed id <-> display name, as sent/read via the device's "pspd" field.
SPEEDS: dict[int, str] = {0: "Slow", 1: "Medium", 2: "Fast"}
SPEED_NAME_TO_ID = {name: speed_id for speed_id, name in SPEEDS.items()}

# Brightness level (0-3) <-> a representative HA 0-255 brightness value. 0 is
# intentionally never used so a dim light is never mistaken for an off one.
BRIGHTNESS_LEVEL_TO_HA: dict[int, int] = {0: 64, 1: 128, 2: 191, 3: 255}
