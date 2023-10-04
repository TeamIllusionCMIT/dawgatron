from src.bot import DawgtaviousVandross
from os import environ

dawg = DawgtaviousVandross(
    token=environ.get("TOKEN"), redis_url=environ.get("REDIS_URL")
)

dawg.load_extension("src.commands")
dawg.load_extension("jishaku")
print("[i] commands loaded")

dawg.run()
