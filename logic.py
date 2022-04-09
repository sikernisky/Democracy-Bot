"""
logic.py
Teddy Siker
April 7th, 2022

All logic used for the VoteKick process.
"""
import asyncio
import discord
import discord.ext


class VoteKick(object):
  """
  A class to represent a VoteKick.

  An instance represents one occurance of the VoteKick process.

  Class Attributes:
    - active_votekick [VoteKick] : the current, active VoteKick.
    - in_timeout [list of member] : all members in timeout

  Instance Attributes:
    - voters [{member; string} dictionary] : all members who can vote in this    
      VoteKick (key) and their vote, empty string if no vote yet (value)
    - votes_needed [int] : number of members who need to vote yes
    - defendant [member] : person who members are voting to kick
    - yes_votes [int] : number of people who voted yes
    - no_votes [int] : number of poeple who voted no
    - abs_votes [int] : number of people who voted to abstain
    - main_client [discord.Client] : the client in the server

  """
  active_votekick = None
  in_timeout = []

  def __init__(self, all_voters, defendant, client):
    """
    Creates a VoteKick Object.

    Parameter all_voters: Everyone who can vote in this VoteKick.
    Precondition: all_voters is a list of Members.
    """
    
    assert VoteKick.active_votekick == None, "A VoteKick is already active."
    for v in all_voters:
      assert isinstance(v, discord.member.Member), "Parameter all_voters contains a non-member item."
    assert isinstance(defendant, discord.member.Member), "Parameter defendant must be a member."
      

    VoteKick.active_votekick = self
    voter_dict = {}
    for v in all_voters:
      voter_dict[v] = ''
    voter_dict[defendant] = 'no'


    self.main_client = client
    self.voters = voter_dict
    self.votes_needed = self.get_threshold()
    self.defendant = defendant
    self.yes_votes = 0
    self.no_votes = 1
    self.abs_votes = 0

  async def start_timer(self, ctx):
    """
    Starts this VoteKick's timer of 120 seconds.

    Ends this VoteKick when the timer expires.

    Parameter ctx: The bot context.
    Precondition: ctx is a valid bot context.
    """
    assert isinstance(ctx, discord.ext.commands.context.Context), "Parameter ctx must be a bot context."
    
    await asyncio.sleep(120)
    if VoteKick.active_votekick != None:
      await ctx.send("The vote to kick " + self.defendant.name + " timed out.")
      VoteKick.active_votekick = None

    

  def get_threshold(self):
    """
    Returns: the number of 'Yes' votes needed for a successful VoteKick.

    The percentage threshold is 60%. Examples:

    - 2 voters: both need to vote yes
    - 3 voters: 2 need to vote yes
    - 4 voters: 3 need to vote yes
    - 11 voters: 7 need to vote yes

    This method returns an integer.
    """
    print('voter length: ' + str(len(self.voters)))
    accum = 0
    for voter in self.voters:
      accum += 1
      print(accum / len(self.voters))
      if accum / len(self.voters) >= .6:
        return accum

  async def vote_no(self, ctx, voter):
    """
    Adds a 'No' vote to this VoteKick.

    Parameter ctx: The bot context.
    Precondition: ctx is a valid bot context.

    Parameter voter: The member who is voting no.
    Precondition: voter is a member in the server.

    Ensures that member `voter` cannot vote again.
    """
    assert isinstance(ctx, discord.ext.commands.context.Context), "Parameter ctx must be a bot context."
    assert isinstance(voter, discord.member.Member), "Parameter voter must be a Member object."

    
    if await self.invalid_vote(ctx, voter):
      return

    msg = 'On the vote to kick ' + self.defendant.name + ', ' + voter.name + ' votes in the negative.'
    await ctx.send(msg)
    self.update_vote_count(ctx, voter, 'no')
    await self.print_vote_status(ctx)
    await self.check_conditions(ctx)

  async def invalid_vote(self, ctx, voter):
    """
    Returns: True if voter is casting an invalid vote.

    Parameter ctx: The bot context.
    Precondition: ctx is a valid bot context.

    Parameter voter: The member who is voting.
    Precondition: voter is a member in the server.

    A vote is invalid if:
      - it is from the defendant
      - the voter was not in the server upon the VoteKick call
      - the voter already voted
    """
    assert isinstance(ctx, discord.ext.commands.context.Context), "Parameter ctx must be a bot context."
    assert isinstance(voter, discord.member.Member), "Parameter voter must be a Member object."
    
    if voter.id == self.defendant.id:
      await ctx.send(voter.name + ", your vote defaults to 'No'.")
      return True
    elif voter not in self.voters:
      await ctx.send(voter.name + ", you are not an active participant of this VoteKick.")
      return True
    elif self.voters[voter] != '':
      await ctx.send(voter.name + ", you already voted.")
      return True

    return False

  async def check_conditions(self, ctx):
    """
    Stops the VoteKick process if the 60% threshold is met
    or if there is no possible vote outcome to kick the
    defendant. 

    Parameter ctx: The bot context.
    Precondition: ctx is a valid bot context.
    """
    assert isinstance(ctx, discord.ext.commands.context.Context), "Parameter ctx must be a bot context."
    
    if self.threshold_met():
      await self.end_votekick(ctx, True)
    elif self.vote_fails():
      await self.end_votekick(ctx, False)
  
  async def vote_yes(self, ctx, voter):
    """
    Adds a 'Yes' vote to this VoteKick.

    Parameter ctx: The bot context.
    Precondition: ctx is a valid bot context.

    Parameter voter: The member who is voting yes.
    Precondition: voter is a member in the server.

    Ensures that member `voter` cannot vote again.
    """  
    assert isinstance(ctx, discord.ext.commands.context.Context), "Parameter ctx must be a bot context."
    assert isinstance(voter, discord.member.Member), "Parameter voter must be a Member object."
    
    if await self.invalid_vote(ctx, voter):
      return

    msg = 'On the vote to kick ' + self.defendant.name + ', ' + voter.name + ' votes in the affirmative.'
    await ctx.send(msg)
    self.update_vote_count(ctx, voter, 'yes')
    await self.print_vote_status(ctx)
    await self.check_conditions(ctx)

  async def vote_abstain(self, ctx, voter):
    """
    Adds an 'Abstain' vote to this VoteKick.

    Parameter ctx: The bot context.
    Precondition: ctx is a valid bot context.

    Parameter voter: The member who is voting to abstain.
    Precondition: voter is a member in the server.

    Ensures that member `voter` cannot vote again.
    """
    assert isinstance(ctx, discord.ext.commands.context.Context), "Parameter ctx must be a bot context."
    assert isinstance(voter, discord.member.Member), "Parameter voter must be a Member object."
    
    if await self.invalid_vote(ctx, voter):
      return

    msg = 'On the vote to kick ' + self.defendant.name + ', ' + voter.name + ' votes to abstain.'
    await ctx.send(msg)
    self.update_vote_count(ctx, voter, 'abstain')
    await self.print_vote_status(ctx)
    await self.check_conditions(ctx)

  
  def threshold_met(self):
    """
    Returns: True if there are enough votes to kick the defendant; False otherwise.

    The threshold is 60%.
    """
    return self.yes_votes >= self.get_threshold()

  def vote_fails(self):
    """
    Returns: True if enough voters have voted 'No' such that the defendant cannot be kicked;
    False otherwise.

    The threshold is 60%.
    """
    current_yes_percentage = self.yes_votes / len(self.voters)
    highest_yes = (len(self.voters) - self.yes_votes - self.no_votes - self.abs_votes) / len(self.voters)
    return current_yes_percentage + highest_yes <= .6


  def update_vote_count(self, ctx, voter, vote):
    """
    Updates this VoteKick's vote count.

    Parameter ctx: The bot context.
    Precondition: ctx is a valid bot context.
    
    Parameter voter: The voter voting.
    Precondition: voter is a member who is in self.voters and is not the defendant.

    Parameter vote: The voter's vote.
    Precondition: vote is a string equal to 'yes', 'no', or 'abstain'.
    """
    assert isinstance(ctx, discord.ext.commands.context.Context), "Parameter ctx must be a bot context."
    assert isinstance(voter, discord.member.Member), "Parameter voter must be a Member object."
    assert isinstance(vote, str), "Parameter vote must be a string."
    
    assert vote == 'no' or vote == 'yes' or vote == 'abstain', "Parameter vote is invalid."  
    self.voters[voter] = vote
    if vote == 'no':
      self.no_votes += 1
    elif vote == 'yes':
      self.yes_votes += 1
    elif vote == 'abstain':
      self.abs_votes += 1
      
    
  async def end_votekick(self, ctx, succeeded):
    """
    Performs logic when the VoteKick is over.

    Parameter ctx: The bot context.
    Precondition: ctx is a valid bot context.
    """
    assert isinstance(ctx, discord.ext.commands.context.Context), "Parameter ctx must be a bot context."
    assert isinstance(succeeded, bool), "Parameter succeeded must be a bool."
    
    if not succeeded:
      await ctx.send("The vote to kick " + self.defendant.name + " failed.")
      VoteKick.active_votekick = None
    else:
      VoteKick.active_votekick = None
      await ctx.send("The vote to kick " + self.defendant.name + " suceeded. Kicking...")
      await self.move_user(ctx)




  async def move_user(self, ctx):
    """
    Moves the condemned defendant to the timeout channel for 60 seconds.

    Parameter ctx: The bot context.
    Precondition: ctx is a valid bot context.    
    """
    member = self.defendant
    VoteKick.in_timeout.append(member)
    timeout = self.main_client.get_channel(961817634821767199)
    ccp = discord.utils.get(member.guild.roles, id = 
  962027214851948606)
    general = self.main_client.get_channel(961478681916735551)
    patriot = discord.utils.get(member.guild.roles, id = 
  962027066914660352)
    await member.remove_roles(patriot)
    await member.add_roles(ccp)
    await member.move_to(timeout)


    await asyncio.sleep(150)
    await member.remove_roles(ccp)
    await member.add_roles(patriot)
    VoteKick.in_timeout.remove(member)
    await ctx.send(self.defendant.name + " has been released from condemnation.")


  async def print_vote_status(self, ctx):
    """
    Prints out the status of this VoteKick.

    Parameter ctx: The bot context.
    Precondition: ctx is a valid bot context.

    The printed format is:

      Current Votes: [g] [g] [g] [r] [r] [y] [ ] [ ] [ ]
      Votes Needed: [g] [g] [g] [ ] [ ] [ ] [ ] [ ] [ ]
    
    """
    assert isinstance(ctx, discord.ext.commands.context.Context), "Parameter ctx must be a bot context."

    
    msg = 'CURRENT VOTES: '
    for i in range(self.yes_votes):
      msg += '<:green_square:12345>'
    for i in range(self.no_votes):
      msg += '<:red_square:92158>'
    for i in range(self.abs_votes):
      msg += '<:yellow_square:22152>'
    remaining = len(self.voters) - self.yes_votes - self.no_votes - self.abs_votes
    for i in range(remaining):
      msg += '<:white_large_square:23593>'

    msg2 = 'NEEDED VOTES:    '
    for i in range(self.get_threshold()):
      msg2 += '<:green_square:12345>'
    for i in range(len(self.voters) - self.get_threshold()):
      msg2 += '<:white_large_square:23593>'

    await ctx.send(msg + '\n' + msg2)  
    

