import random
import discord
from .command import Command
from utils.battlemanager import BattleManager

class Defense(Command):
  command_type = 'Defense'
  def __init__(self, command, config, bot_client):
    super().__init__(command, config, bot_client)

  async def run_command(self, message, author, attacker, targets=[]):
    if len(targets) > 0 and len(self.mention_response_templates) > 0:
      title = random.choice(self.mention_response_templates).replace('{{targets}}', self.create_mention_list(targets)).replace('{{target}}', author.mention).replace('{{attacker}}', attacker.mention)
    elif len(self.single_response_templates) > 0:
      title = random.choice(self.single_response_templates).replace('{{target}}', author.mention).replace('{{attacker}}', attacker.mention)
    else:
      title = f'{author.mention} dodged an attack from {attacker.mention}'

    battle_manager = BattleManager.get_instance()
    await battle_manager.defend_battle(message.id)

    if len(self.gif_files) > 0:
      image_name = random.choice(self.gif_files)
      await message.channel.send(title, file=discord.File(image_name))
    else:
      await message.channel.send(title)