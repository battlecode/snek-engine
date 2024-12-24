class GameConstants:

    SPEC_VERSION = "lol"

    # ****************************
    # ****** MAP CONSTANTS *******
    # ****************************

    MAP_MIN_HEIGHT = 20

    MAP_MAX_HEIGHT = 60

    MAP_MIN_WIDTH = 20
    
    MAP_MAX_WIDTH = 60

    MIN_RUIN_SPACING_SQUARED = 25

    # ******************************
    # ****** GAME PARAMETERS *******
    # ******************************

    GAME_DEFAULT_SEED = 6370

    GAME_MAX_NUMBER_OF_ROUNDS = 2000

    BYTECODE_LIMIT = 25000

    # The maximum length of indicator strings that a player can associate with a robot.
    INDICATOR_STRING_MAX_LENGTH = 64

    # The bytecode penalty that is imposed each time an exception is thrown.
    EXCEPTION_BYTECODE_PENALTY = 500

    # Health each robot starts with
    DEFAULT_HEALTH = 1000

    # Paint penalty for moving into enemy territory
    PENALTY_ENEMY_TERRITORY = 2

    # Paint penalty for moving into neutral territory
    PENALTY_NEUTRAL_TERRITORY = 1

    # The total number of robots a team has (both despawned or spawned).
    ROBOT_CAPACITY = 50

    # Paint capacity for soldier robots
    PAINT_CAPACITY_SOLDIER = 200

    # Paint capacity for splasher robots
    PAINT_CAPACITY_SPLASHER = 300

    # Paint capacity for mopper robots
    PAINT_CAPACITY_MOPPER = 100

    # The amount of a paint a paint tower starts with.
    INITIAL_PAINT_TOWER_PAINT = 500

    # The amount of money each team starts with.
    INITIAL_TEAM_MONEY = 1000

    # The percent of the map which a team needs to paint to win.
    PAINT_PERCENT_TO_WIN = 70

    # *****************************
    # ****** GAME MECHANICS *******
    # *****************************

    # The number of towers a player starts with.
    NUMBER_INITIAL_TOWERS = 3

    # The width and height of the patterns that robots can draw
    PATTERN_SIZE = 5

    # Maximum percent amount of paint to start cooldown
    DECREASED_MOVEMENT_THRESHOLD = 50

    # Intercept in the formula for the cooldown
    MOVEMENT_COOLDOWN_INTERCEPT = 100

    # Slope in the formula for the cooldown
    MOVEMENT_COOLDOWN_SLOPE = -2

    # The maximum distance from a robot where information can be sensed
    VISION_RADIUS_SQUARED = 20


    # The maximum distance for transferring paint from/to an ally robot or tower
    PAINT_TRANSFER_RADIUS_SQUARED = 2

    # The maximum distance from a tower for building robots
    BUILD_ROBOT_RADIUS_SQUARED = 4

    # The amount of paint depleted from enemy in a regular mopper attack
    MOPPER_ATTACK_PAINT_DEPLETION = 10

    # The amount of paint added to self in a regular mopper attack
    MOPPER_ATTACK_PAINT_ADDITION = 5

    # The amount of paint depleted from enemies in a swing mopper attack
    MOPPER_SWING_PAINT_DEPLETION = 5

    # ************************
    # ****** COOLDOWNS *******
    # ************************

    # If the amount of cooldown is at least this value, a robot cannot act.
    COOLDOWN_LIMIT = 10

    # The number of cooldown turns reduced per turn.
    COOLDOWNS_PER_TURN = 10

    # The amount added to the movement cooldown counter when moving without a flag
    MOVEMENT_COOLDOWN = 10

    # The amount added to the action cooldown counter after a tower builds a robot
    BUILD_ROBOT_COOLDOWN = 10

    # The amount added to the action cooldown counter after attacking (as a mopper for the swing attack)
    ATTACK_MOPPER_SWING_COOLDOWN = 40

    # THe amount added to the action cooldown counter after transferring paint
    PAINT_TRANSFER_COOLDOWN = 10

    # ****************************
    # ****** COMMUNICATION *******
    # ****************************

    # The maximum amount of bytes that can be encoded in a message
    MAX_MESSAGE_BYTES = 4

    # The maximum squared radius a robot can send a message to
    MESSAGE_RADIUS_SQUARED = 20

    # The maximum number of rounds a message will exist for
    MESSAGE_ROUND_DURATION = 5

    # The maximum number of messages a robot can send per turn
    MAX_MESSAGES_SENT_ROBOT = 1

    # The maximum number of messages a tower can send per turn
    MAX_MESSAGES_SENT_TOWER = 20