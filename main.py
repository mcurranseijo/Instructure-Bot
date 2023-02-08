from secret import discord_token
from interactions.ext.wait_for import wait_for, setup

"""These lines import the needed libraries, you'll also need to setup your requirements.txt for this (see readme)"""
import interactions


"""This is where you should put your bot token, the instructions for generating that can be found in the readme file"""
bot = interactions.Client(token=discord_token)
setup(bot)


"""This is where you will add the additional cogs, you will need to add them as cogs.filename and they should be placed in the cogs folder.
Each time you add a final cog you should add it here so it will autoload on restart. For testing you can use the load cog command."""

extensions = [
    'cogs.canvas_cog'  # Same name as it would be if you were importing it
]

"""You won't need to touch this, this just makes sure this is the proper file"""
for extension in extensions:
    bot.load(extension)

bot.start()




