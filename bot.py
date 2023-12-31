import discord
import asyncio
from discord.ext import commands
from riotwatcher import LolWatcher, ApiError

# golbal variables
api_key = '' # insert key here
watcher = LolWatcher(api_key)
my_region = 'eun1'

# bot = discord.Client(intents=discord.Intents.all())
bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())

@bot.event
async def on_ready():
    # print names and ids of all servers bot is connected to
    guild_count = 0
    for guild in bot.guilds:
        print(f"id: {guild.id} name: {guild.name}")
        guild_count = guild_count + 1
    print("Pig Detector is on " + str(guild_count) + " servers.")

@bot.command()
async def commands(ctx):
    await ctx.send('$pigs <summoner name> - detects all pigs in live game\n'
                   '$stats <summoner name> - shows most important stats from last game\n'
                   '$stats <summoner name> <games ago> - shows most important stats from x games ago\n'
                   '$list - shows list of known inters\n'
                   '$list add <summoner name> - adds summoner to list\n'
                   '$list del <summoner name> - deletes summoner from list\n')

@bot.command()
async def list(ctx, delete=None, arg1=None):
    # if no arguments, print list
    if arg1 is None and delete is None:
        f = open('list.txt', 'r')
        lines = f.readlines()
        response = ''
        f.close()
        for line in lines:
            words = line.split(' ')
            if len(words) > 1:
                second_word = words[1]
                response += second_word
        if lines == []:
            response = 'list is empty'
        await ctx.send(response)
        return

    # if delete argument, check if summoner name is given
    if delete == 'del' and arg1 is None:
        await ctx.send('delete who?')
        return

    # if add argument, check if summoner name is given
    if delete == 'add' and arg1 is None:
        await ctx.send('add who?')
        return

    # if delete argument, delete player from list
    if delete == 'del' and arg1 is not None:
        # find summoner
        try:
            player = arg1
            player_puuid = watcher.summoner.by_name(my_region, player)
        except:
            print('/list error: no summoner found')
            await ctx.send('no summoner found')
            return
        # delete player from list
        f = open('list.txt', 'r')
        lines = f.readlines()
        f.close()
        f = open('list.txt', 'w')
        response = 'player not on the list \n'
        for line in lines:
            if player_puuid['puuid'] not in line:
                f.write(line)
            else:
                response = 'player deleted from list: ' + arg1 + '\n'
        f.close()
        await ctx.send(response)
        return

    # if add argument, add player to list
    if delete == 'add' and arg1 is not None:
        # find summoner
        try:
            player = arg1
            player_puuid = watcher.summoner.by_name(my_region, player)
        except:
            print('/list error: no summoner found')
            await ctx.send('no summoner found')
            return
        # find if player is already on list
        f = open('list.txt', 'r')
        f.seek(0)
        for line in f:
            if player_puuid['puuid'] in line:
                response = 'player is already on list \n'
                f.close()
                await ctx.send(response)
                return
        f.close()
        # add player to list
        f = open('list.txt', 'a')
        f.write(player_puuid['puuid'] + ': ' + arg1 + '\n')
        response = 'player added to list: ' + arg1 + '\n'
        f.close()
        await ctx.send(response)
        return

    await ctx.send('invalid command')

