from src.wikipedia import WikipediaSearch
from src.log import commandlog
from src.google import GoogleSearch
from src.myanimelist import MyAnimeListSearch
from src.googlereverseimages import ImageSearch
from src.sudo import Sudo
from src.scholar import ScholarSearch
from src.youtube import YoutubeSearch
from dotenv import load_dotenv
from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands
import discord, re, os, asyncio, json, aiohttp

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
commandprefix = "&"

with open('serverSettings.json', 'r') as data:
    serverSettings = json.load(data)

def prefix(bot, message):
    id = message.guild.id
    return serverSettings[str(id)]['commandprefix']

intents = discord.Intents.default()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix=prefix, intents=intents)

@bot.event
async def on_guild_join(guild):
    #Reads settings of server
    with open('serverSettings.json', 'r') as data:
        serverSettings = json.load(data)

    Sudo.settingsCheck(serverSettings, guild.id)

    owner = await bot.fetch_user(guild.owner_id)
    dm = await owner.create_dm()
    embed = discord.Embed(title=f"Search.io was added to your server: '{guild.name}'.", 
        description = f"""
    Search.io is a bot that searches through multiple search engines/APIs.
    The activation command is '{commandprefix}', and a list of various commands can be found using '{commandprefix}help'.
            
    A list of admin commands can be found by using '{commandprefix}help sudo'. These commands may need ID numbers, which requires Developer Mode.
    To turn on Developer Mode, go to Settings > Appearances > Advanced > Developer Mode. Then right click on users, roles, or channels to copy ID.

    As a start, it is suggested to designate an administrator role that can use Search.io's sudo commands. Do '{commandprefix}sudo adminrole [roleID]' to designate an admin role.
    It is also suggested to turn on Safe Search, if needed. Do '{commandprefix}sudo safesearch [on/off]'. The default is off. 
    If you need to block a specific user from using Search.io, do '{commandprefix}sudo blacklist [userID]'. Unblock with '{commandprefix}sudo whitelist [userID]'

    If you have any problems with Search.io, DM ACEslava#9735""")
    await dm.send(embed=embed)
    return

@bot.event
async def on_guild_remove(guild):
    with open('serverSettings.json', 'r') as data:
        serverSettings = json.load(data)

    del serverSettings[str(guild.id)]
    
    with open('serverSettings.json', 'w') as data:
        data.write(json.dumps(serverSettings, indent=4))
    return

@bot.event
async def on_connect():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="command prefix '&'"))

    with open('serverSettings.json', 'r') as data:
        serverSettings = json.load(data)
    
    for servers in bot.guilds:
        Sudo.settingsCheck(serverSettings, servers.id)

class WikipediaCommands(commands.Cog, name="Wikipedia Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name = 'wiki',
        help=f"""Wikipedia search. Usage: {commandprefix}wiki [query] [flags]. Send 'cancel' to cancel search
            
            ----Flags----
            --lang              Specify a country code to search through that wikipedia. Use {commandprefix}wikilang to see available codes""",
        brief='Search through Wikipedia.')
    async def wikisearch(self, ctx, *args):
        with open('serverSettings.json', 'r') as data:
            serverSettings = json.load(data)

        if str(ctx.author.id) not in serverSettings[str(ctx.guild.id)]['blacklist'] and serverSettings[str(ctx.guild.id)]['wikipedia'] != False:
            UserCancel = Exception
            language = "en"
            if not args: #checks if search is empty
                await ctx.send('Enter search query:') #if empty, asks user for search query
                try:
                    userquery = await bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout = 30) # 30 seconds to reply
                    userquery = userquery.content
                    if userquery == 'cancel': raise UserCancel
                
                except asyncio.TimeoutError:
                    await ctx.send(f'{ctx.author.mention} Error: You took too long. Aborting') #aborts if timeout

                except UserCancel:
                    await ctx.send('Aborting')
            else: 
                args = list(args)
                if '--lang' in args:
                    language = args[args.index('--lang')+1]
                    del args[args.index('--lang'):]
                userquery = ' '.join(args).strip() #turns multiword search into single string

            search = WikipediaSearch(bot, ctx, language, userquery)
            await search.search()
            return
    
    @commands.command(
            name = 'wikilang',
            help="""Lists Wikipedia's supported wikis in ISO codes. Common language codes are:
            zh: 中文
            es: Español
            en: English
            pt: Português
            hi: हिन्दी
            bn: বাংলা
            ru: русский
            """,
            brief="Lists supported languages")
    async def wikilang(self, ctx):
        with open('serverSettings.json', 'r') as data:
            serverSettings = json.load(data)

        if str(ctx.author.id) not in serverSettings[str(ctx.guild.id)]['blacklist']:
            log = commandlog(ctx, "wikilang")
            log.appendToLog()

            await WikipediaSearch(bot, ctx, "en").lang()
            return

