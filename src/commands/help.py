from . import Command, Attack, Defense, Emote

class Help(Command):
  command_type = 'Special'
  bot_client = None
  __help_message = None

  def __init__(self, bot_client):
    self.bot_client = bot_client

  @property
  def help_message(self):
    if self.__help_message is None:
      self.__help_message = self.build_help_message()
    return self.__help_message

  async def run_command(self, message):
    await message.delete()
    await message.channel.send(self.help_message.replace('{{author}}', message.author.mention), delete_after=60)

  def build_help_message(self):
    note = '{{author}}, Here are the list of commands:\n'
    note = note + self.get_emotes_list()
    note = note + self.get_attack_list()
    #note = note + self.get_defense_list()

    note = note + self.get_special_list()

    #note = note + self.get_footer()

    return note

  def get_footer(self):
    note = '\n\n'
    note = note + '* [] - optional argument \n'
    note = note + '* <> - required argument \n'
    return note

  def get_special_list(self):
    note = f'**===OTHER COMMANDS===**\n'
    note = note + f'`help` - You seemed to have figured that one out already. \n'
    note = note + f'* There are some other hidden commands.'

    return note

  def get_emotes_list(self):
    note = f'**===EMOTES===**\n'
    for command_name in self.bot_client.commands:
      command = self.bot_client.commands[command_name]
      if isinstance(command, Emote):
        note = note + f'`{command_name}` '
    return note + '\n'

  def get_attack_list(self):
    note = f'**===ATTACKS==**\n'
    for command_name in self.bot_client.commands:
      command = self.bot_client.commands[command_name]
      if isinstance(command, Attack):
        note = note + f'`{command_name}` '
    return note + '\n'

  def get_defense_list(self):
    note = f'**===DEFENSES==**\n'
    for command_name in self.bot_client.commands:
      command = self.bot_client.commands[command_name]
      if isinstance(command, Defense):
        note = note + f'`{command_name}` \n'
    return note + '\n'