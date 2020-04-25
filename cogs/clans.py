import discord
from discord.ext import commands
import requests
from cogs.players import get_player_role
from http_error import HttpError
import tokens


# Credentials to access the Clash of Clans API
headers = {
    "Accept": "application/json",
    "authorization": f"Bearer {tokens.CLASH_API_TOKEN}"
}


# Search for a clan by its tag. If found, print its result
async def _clans_by_tag(ctx, tag):
    url = f"{tokens.CLASH_API_URL}clans/%23{tag}"
    response = requests.get(url=url, headers=headers)
    try:
        c = response.json()
        if response.status_code != 200:
            raise HttpError(response.status_code, c['reason'], tag)
    except HttpError as he:
        await ctx.send(he)
        return

    await ctx.send(f"_Found clan **{c['name']}**:_\n")

    # Create embed to send
    embed = discord.Embed(title=c['name'], color=0xFF00FF)
    embed.set_thumbnail(url=c['badgeUrls']['small'])
    embed.add_field(name="Clan Level", value=c['clanLevel'], inline=False)
    embed.add_field(name="Members", value=c['members'], inline=False)
    embed.add_field(name="Clan Points", value=c['clanPoints'], inline=False)
    embed.add_field(name="Clan Versus Points", value=c['clanVersusPoints'], inline=False)
    embed.add_field(name="Description", value=c['description'], inline=False)
    await ctx.send(embed=embed)


# Print the top 10 results from searching for a clan its name
async def _clans_by_name(ctx, name):
    url = f"{tokens.CLASH_API_URL}clans?name={name.replace(' ', '%20')}"
    response = requests.get(url=url, headers=headers)
    try:
        c = response.json()
        if response.status_code != 200:
            raise HttpError(response.status_code, c['reason'], name)
    except HttpError as he:
        await ctx.send(he)
        return

    await ctx.send(f"_Fetching search results for \"{name}\"..._")

    search_limit = min({10, len(c['items'])})
    message = ""
    for i in range(search_limit):
        clan = c['items'][i]
        message += f"\n**{i+1}. {clan['name']}** ({clan['members']} members, {clan['tag']})"
    await ctx.send(message)
    await ctx.send("_To get more information on one of these clans, enter_ !clans <tag>.")


class Clans(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="clans",
        description="Returns a list of clans that match a searched name or tag. If searching by name, enclose the "
                    "clan's name in quotes. The top 10 results will be shown if searching by name."
                    "If searching by tag, include the leading pound sign (#)."
    )
    async def _clans(self, ctx, name_or_tag):
        if name_or_tag[0] == '#':
            await _clans_by_tag(ctx, name_or_tag[1:])
        else:
            await _clans_by_name(ctx, name_or_tag)

    @commands.command(
        name="clanmembers",
        description="Returns a list of members in a clan."
    )
    async def _clanmembers(self, ctx, tag):
        tag = tag[1:]
        url = f"{tokens.CLASH_API_URL}clans/%23{tag}"
        response = requests.get(url=url, headers=headers)
        try:
            c = response.json()
            if response.status_code != 200:
                raise HttpError(response.status_code, c['reason'], tag)
        except HttpError as he:
            await ctx.send(he)
            return

        await ctx.send(f"_Listing members in clan **{c['name']}**..._\n")

        cm = c['memberList']

        # Divide output into messages with 10 entries to circumvent Discord's message length limit
        message = ""
        i = 0
        while i < len(cm):
            player = cm[i]
            role = get_player_role(player)
            message += f"\n**{i+1}. {player['name']}** ({player['trophies']} trophies, {role}{player['tag']})"

            i += 1
            if i % 10 == 0 or i == len(cm):
                await ctx.send(message)
                message = ""


def setup(bot):
    bot.add_cog(Clans(bot))
