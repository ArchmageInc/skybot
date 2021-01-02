import yaml
from commands import Attack, Defense, Command
from os.path import join, isfile
from os import listdir

class CommandInitializer():
  gif_counts = {}
  templates = {}
  commands = {}

  _gif_directory = '../gifs'
  _attack_templates = './templates/attacks.yml'
  _emote_templates = './templates/emotes.yml'
  _defense_templates = './templates/defenses.yml'

  def __init__(self):

    gif_counts = self.scan_gifs()
    attack_commands = self.load_attacks(gif_counts)
    defense_commands = self.load_defenses(gif_counts)
    emote_commands = self.load_emotes(gif_counts)

    self.commands.update(attack_commands)
    self.commands.update(defense_commands)
    self.commands.update(emote_commands)

  def scan_gifs(self):
    files = [f for f in listdir(f'{self._gif_directory}') if isfile(join(f'{self._gif_directory}/', f))]
    gifs = {}
    for filename in files:
      parts = filename.split('_')
      command = parts[0]
      if command not in gifs:
        gifs[command] = 1
      else:
        gifs[command] = gifs[command] + 1
        
    return gifs

  def load_attacks(self, gif_counts):
    templates = self.load_template(self._attack_templates)
    commands = {}
    for command_name in templates:
      template = templates[command_name]
      config = self.standard_config(command_name, template, gif_counts)

      if 'defense' in template:
        config['defense'] = template['defense']
      else:
        config['defense'] = None

      commands[command_name] = Attack(command_name, config)
      commands.update(self.create_aliases(Attack, template, config))
    return commands

  def load_defenses(self, gif_counts):
    templates = self.load_template(self._defense_templates)
    commands = {}
    for command_name in templates:
      template = templates[command_name]
      config = self.standard_config(command_name, template, gif_counts)

      commands[command_name] = Defense(command_name, config)
      commands.update(self.create_aliases(Defense, template, config))
    return commands

  def load_emotes(self, gif_counts):
    templates = self.load_template(self._emote_templates)
    commands = {}
    for command_name in templates:
      template = templates[command_name]
      config = self.standard_config(command_name, template, gif_counts)
      commands[command_name] = Command(command_name, config)
      commands.update(self.create_aliases(Command, template, config))
    return commands

  def load_template(self, filename):
    with open(filename) as file:
      return yaml.safe_load(file)

  def standard_config(self, command_name, template, gif_counts):
    config = {}

    config['prefix'] = command_name

    if 'single' in template:
      config['single'] = template['single']
    else:
      config['single'] = []
    
    if 'mentions' in template:
      config['mentions'] = template['mentions']
    else:
      config['mentions'] = config['single']

    if command_name in gif_counts:
      config['gifs'] = gif_counts[command_name]
    else:
      config['gifs'] = 0

    return config

  def create_aliases(self, command_class, template, config):
    commands = {}
    if 'aliases' in template:
      for command_alias in template['aliases']:
        commands[command_alias] = command_class(command_alias, config)

    return commands