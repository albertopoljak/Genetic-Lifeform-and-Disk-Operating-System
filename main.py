from discord.ext import commands
from utils.logger import Logger

logger = Logger().logger
glados_cores = ["cogs.angry_core"]
bot = commands.Bot(command_prefix="!")
bot.logger = logger


@bot.event
async def on_ready():
    logger.info("---------------bot-ready---------------")
    logger.info("Hello and, again, welcome to the Aperture Science computer-aided enrichment center.")


if __name__ == "__main__":
    for extension in glados_cores:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = f"{type(e).__name__}: {e}"
            logger.info(f"{exc} Failed to load extension {extension}")

bot.run(YOUR_TOKEN_HERE)