class GoogleCommands(commands.Cog, name="Google Search Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
            name = 'google',
            help=f"""Google search. Usage: {commandprefix}google [query].
                If a keyword is detected in [query], a special function will activate
                
                ----Keywords----
                translate           Uses Google Translate API to translate from language > English 
                """,
            brief='Search Google.'
        )
    async def gsearch(self, ctx, *args):
        UserCancel = Exception
        with open('serverSettings.json', 'r') as data:
            serverSettings = json.load(data)

        if str(ctx.author.id) not in serverSettings[str(ctx.guild.id)]['blacklist'] and serverSettings[str(ctx.guild.id)]['google'] != False:
            if not args: #checks if search is empty
                await ctx.send('Enter search query:') #if empty, asks user for search query
                try:
                    userquery = await bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout = 30) # 30 seconds to reply
                    userquery = userquery.content
                    if userquery == 'cancel': raise UserCancel
                
                except asyncio.TimeoutError:
                    await ctx.send(f'{ctx.author.mention} Error: You took too long. Aborting') #aborts if timeout

                except UserCancel:
                    await ctx.send('Aborting')
            else: 
                args = list(args)
                userquery = ' '.join(args).strip() #turns multiword search into single string.

            search = GoogleSearch(bot, ctx, serverSettings, userquery)
            await search.search()
            return

    @commands.command(
        name='image',
        help="Reads a user's reply for an image URL or takes in a URL as an arg",
        brief="Reverse image search with a given URL arg or reply")
    async def image(self, ctx, *args):
        UserCancel = Exception
        
        with open('serverSettings.json', 'r') as data:
            serverSettings = json.load(data)

        if str(ctx.author.id) not in serverSettings[str(ctx.guild.id)]['blacklist'] and serverSettings[str(ctx.guild.id)]['google'] != False:
            if ctx.message.reference:
                imagemsg = await ctx.fetch_message(ctx.message.reference.message_id)
                if imagemsg.attachments:
                    userquery = imagemsg.attachments[0].url

            elif not args: #checks if search is empty
                await ctx.send('Enter search query:') #if empty, asks user for search query
                try:
                    userquery = await bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout = 30) # 30 seconds to reply
                    userquery = userquery.content
                    if userquery == 'cancel': raise UserCancel
                
                except asyncio.TimeoutError:
                    await ctx.send(f'{ctx.author.mention} Error: You took too long. Aborting') #aborts if timeout

                except UserCancel:
                    await ctx.send('Aborting')
            else: 
                args = list(args)
                userquery = ' '.join(args).strip() #turns multiword search into single string

            search = ImageSearch(bot, ctx, userquery)
            await search.search()
            return

    @commands.command(
            name = 'scholar',
            help=f"""Google Scholar search. Usage: {commandprefix}scholar [query] [flags].
                
                ----Flags----
                --author            Use [query] to search for a specific author. Cannot be used with --cite
                --cite              Outputs a citation for [query] in BibTex. Cannot be used with --author""",
            brief='Search through Google Scholar.')   
    async def scholarsearch(self, ctx, *args):
        with open('serverSettings.json', 'r') as data:
            serverSettings = json.load(data)

        if str(ctx.author.id) not in serverSettings[str(ctx.guild.id)]['blacklist'] and serverSettings[str(ctx.guild.id)]['scholar'] != False:
            UserCancel = Exception
            if not args: #checks if search is empty
                await ctx.send('Enter search query:') #if empty, asks user for search query
                try:
                    userquery = await bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout = 30) # 30 seconds to reply
                    userquery = userquery.content
                    if userquery == 'cancel': raise UserCancel
                
                except asyncio.TimeoutError:
                    await ctx.send(f'{ctx.author.mention} Error: You took too long. Aborting') #aborts if timeout

                except UserCancel:
                    await ctx.send('Aborting')
            else:
                args = ' '.join(list(args)).strip().split('--') #turns entire command into list split by flag operator
                userquery = args[0].strip()
                del args[0]

            search = ScholarSearch(bot, ctx, args, userquery)
            await search.search()
            return
    
    @commands.command(
        name = 'youtube',
        help=f"""Youtube search. Usage: {commandprefix}youtube [query].""",
        brief='Search Youtube.')
    async def ytsearch(self, ctx, *args):
        UserCancel = Exception
        with open('serverSettings.json', 'r') as data:
            serverSettings = json.load(data)

        if str(ctx.author.id) not in serverSettings[str(ctx.guild.id)]['blacklist'] and serverSettings[str(ctx.guild.id)]['youtube'] != False:
            if not args: #checks if search is empty
                await ctx.send('Enter search query:') #if empty, asks user for search query
                try:
                    userquery = await bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout = 30) # 30 seconds to reply
                    userquery = userquery.content
                    if userquery == 'cancel': raise UserCancel
                
                except asyncio.TimeoutError:
                    await ctx.send(f'{ctx.author.mention} Error: You took too long. Aborting') #aborts if timeout

                except UserCancel:
                    await ctx.send('Aborting')
            else: 
                args = list(args)
                userquery = ' '.join(args).strip() #turns multiword search into single string.

            search = YoutubeSearch(bot, ctx, userquery)
            await search.search()
            return

