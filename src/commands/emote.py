from .command import Command

class Emote(Command):
  command_type = 'Emote'
  def __init__(self, command, config):
    super().__init__(command, config)