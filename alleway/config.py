# name of the ROM folder at gym-retro/retro/data/stable/
GAME = "Alleyway-GameBoy"

# defined at gym-retro/retro/data/stable/.../metadata.json
STATE = "Level1"

SCENARIO = "./scenario_one_live.json"

# Not using more than one player
PLAYERS = 1

# If true, will wait for ENTER input between iterations
WAIT_BETWEEN_ITERATIONS = False

# NOTE: Unused on RL agents. Used for debugging simple agents
MULTIPLE_ITERATIONS = True

NUM_ITERATIONS = 1000

# > 1 print all, 1 print only finished iterations, 0 don"t print anything
VERBOSITY = 1

# log outputs in .bk2
RECORD = False

# log all info (if verbosity > 1) each amount of steps
MODULO_STEPS_TO_LOG_INFO = 1
