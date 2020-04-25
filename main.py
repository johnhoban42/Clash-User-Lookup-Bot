from discord.ext import commands
import tokens


# Create the bot
bot = commands.Bot(
    command_prefix='!',
    description="A bot for looking up player and clan data from Clash of Clans.",
    case_insensitive=True
)


cogs = ['cogs.clans', 'cogs.players']


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    for cog in cogs:
        bot.load_extension(cog)
    return

# Finally, login the bot
bot.run(tokens.DISCORD_API_TOKEN, bot=True, reconnect=True)
bot.change_presence(activity="Clash of Clans")
