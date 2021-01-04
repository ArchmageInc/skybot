from .command import Command
from utils.battlemanager import BattleManager

class Attack(Command):
  command_type = 'Attack'
  defense = None
  precursor = None

  def __init__(self, command, config, bot_client):
    super().__init__(command, config, bot_client)

    if 'defense' in config:
      self.defense = config['defense']

    if 'precursor' in config:
      self.precursor = config['precursor']

  async def run_command(self, message):
    if self.precursor is not None:
      if isinstance(self.precursor, Command):
        await self.precursor.run_command(message, self)
      else:
        new_message = await super(Attack, self).run_command(message)
        if new_message is None:
          return
    else:
      battle_manager = BattleManager.get_instance()
      await battle_manager.setup_listener(self, message.author, message.mentions, new_message)
