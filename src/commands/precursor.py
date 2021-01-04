from .command import Command
from utils.battlemanager import BattleManager

class Precursor(Command):
  command_type = 'Precursor'

  def __init__(self, command, config, bot_client):
    super().__init__(command, config, bot_client)

  async def run_command(self, message, attack):
    new_message = await super(Prec, self).run_command(message)
    if new_message is None:
      return

    battle_manager = BattleManager.get_instance()
    await battle_manager.setup_listener(attack, message.author, message.mentions, new_message)
