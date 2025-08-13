import argparse
import colorlog

from functions.logging_config import logger

def parse() -> tuple[str, str, str]:
    """Lit les arguments de ligne de commande."""
    parser = argparse.ArgumentParser()

    parser.add_argument( "cable", help="nom du câble à mettre à jour")

    parser.add_argument("-r", "--raw", help="chemin des données brutes",
                        default="//nashdprdif274/SMB_DTS-DAS/DTS/RAW")

    parser.add_argument("-s", "--save", help="chemin des données traitées",
                        default="//nashdprdif274/SMB_DTS-DAS/DTS")

    parser.add_argument("-v", "--verbose", action="store_true",
                        help="augmenter la verbosité (activer le mode debug)")

    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(colorlog.DEBUG)

    return args.cable, args.raw +'/'+ args.cable, args.save +'/'+ args.cable