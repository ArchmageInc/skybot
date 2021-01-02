from .command import Command
from utils.battlemanager import BattleManager

class Attack(Command):
  command_type = 'Attack'
  defense = None

  def __init__(self, command, config):
    super().__init__(command, config)
    if 'defense' in config:
      self.defense = config['defense']

  async def run_command(self, message):
    new_message = await super(Attack, self).run_command(message)
    if new_message is None:
      return

    battle_manager = BattleManager.get_instance()
    await battle_manager.setup_listener(self, message.author, message.mentions, new_message)
