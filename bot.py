import discord
from discord.ext import commands
from riotwatcher import LolWatcher, ApiError

# golbal variables
api_key = '' # insert key here
watcher = LolWatcher(api_key)
my_region = 'eun1'

# bot = discord.Client(intents=discord.Intents.all())
bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

@bot.event
async def on_ready():
    guild_count = 0
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
        guild_count = guild_count + 1
    print("SampleDiscordBot is in " + str(guild_count) + " guilds.")

@bot.command()
async def pigs(ctx, arg):
    try:
        me = watcher.summoner.by_name(my_region, arg)
    except:
        await ctx.send('no summoner found')
        return
    response = ''

    try:
        my_live_game = None
        try:
            my_live_game = watcher.spectator.by_summoner(my_region, me['id'])
        except:
            print('no game found')

        # print summoner names
        for row in my_live_game['participants']:
            if row['teamId'] != 100:
                print(row['summonerName'])
                response += row['summonerName'] + ' - '
                # check wins and losses for past games
                wins = 0
                losses = 0
                player = row['summonerName']
                player_puuid = watcher.summoner.by_name(my_region, player)
                player_matches = watcher.match.matchlist_by_puuid(my_region, player_puuid['puuid'])
                for i in range (15):
                    match = player_matches[i]
                    match_detail = watcher.match.by_id(my_region, match)
                    if match_detail['info']['queueId'] == 420:
                        for row in match_detail['info']['participants']:
                            if row['summonerName'] == player:
                                if row['win'] == True:
                                    wins += 1
                                elif row['win'] == False:
                                    losses += 1
                print('wins: ', wins, 'losses: ', losses)
                if(wins/(wins+losses) < 0.5):
                    response += 'pig ' + '\n'
                elif (player == 'Jacektocwel'):
                    response += 'pig (as per usual)' + '\n'
                else:
                    response += 'not a pig ' + '\n'
                # response += 'wins: ' + str(wins) + ' losses: ' + str(losses) + '\n'
    except:
        response = 'no game found'

    await ctx.send(response)

bot.run("") # insert bot token here
