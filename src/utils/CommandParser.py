import re
from utils.BattleManager import BattleManager

class CommandParser():
  bot_client = None
  battle_manager = None
  special_commands = ['help', 'add']

  def __init__(self, bot_client):
    self.bot_client = bot_client
    self.battle_manager = BattleManager(bot_client)

  async def parse_message(self, message):
    if self.is_michael(message):
      self.michael_command(message)
      return

    command = self.get_skybot_command(message)
    if command is not None:
      await command.run_command(message)

  async def parse_reaction(self, reaction, user):
    await self.battle_manager.check_reaction(reaction ,user)

  def is_michael(self, message):
    return bool(re.search('michael|mike', message.author.display_name, re.I))

  def special_command(self, command_name, message):
    if command_name in self.special_commands:
      return command_name

    if re.search('what can you do', message.content, re.I):
      return 'help'

    return None

  def get_skybot_command(self, message):
    if not re.match('^skybot',message.content, re.I):
      return None

    message_parts = message.content.split()
    if len(message_parts) < 2:
      return None

    command_name = message_parts[1].lower()
    special_command = self.special_command(command_name, message)
    if special_command is not None:
      return special_command

    if command_name in self.bot_client.commands:
      return self.bot_client.commands[command_name]

  async def michael_command(message):
    title = f'{message.author.mention} just got krilled. Ouch!'
    for role in message.channel.guild.roles:
      if re.search('michael hate club', role.name, re.I) and role.mentionable:
        title = f'{role.mention} made sure {message.author.mention} got krilled. Sucker!'
        break
      
    filename = './gifs/krill_0.gif'
    await self.send_image(message.channel, title, filename)