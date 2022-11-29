import os
import dotenv
import discord
import logging
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

dotenv.load_dotenv()
# bot = commands.Bot(
#     command_prefix=config['prefix'],
#     owner_id=config['owner_id']
#     )
bot = commands.Bot()

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')

bot.logger = logging.getLogger(__name__)


def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            print(f"Loading {file}")
            bot.load_extension(f"cogs.{file[:-3]}")
            print(f"Loaded {file}")


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


@bot.event
async def on_guild_join(guild):
    print(f'Joined {guild.name}!')


def main():
    load_cogs()
    print("Running bot...")
    bot.run(os.getenv('TOKEN'))


main()