class MyAnimeListCommands(commands.Cog, name="MyAnimeList Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
            name = 'anime',
            help=f"""Add a query after {commandprefix}anime to search through the MyAnimeList database. Send 'cancel' to cancel search.""",
            brief='Search through MyAnimeList.'
    )
    async def animesearch(self, ctx, *args):
        UserCancel = Exception
        with open('serverSettings.json', 'r') as data:
            serverSettings = json.load(data)

        if str(ctx.author.id) not in serverSettings[str(ctx.guild.id)]['blacklist'] and serverSettings[str(ctx.guild.id)]['mal'] != False:
            if not args: #checks if search is empty
                await ctx.send('Enter search query:') #if empty, asks user for search query
                try:
                    userquery = await bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout = 30) # 30 seconds to reply
                    userquery = userquery.content
                    if userquery == 'cancel': raise UserCancel
                
                except asyncio.TimeoutError:
                    await ctx.send(f'{ctx.author.mention} Error: You took too long. Aborting') #aborts if timeout

                except UserCancel:
                    await ctx.send('Aborting')
            else: 
                userquery = ' '.join(args).strip() #turns multiword search into single string
            
            search = MyAnimeListSearch(bot, ctx, userquery)
            await search.search()
            return

@bot.command(
        name='log',
        help="DMs a .csv file of all the logs that the bot has for your username",
        brief="DMs a .csv file of the logs"       
)
async def logging(ctx): 
    log = commandlog(ctx, "log")
    log.appendToLog()
    await log.logRequest(bot)
    return

@bot.command(
        name='sudo',
        help=f"""Admin commands. Server owner has sudo privilege by default. Usage: {commandprefix}sudo [command] [args].
        
        ----Commands----
        say                 Have the bot say something. Args: message. Optional flag: --channel [channelID]
        blacklist           Block a user from using the bot. Args: userName OR userID 
        whitelist           Unblock a user from using the bot. Args: userName OR userID       
        sudoer              Add a user to the sudo list. Args: userName OR userID           
        unsudoer            Remove a user to the sudo list. Args: userName OR userID 
        config              Opens the bot configuration menu. Do {commandprefix}sudo config to see list of args""",

        brief="Admin commands"       
)
async def sudo(ctx, *args):
    args = list(args)
    command = Sudo(bot, ctx)
    await command.sudo(args)

    with open('serverSettings.json', 'r') as data:
        global serverSettings
        serverSettings = json.load(data)
    return

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send(f"Command not found. Do {commandprefix}help for available commands")

bot.add_cog(WikipediaCommands(bot))
bot.add_cog(GoogleCommands(bot))
bot.add_cog(MyAnimeListCommands(bot))

bot.run(DISCORD_TOKEN)