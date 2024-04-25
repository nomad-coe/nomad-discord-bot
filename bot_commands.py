import re
import discord
from discord.ext import commands

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_dynamic_commands(self, sections):
        for key, val in sections.items():
            async def dynamic_command(ctx, response=val):
                await ctx.send(response)

            dynamic_command.__name__ = key.lower()  # Set the command name
            self.bot.add_command(commands.command()(dynamic_command))  # Add the command

intents = discord.Intents.default() # need all intents (rather than default) for reading messages in all channels!
intents.messages = True
intents.guilds = True
command_prefix='!'
bot = commands.Bot(command_prefix=command_prefix, intents=intents)
token = '<bot_token>'

# Get the NOMAD Docs glossary items
with open('glossary.md', 'r', encoding='utf-8') as file:
    markdown_content = file.read()

# Extract sections and their content using capturing groups
sections = re.findall(r'###\s(\w+)\n(.*?)(?=(?:###\s\w+)|$)', markdown_content, re.DOTALL)
sections = {heading.lower().strip(): response for heading, response in sections}

# Create an instance of MyCog and pass the bot to it
my_cog = MyCog(bot)

# Add the cog to the bot
bot.add_cog(my_cog)

# Run the bot with your token
bot.run(token)
