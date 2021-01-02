import random
import discord
from commands import Command
from utils.BattleManager import BattleManager

class Defense(Command):
  def __init__(self, command, config):
    super().__init__(command, config)

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