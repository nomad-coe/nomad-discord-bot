import re
import discord
from discord.ext import commands

intents = discord.Intents.all() # need all intents (rather than default) for reading messages in all channels!
# intents.guild_messages = True
command_prefix='!'
client = discord.Client(command_prefix=command_prefix, intents=intents)
glossary_dict = {}
links_dict = {}
token = '<bot_token>'

def get_help(input_dict):
    markdown_text = "Here is the list of commands that I know:\n"

    for main_key, sub_dict in input_dict.items():
        # Add section header
        markdown_text += f"### {main_key}\n"

        # Add list of keys under the section
        for key in sub_dict.keys():
            markdown_text += f"- {key}\n"

        # Add an empty line between sections
        markdown_text += "\n"

    return markdown_text


def replace_link_prefix(response, new_prefix):
    def replace_link(match):
        if match.group(1):
            # Link with link text
            link_text = match.group(1)
            old_link = match.group(2)
        else:
            # Link without link text
            link_text = ''
            old_link = match.group(3)

        # Case 1: If the link starts with "#", add the new prefix
        if old_link.startswith('#'):
            return f'[{link_text}]({new_prefix}reference/glossary.html{old_link})'

        # Case 2: If the link starts with "../", replace "../" with the new prefix
        elif old_link.startswith('../'):
            old_link = old_link.replace('.md', '.html')
            return f'[{link_text}]({new_prefix}{old_link[3:]})'

        # If neither case matches, leave the link unchanged
        else:
            return match.group(0)

    return re.sub(r'\[([^\]]*?)\]\(([^)]*?)\)|\(([^)]*?)\)', replace_link, response)

markdown_sections_pattern = r'###\s(.*?)\n(.*?)(?=(?:###\s|\Z))'
# Get the NOMAD Docs glossary items
with open('glossary.md', 'r', encoding='utf-8') as file:
    markdown_content = file.read()
# Extract sections and their content using capturing groups
sections = re.findall(markdown_sections_pattern, markdown_content, re.DOTALL)
glossary_dict = {heading.lower().strip(): response for heading, response in sections}

# Get the link information
with open('links.md', 'r', encoding='utf-8') as file:
    markdown_content = file.read()
sections = re.findall(markdown_sections_pattern, markdown_content, re.DOTALL)
links_dict = {heading.lower().strip(): response for heading, response in sections}

# Define a command to respond to specific keywords
@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    # Ignore messages from the bot itself to prevent an infinite loop
    if message.author == client.user:
        return

    if not message.content.startswith(command_prefix):
        return

    # Process the command
    command = message.content[len(command_prefix):].lower().strip()

    if command == 'hello':
        response = "Hello! How can I help you?"
        await message.channel.send(response)
    elif command == 'help':
        response = get_help({'Glossary Terms': glossary_dict, 'Resources': links_dict})
        await message.channel.send(response)
    elif command in glossary_dict.keys():
        # Replace link prefixes dynamically
        new_prefix = 'https://nomad-lab.eu/prod/v1/staging/docs/'
        response_transformed = replace_link_prefix(glossary_dict[command], new_prefix)
        await message.channel.send(response_transformed)
    elif command in links_dict.keys():
        await message.channel.send(links_dict[command])

    # Ignore messages that do not start with the command prefix
    else:
        return

# Run the bot with your token
client.run(token)
