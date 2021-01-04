import random
import discord

class Command():
  _gif_directory = '../gifs'
  command_type = 'Default'
  bot_client = None
  command = None
  prefix = None
  gif_files = []
  mention_response_templates = []
  single_response_templates = []

  def __init__(self, command, config, bot_client):
    self.bot_client = bot_client
    self.command = command
    self.prefix = config['prefix']
    self.gif_files = self.compile_gifs(config)
    self.mention_response_templates = self.compile_mention_templates(config)
    self.single_response_templates = self.compile_single_templates(config)

  def compile_gifs(self, config):
    file_names = []
    for i in range(config['gifs']):
      file_names.append(f'{self._gif_directory}/{self.prefix}_{i}.gif')
    return file_names

  def compile_mention_templates(self, config):
    templates = []
    for template in config['mentions']:
      templates.append(template)
    return templates

  def compile_single_templates(self, config):
    templates = []
    for template in config['single']:
      templates.append(template)
    return templates

  def parse_template(self, template, author, mentions):
    output = template.replace('{{author}}', author.mention)

    if len(mentions) == 1:
      output = output.replace('{{mention}}', mentions[0].mention).replace('{{mentions}}', mentions[0].mention)
    
    if len(mentions) > 1:
      output = output.replace('{{mention}}', mentions[0].mention).replace('{{mentions}}', self.create_mention_list(mentions))
    
    return output

  def create_mention_list(self, mentions):
    str = ''
    if len(mentions) == 1:
      return f'{mentions[0].mention}'
      
    for m in mentions:
      if mentions.index(m) < (len(mentions)-1):
        str = str + f'{m.mention}, '
      else:
        str = str + f'and {m.mention}'
    return str

  async def send_invalid_gif(self, message):
    await message.channel.send(f'{message.author.mention} You\'ve specified an invalid gif.')

  def get_title(self, author, mentions=[]):
    if len(mentions) > 0:
      return self.parse_template(random.choice(self.mention_response_templates), author, mentions)
    return self.parse_template(random.choice(self.single_response_templates), author, mentions)

  def get_image(self, message=None):
    if message is not None:
      message_parts = message.content.lower().split()
    else:
      message_parts = []
    try:
      img_name = f'{self._gif_directory}/{self.prefix}_{int(message_parts[len(message_parts)-1])}.gif'
    except ValueError:
      img_name = random.choice(self.gif_files)

    if img_name not in self.gif_files:
      raise FileNotFoundError(f'{img_name} could not be found')

    return img_name

  async def run_command(self, message):
    try:
      img_name = self.get_image(message)
    except FileNotFoundError:
      await self.send_invalid_gif(message)
      return

    title = self.get_title(message.author, message.mentions)
    await message.delete()
    new_message = await message.channel.send(title, file=discord.File(f'{img_name}'))
    return new_message
