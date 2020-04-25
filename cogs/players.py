import discord
from discord.ext import commands
import requests
from http_error import HttpError
import tokens


# Credentials to access the Clash of Clans API
headers = {
    "Accept": "application/json",
    "authorization": f"Bearer {tokens.CLASH_API_TOKEN}"
}


# Returns a string with a player's clan role
# Returns an empty string if the player is just a member
def get_player_role(player):
    role = player['role']
    if role == "coLeader":
        role = "Co-Leader, "
    elif role == "leader":
        role = "Leader, "
    else:
        role = ""
    return role


class Players(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Search for a player and print some attributes
    @commands.command(
        name="players",
        description="Searches for a player based on their unique tag."
    )
    async def _players(self, ctx, tag):
        # Fetch player data from an API request. If the request fails, abort before handling the JSON
        if tag[0] == '#':
            tag = tag[1:]
        url = f"{tokens.CLASH_API_URL}players/%23{tag}"
        response = requests.get(url=url, headers=headers)
        try:
            p = response.json()
            if response.status_code != 200:
                raise HttpError(response.status_code, p['reason'], tag)
        except HttpError as he:
            await ctx.send(he)
            return

        # If the player is just a member, the bot won't print a role
        role = get_player_role(p)

        await ctx.send(f"_Found player **{p['name']}**:_\n")

        # Create embed to send
        embed = discord.Embed(title=p['name'], color=0xFF00FF)
        embed.set_thumbnail(url=p['league']['iconUrls']['small'])
        embed.add_field(name="Clan", value=f"{p['clan']['name']} ({role}#{tag})", inline=False)
        embed.add_field(name="Town Hall", value=p['townHallLevel'], inline=False)
        embed.add_field(name="Trophies", value=p['trophies'], inline=False)
        embed.add_field(name="Experience Level", value=p['expLevel'], inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Players(bot))
