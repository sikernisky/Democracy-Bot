"""
main.py
Teddy Siker
April 7th, 2022

Commands & authentication for Democracy Bot.
"""
import asyncio
import discord
from discord.ext import commands
import os
import logic

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(intents = intents, command_prefix='!')

@client.event
async def on_ready():
	"""
	Performs logic when the bot is 'Ready'.
	"""
	print('Ready!')

#@client.event
#async def on_command_error(ctx, error):
#  if isinstance(error, commands.MemberNotFound):
#    await ctx.send("That member does not exist.")


@client.command()
async def votekick(ctx, *, member : discord.Member = None):
  """
  Starts the VoteKick process.

  Parameter ctx: The bot context.
  Precondition: ctx is a valid bot context.

  Parameter member: The person people are voting to kick.
  Precondition: member is a valid discord.Member object.
  """
  assert isinstance(ctx, discord.ext.commands.context.Context), "Parameter ctx must be a bot context."
  assert isinstance(member, discord.member.Member), "Parameter member must be a Member object."

  channel = client.get_channel(961478681916735551)
  channel_members = channel.members
  all_members = []
  for m in channel_members:
    all_members.append(m)
  if member not in all_members:
    await ctx.send("That member is not in **no mao zone**.")
    return

  await logic.votekick(ctx, member, ctx.author, all_members, client)
  

@client.command()
async def yes(ctx):
  """
  Votes yes.

  Parameter ctx: The bot context.
  Precondition: ctx is a valid bot context.
  """

  assert isinstance(ctx, discord.ext.commands.context.Context), "Parameter ctx must be a bot context."

  if logic.VoteKick.active_votekick == None:
    await ctx.send("There is no active VoteKick. Type !votekick [user] to start one.")
    return
  kick = logic.VoteKick.active_votekick
  voter = ctx.author
  await kick.vote_yes(ctx, voter)

@client.command()
async def no(ctx):
  """
  Votes no.

  Parameter ctx: The bot context.
  Precondition: ctx is a valid bot context.
  """
  assert isinstance(ctx, discord.ext.commands.context.Context), "Parameter ctx must be a bot context."
  
  if logic.VoteKick.active_votekick == None:
    await ctx.send("There is no active VoteKick. Type !votekick [user] to start one.")
    return
  kick = logic.VoteKick.active_votekick
  voter = ctx.author
  await kick.vote_no(ctx, voter)

@client.command()
async def abstain(ctx):
  """
  Votes to abstain.

  Parameter ctx: The bot context.
  Precondition: ctx is a valid bot context.
  """
  assert isinstance(ctx, discord.ext.commands.context.Context), "Parameter ctx must be a bot context."
  
  if logic.VoteKick.active_votekick == None:
    await ctx.send("There is no active VoteKick. Type !votekick [user] to start one.")
    return
    
  kick = logic.VoteKick.active_votekick
  voter = ctx.author
  await kick.vote_abstain(ctx, voter)



client.run('OTYxNjU2NzI1NjA4NDc2Njgy.Yk8Kng.PI5sRKmTl3fMCnsQnQF8z1gq7Y8')