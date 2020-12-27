# skybot.py

import discord
import re
import signal
import asyncio
import random
import yaml
from os import getenv, listdir
from os.path import join, isfile
from dotenv import load_dotenv

load_dotenv()

TOKEN = getenv('DISCORD_TOKEN')

client = discord.Client()

class SkyClient(discord.Client):
    def __init__(self):
      super().__init__()
      
      self.guild_id = getenv('GUILD_ID')
      self.contributor_role_id = getenv('CONTRIBUTOR_ROLE_ID')

      templates = self.load_yaml()
      gifs = self.scan_gifs()
      self.commands = self.setup_commands(templates, gifs)

      print(f'Started with the following commands: {self.commands}')
    
    def setup_commands(self, templates, gifs):
      commands = {}
      for command in templates:
        if 'single' not in templates[command]:
          raise Exception(f'Invalid configuration {command} has no single template defined')

        if 'mentions' in templates[command]:
          mentions = templates[command]['mentions']
        else:
          mentions = templates[command]['single']
        
        commands[command] = {
          "mentions": mentions,
          "single": templates[command]['single'],
          "prefix": command
        }

        if command in gifs:
          commands[command]['gifs'] = gifs[command]
        
        if 'aliases' in templates[command]:
          for alias in templates[command]['aliases']:
            commands[alias] = {
              "mentions": commands[command]['mentions'],
              "single": commands[command]['single'],
              "gifs": commands[command]['gifs'],
              "prefix": command
            }
      return commands
        
    def scan_gifs(self):
      files = [f for f in listdir('./gifs') if isfile(join('./gifs/', f))]
      gifs = {}
      for filename in files:
        parts = filename.split('_')
        command = parts[0]
        if command not in gifs:
          gifs[command] = 0
        else:
          gifs[command] = gifs[command] + 1
      return gifs

    async def stop(self):
      print(f'{self.user} is disconnecting from Discord')
      await self.change_presence(status=discord.Status.offline)
      await self.close()

    def load_yaml(self):
      with open('./templates.yml') as file:
        return yaml.safe_load(file)
    
    def concatenate_mentions(self, message):
      str = ''
      for m in message.mentions:
        if message.mentions.index(m) < (len(message.mentions)-1):
          str = str + f'{m.mention}, '
        else:
          str = str + f'and {m.mention}'
      return str

    def parse_template(self, command, message):
      if len(message.mentions) == 1:
        choice = random.choice(self.commands[command]['mentions'])
        str = choice.replace('{{mention}}',message.mentions[0].mention).replace('{{mentions}}',message.mentions[0].mention)
      elif len(message.mentions) > 1:
        mention_list = self.concatenate_mentions(message)
        str = random.choice(self.commands[command]['mentions']).replace('{{mention}}',message.mentions[0].mention).replace('{{mentions}}', mention_list)
      else:
        str = random.choice(self.commands[command]['single'])
      str = str.replace('{{author}}',message.author.mention)
      return str
    
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
        if message.author == self.user:
            return
        
        if re.search('michael|mike', message.author.display_name, re.I):
          await self.send_michael(message)
          return

        if not re.match('^skybot',message.content, re.I):
          return

        message_parts = message.content.split()

        if len(message_parts) < 2:
          await message.channel.send(f'{message.author.mention} You rang?')
          return

        command = message_parts[1].lower()
        special = self.special_command(message)

        if special is not None:
          await getattr(self, special)(message)
          return
        
        if command not in self.commands:
          await message.channel.send(f'{message.author.mention} I\'m not quite sure how to do that.')
          return
        
        try:
          img_num = int(message_parts[len(message_parts)-1])
        except:
          img_num = random.randint(0, self.commands[command]['gifs'])
        
        if img_num > self.commands[command]['gifs']:
          await message.channel.send(f'{message.author.mention} You\'ve specified an invalid gif.')
          return

        img_title = self.parse_template(command, message)
        
        await message.delete()
        await self.send_image(message.channel, img_title, f'./gifs/{self.commands[command]["prefix"]}_{img_num}.gif')

    async def send_image(self, channel, title, filename):
      await channel.send(title, file=discord.File(filename));
        
client = SkyClient()
client.run(TOKEN)