async def votekick(ctx, member, voice_members, client):
  """
  Starts the VoteKick process on member.

  Parameter ctx: The bot context.
  Precondition: ctx is a valid bot context.

  Parameter member: Person who members are voting to kick.
  Precondition: member is a valid Member object
  """
  assert isinstance(ctx, discord.ext.commands.context.Context), "Parameter ctx must be a bot context."
  assert isinstance(member, discord.member.Member), "Parameter member must be a Member object."
  
  
  if VoteKick.active_votekick != None:
    await ctx.send("A VoteKick is already active.")
    return

  defendant = None

  all_voters = []
  for m in voice_members:
    if m.name == member.name:
      defendant = m
    elif (not m.bot):
      all_voters.append(m)

  if len(all_voters) == 0:
    await ctx.send("Not enough members to VoteKick.")
    return

  if defendant in VoteKick.in_timeout:
    await ctx.send(defendant.name + " is already condemned.")
    return
  
  await ctx.send("Starting the VoteKick process on " + member.name + ".\nType **!yes** to vote yes, **!no** to vote no, or **!abstain** to abstain.\nA successful VoteKick requires 60% of all members in no mao zone to vote 'Yes'.")
  

  current_vote = VoteKick(all_voters, defendant, client)
  await current_vote.print_vote_status(ctx)
  await current_vote.check_conditions(ctx)
  await current_vote.start_timer(ctx)


