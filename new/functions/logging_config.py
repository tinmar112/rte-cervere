import colorlog

### CONFIGURATION DU LOGGER
# Création du logger
logger = colorlog.getLogger('shared_logger')
logger.setLevel(colorlog.WARNING)

# Empêcher la reconfiguration d'un handler déjà configuré
if not logger.handlers:
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    # Configuration du handler dans la console
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.propagate = False