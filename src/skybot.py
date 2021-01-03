# skybot.py

import discord
import re
import signal
from utils import CommandInitializer, CommandParser
from os import getenv
from dotenv import load_dotenv

load_dotenv()

TOKEN = getenv('DISCORD_TOKEN')

client = discord.Client()

class SkyClient(discord.Client):
    __instance = None
    active_attacks = {}
    commands = {}
    command_parser = None
    
    @staticmethod
    def get_instance():
      return SkyClient.__instance

    def __init__(self):
      if SkyClient.__instance is not None:
        raise Exception("Instantating an already instantiated singleton!")
      SkyClient.__instance = self
      super().__init__()
      
      self.guild_id = getenv('GUILD_ID')
      self.contributor_role_id = getenv('CONTRIBUTOR_ROLE_ID')

      commandInitializer = CommandInitializer(self)
      self.commands = commandInitializer.commands
      self.command_parser = CommandParser(self)

      print(f'SkyBot activated with {len(self.commands)} commands')
      

    async def stop(self):
      print(f'{self.user} is disconnecting from Discord')
      await self.change_presence(status=discord.Status.offline)
      await self.close()

    
    def special_command(self, message):
      if re.search('help', message.content, re.I) or re.search('what can you do', message.content, re.I):
        return 'help'
      if message.content.split()[1] == 'add':
        return 'add'
      return None
    
    async def help(self, message):
      note = f'{message.author.mention}, you may ask me to perform the following: \n'
      for command in self.commands.keys():
        note = note + f'{command} - [0 - {self.commands[command]["gifs"]}], '
      note = note + 'plus some additional hidden items. Like the one you just asked me. This message will self destruct after 60 seconds.'
      await message.delete()
      await message.channel.send(note, delete_after=60)
    
    async def add(self, message):
      if message.guild != self.guild:
        await message.channel.send(f'{message.author.mention}, gif adding must take place in the test server: {self.guild.name}')
        return
      
      if self.contributor_role not in message.author.roles:
        await message.channel.send(f'{message.author.mention}, you do not have the appropriate role to add a gif.')
        return

      message_parts = message.content.split()
      
      if len(message_parts) < 3:
        await message.channel.send(f'{message.author.mention}, you must specify a command with which to add a gif')
        return

      if len(message.attachments) != 1:
        await message.channel.send(f'{message.author.mention}, you must attach exactly 1 gif file')
        return

      if message.attachments[0].filename[-3:] != 'gif':
        await message.channel.send(f'{message.author.mention}, the file attachment must be a gif')
        return

      command = message_parts[2]

      if command not in self.commands:
        await message.channel.send(f'{message.author.mention}, you are trying to add a file for a command I don\'t know how to perform')
        return

      if command not in self.commands:
        self.commands[command]['gifs'] = -1

      new_count = self.commands[command]['gifs'] + 1
      filename = f'./gifs/{self.commands[command]["prefix"]}_{new_count}.gif'
      await message.attachments[0].save(filename)
      self.commands[command]['gifs'] = new_count
      await message.channel.send(f'{message.author.mention}, the new gif has been added to {command}')
      print(f'{message.author.display_name} added {filename} to the {command} command')
    
    async def send_michael(self, message):
      title = f'{message.author.mention} just got krilled. Ouch!'
      for role in message.channel.guild.roles:
        if re.search('michael hate club', role.name, re.I) and role.mentionable:
          title = f'{role.mention} made sure {message.author.mention} got krilled. Sucker!'
          break
      
      filename = './gifs/krill_0.gif'
      await self.send_image(message.channel, title, filename)
  
    @client.event
    async def on_ready(self):
      for s in (signal.SIGTERM, signal.SIGINT):
        self.loop.add_signal_handler(s, lambda s=s: self.loop.create_task(self.stop()))
      print(f'{self.user} has connected to Discord')
      self.guild = await self.fetch_guild(self.guild_id)
      #self.contributor_role = self.guild.get_role(self.contributor_role_id)
      for role in self.guild.roles:
        if f'{role.id}' == f'{self.contributor_role_id}':
          self.contributor_role = role

    @client.event
    async def on_message(self, message):
      await self.command_parser.parse_message(message)
    
    @client.event
    async def on_reaction_add(self, reaction, user):
      await self.command_parser.parse_reaction(reaction, user)
      
    
        
client = SkyClient()
client.run(TOKEN)

