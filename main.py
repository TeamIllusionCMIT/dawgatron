from src.bot import DawgtaviousVandross
from os import environ

dawg = DawgtaviousVandross(token=environ.get("TOKEN"))

dawg.run()