@bot.command()
async def pigs(ctx, arg):
    # find summoner
    try:
        me = watcher.summoner.by_name(my_region, arg)
    except:
        print('/pigs error: no summoner found')
        await ctx.send('no summoner found')
        return

    response = ''
    try:
        # find live game and team id
        try:
            my_live_game = watcher.spectator.by_summoner(my_region, me['id'])
            my_team_id = my_live_game['participants'][0]['teamId']
        except:
            print('/pigs error: no game found')
            await ctx.send('no game found')
            return

        for row in my_live_game['participants']:
            # find all teammates
            if row['teamId'] == my_team_id:
                print(row['summonerName'])
                response += row['summonerName'] + ' - '
                # find puuid by summoner name
                player = row['summonerName']
                player_puuid = watcher.summoner.by_name(my_region, player)
                # find match history by puuid
                player_matches = watcher.match.matchlist_by_puuid(my_region, player_puuid['puuid'])
                # check wins and losses for past 10 ranked games
                wins = 0
                losses = 0
                arams = 0
                tft = 0
                i = 0
                search_limit = 20
                while (wins+losses < 10 and i < search_limit):
                    # sometimes match history is empty
                    try:
                        match = player_matches[i]
                        match_detail = watcher.match.by_id(my_region, match)
                    except:
                        # if match history is empty, multiply wins and losses to end loop
                        wins *= 10
                        losses *= 10
                        print('/pigs error: failed to find game to analyze')
                    # check if match is aram
                    if match_detail['info']['queueId'] == 450:
                        arams += 1
                    # check if match is tft
                    if match_detail['info']['queueId'] == 1090 or match_detail['info']['queueId'] == 1100:
                        tft += 1
                    # check if match is ranked (only solo/duo)
                    if match_detail['info']['queueId'] == 420:
                        for row in match_detail['info']['participants']:
                            if row['summonerName'] == player:
                                if row['win'] == True:
                                    wins += 1
                                elif row['win'] == False:
                                    losses += 1
                    i += 1
                print('wins: ', wins, 'losses: ', losses)
                print('arams: ', arams, 'tft: ', tft)
                # detect all lowbobs
                if(wins/(wins+losses) < 0.5 and wins+losses > 0):
                    response += 'pig'
                elif(wins+losses == 0):
                    response += 'first game'
                elif (player == 'Jacektocwel'): # VERY important line
                    response += 'pig (as per usual)'
                else:
                    response += 'not a pig '
                # detect all aram/tft players
                if(arams > 0):
                    response += ', aram enjoyer'
                if(tft > 0):
                    response += ', tft player (ewwww)'
                response += '\n'
    except:
        print('/pigs error: ERORR')
        response = 'ERROR'
    if response == '':
        print('/pigs error: ERORR 2 ')
        response = 'ERROR'
    await ctx.send(response)

@bot.command()
async def stats(ctx, arg, arg2=None):
    # parameter 2 is optional, if not given, show latest game
    if arg2 is None:
        game_no = 0
    else:
        game_no = int(arg2)
    # find summoner
    try:
        me = watcher.summoner.by_name(my_region, arg)
    except:
        print('/stats error: no summoner found')
        await ctx.send('no summoner found')
        return
    # find latest game
    try:
        my_matches = watcher.match.matchlist_by_puuid(my_region, me['puuid'])
        match = my_matches[game_no]
        match_detail = watcher.match.by_id(my_region, match)
    except:
        print('/stats error: no game found')
        await ctx.send('no game found')
        return
    # get stats (only most important ones)
    response = ''
    response += 'Game mode: ' + str(match_detail['info']['gameMode']) + '\nQueue type: ' + str(match_detail['info']['queueId']) + '\n'
    for row in match_detail['info']['participants']:
        if row['summonerName'] == arg:
            response += 'KDA: ' + str(row['kills']) + '/' + str(row['deaths']) + '/' + str(row['assists']) + '\n'
            response += 'Bait pings: ' + str(row['baitPings']) + '\n'
            response += '? pings: ' + str(row['enemyMissingPings']) + '\n'
            response += 'Largest killing spree: ' + str(row['largestKillingSpree']) + '\n'
            response += 'Largest multi kill: ' + str(row['largestMultiKill']) + '\n'
            response += 'Total time spent dead: ' + str(row['totalTimeSpentDead']) + '\n'
            response += 'Kill participation: ' + str(row['challenges']['killParticipation']) + '\n'
            response += 'MAX cs advantage: ' + str(row['challenges']['maxCsAdvantageOnLaneOpponent']) + '\n'
            response += 'Skillshots hit: ' + str(row['challenges']['skillshotsHit']) + '\n'
            response += 'Skillshots dodged: ' + str(row['challenges']['skillshotsDodged']) + '\n'
            response += 'Invade kills (before jg camps spawn): ' + str(row['challenges']['takedownsBeforeJungleMinionSpawn']) + '\n'
    if response == '':
        print('/stats error: ERORR')
        response = 'ERROR'
    await ctx.send(response)

bot.run("") # insert bot token here
