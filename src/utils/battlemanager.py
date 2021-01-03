import asyncio
import discord
from datetime import datetime

class BattleManager():
  __instance = None
  bot_client = None
  active_battles = {}
  active_attacks = {}

  active_timeout = 60
  icons = {
    "win_battle": '🏅',
    "defend": '🛡️',
    "wait": '⏲'
  }

  @staticmethod
  def get_instance():
    return BattleManager.__instance

  def __init__(self, bot_client):
    if BattleManager.__instance is not None:
      raise Exception("Instantating an already instantiated singleton!")
    self.bot_client = bot_client
    BattleManager.__instance = self
    bot_client.loop.create_task(self.manage_active_attacks())

  async def setup_listener(self, command, attacker, targets, watch_message):
    if not command.command_type == 'Attack':
      return
    if len(targets) <= 0:
      return

    self.active_attacks[watch_message.id] = {
      "message": watch_message,
      "attacker": attacker,
      "targets": targets,
      "command": command,
      "time": datetime.now()
    }

    await watch_message.add_reaction(self.icons['wait'])

  async def win_battle(self, id):
    if id not in self.active_attacks:
      return
    try:
      await self.active_attacks[id]['message'].clear_reaction(self.icons['wait'])
      await self.active_attacks[id]['message'].add_reaction(self.icons['win_battle'])
    except (discord.HTTPException, discord.NotFound):
      print('Tried to update winning battle message, but it was deleted.')
    finally:
      del self.active_attacks[id]

  async def defend_battle(self, id):
    if id not in self.active_attacks:
      return
    try:
      await self.active_attacks[id]['message'].delete()
    except (discord.HTTPException, discord.NotFound):
      print('Tried to remove a defended attack, but it was already gone.')
    finally:
      del self.active_attacks[id]

  async def manage_active_attacks(self):
    while True:
      battles_won = []
      for id in self.active_attacks:
        active_attack = self.active_attacks[id]
        within_window = (datetime.now() - active_attack['time']).total_seconds() < self.active_timeout
        if not within_window:
          battles_won.append(id)
      for id in battles_won:
        await self.win_battle(id)
      await asyncio.sleep(10)

  async def check_reaction(self, reaction, user):
    message = reaction.message
    message_id = message.id
    if message_id not in self.active_attacks:
        return

    active_attack = self.active_attacks[message_id]
    within_window = (datetime.now() - active_attack['time']).total_seconds() < self.active_timeout

    if not within_window:
      await self.win_battle(message_id)
      return

    is_defense = reaction.emoji == self.icons['defend']

    if not is_defense:
      return

    is_by_target = user in active_attack['targets']
    if not is_by_target:
      try:
        await message.remove_reaction(reaction, user)
      except (discord.HTTPException, discord.NotFound):
        print('Tried to remove an invalid reaction from an attack message, but it was deleted')
      finally:  
        await message.channel.send(f'{user.mention}, you cannot defend against an attack of which you are not a target.', delete_after=10)
      

    attacker = active_attack['attacker']
    command = active_attack['command']
    targets = active_attack['targets']
    attack_message = active_attack['message']
    if command.defense not in self.bot_client.commands:
      await message.channel.send(f'{user.mention} dodged an attack from {attacker.mention}')
    else:
      await self.bot_client.commands[command.defense].run_command(attack_message, user, attacker, targets)
    await self.defend_battle(message_id)