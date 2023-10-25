from discord.ext import commands
import discord
import random
import http.client
import json
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix="!",  # Change to desired prefix
    case_insensitive=True, # Commands aren't case-sensitive
    intents = intents # Set up basic permissions
)

bot.author_id = 266190470328090624  # Change to your discord id

user_history = {}
flood_timer = 60
flood_limit = 5
flood_check = False

@bot.event
async def on_ready():  # When the bot is ready
    print("I'm in")
    print(bot.user)  # Prints the bot's username and identifier

@bot.command()
async def pong(ctx):
    await ctx.send('pong')

@bot.command()
async def name(ctx):
    """Responds to the command !name with the name of the user."""
    await ctx.send(ctx.author.name)

@bot.command()
async def d6(ctx):
    """Responds to the command !d6 with a random integer between 1 and 6."""
    await ctx.send(random.randint(1,6))

@bot.event
async def on_message(message):
    """Responds to the message Salut tout le monde with "Salut tout seul, {Ping of the user who typed the message}!"""
    if message.content == "Salut tout le monde":
        await message.channel.send(f"Salut tout seul, {message.author.mention}")
    await bot.process_commands(message)

@bot.command()
async def admin(ctx, member: discord.Member):
    """Responds to the command !admin by creating a role named admin and giving it to the user name provided after the command."""
    adminrole = discord.utils.get(ctx.guild.roles, name="admin")
    if adminrole is None:
        adminrole = await ctx.guild.create_role(name="admin", permissions=discord.Permissions.all())
    await member.add_roles(adminrole)
    await ctx.send(f"Admin role given to {member.mention}")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    """Responds to the command !ban by banning the username provided after the command and the reason provided after."""
    catchphrases = ["Cheh !", "A plus dans le bus !", "Bisous caribou !"]
    
    await ctx.guild.ban(member, reason=reason)
    await ctx.send(f"You banned {member.mention}: {reason if reason != 'No reason provided' else random.choice(catchphrases)}")

@bot.event
async def on_message(message):
    """Monitor the message sent in the discord"""
    global flood_check
    if message.author == bot.user:
        return

    if flood_check:
        author_id = str(message.author.id)
        current_time = message.created_at.timestamp()

        if author_id not in user_history:
            user_history[author_id] = []

        user_history[author_id] = [
            msg
            for msg in user_history[author_id]
            if current_time - msg <= 60 * flood_timer
        ]

        user_history[author_id].append(current_time)

        if len(user_history[author_id]) > flood_limit:
            await message.channel.send(
                f"{message.author.mention}, please refrain from flooding the chat."
            )

    await bot.process_commands(message)

@bot.command()
async def flood(ctx, action=None):
    """Responds to !flood by activating or deactivating the flood monitoring."""
    global flood_check
    if action == "activate":
        flood_check = True
        await ctx.send("Flood monitoring has been activated.")
    elif action == "deactivate":
        flood_check = False
        await ctx.send("Flood monitoring has been deactivated.")
    else:
        await ctx.send("Usage: !flood [activate/deactivate]")

@bot.command()
async def xkcd(ctx):
    """Responds to !xkcd by sending a random xkcd comic."""
    connection = http.client.HTTPSConnection("xkcd.com")
    connection.request("GET", f"{random.randint(1, 2846)}/info.0.json")
    response = connection.getresponse()

    if response.status == 200:
        data = response.read()
        decoded = data.decode("utf-8")
        loaded = json.loads(decoded)
        await ctx.send(f"{loaded['img']}")
    else:
        await ctx.send("Couldn't get a comic.")

@bot.command()
async def poll(ctx, *, question):
    poll_message = await ctx.send(
        f"@here {question} (vote will last 10 seconds)"
    )

    question_message = await ctx.send(f"**Poll:** {question}")
    await question_message.add_reaction("👍")
    await question_message.add_reaction("👎")

    time_limit = 10

    if time_limit > 0:
        await asyncio.sleep(time_limit)

        question_message = await ctx.channel.fetch_message(question_message.id)

        thumbs_up = 0
        thumbs_down = 0
        for reaction in question_message.reactions:
            if str(reaction.emoji) == "👍":
                thumbs_up = reaction.count - 1
            elif str(reaction.emoji) == "👎":
                thumbs_down = reaction.count - 1

        await ctx.send(
            f"**Poll Results:** {question}\n👍: {thumbs_up} | 👎: {thumbs_down}"
        )
        await poll_message.delete()



token = ""
bot.run(token)  # Starts the bot