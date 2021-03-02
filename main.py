from src.wikipedia import WikipediaSearch
from src.log import commandlog
from src.google import GoogleSearch
from src.myanimelist import MyAnimeListSearch
from src.googlereverseimages import ImageSearch
from src.sudo import Sudo
from src.scholar import ScholarSearch
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import asyncio
import json

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
commandprefix = "&"
bot = commands.Bot(command_prefix=commandprefix)

async def on_message(message):
    if message.author == bot.user:
        return
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="command prefix '&'"))

class WikipediaCommands(commands.Cog, name="Wikipedia Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name = 'wikisearch',
        help=f"""Wikipedia search. Usage: {commandprefix}wikisearch [query] [flags]. Send 'cancel' to cancel search
            
            ----Flags----
            --lang              Specify a country code to search through that wikipedia. Use {commandprefix}wikilang to see available codes""",
        brief='Search through Wikipedia.'
    )

    async def wikisearch(self, ctx, *args):
        with open('serverSettings.json', 'r') as data:
            serverSettings = json.load(data)

        if 'blacklist' in serverSettings[str(ctx.guild.id)].keys():
            if str(ctx.author.id) not in serverSettings[str(ctx.guild.id)]['blacklist']:
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
        else:
            serverSettings[str(ctx.guild.id)]['blacklist'] = []
            with open('serverSettings.json', 'w') as data:
                data.write(json.dumps(serverSettings, indent=4))
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
            brief="Lists supported languages"
    )
    async def wikilang(self, ctx):
        with open('serverSettings.json', 'r') as data:
            serverSettings = json.load(data)

        if 'blacklist' in serverSettings[str(ctx.guild.id)].keys():
            if str(ctx.author.id) not in serverSettings[str(ctx.guild.id)]['blacklist']:
                log = commandlog(ctx, "wikilang")
                log.appendToLog()

                await WikipediaSearch(bot, ctx, "en").lang()
                return
        else:
            serverSettings[str(ctx.guild.id)]['blacklist'] = []
            with open('serverSettings.json', 'w') as data:
                data.write(json.dumps(serverSettings, indent=4))
            return
class GoogleCommands(commands.Cog, name="Google Search Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
            name = 'gsearch',
            help=f"""Google search. Usage: {commandprefix}gsearch [query].
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

        if 'blacklist' in serverSettings[str(ctx.guild.id)].keys():
            if str(ctx.author.id) not in serverSettings[str(ctx.guild.id)]['blacklist']:
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

                search = GoogleSearch(bot, ctx, userquery)
                await search.search()
                return
        else:
            serverSettings[str(ctx.guild.id)]['blacklist'] = []
            with open('serverSettings.json', 'w') as data:
                data.write(json.dumps(serverSettings, indent=4))
            return


    @commands.command(
        name='image',
        help="Reads a user's reply for an image URL or takes in a URL as an arg",
        brief="Reverse image search with a given URL arg or reply"       
    )
    async def image(self, ctx, *args):
        UserCancel = Exception
        
        with open('serverSettings.json', 'r') as data:
            serverSettings = json.load(data)

        if 'blacklist' in serverSettings[str(ctx.guild.id)].keys():
            if str(ctx.author.id) not in serverSettings[str(ctx.guild.id)]['blacklist']:
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
        else:
            serverSettings[str(ctx.guild.id)]['blacklist'] = []
            with open('serverSettings.json', 'w') as data:
                data.write(json.dumps(serverSettings, indent=4))
            return

    @commands.command(
            name = 'scholar',
            help=f"""Google Scholar search. Usage: {commandprefix}scholar [query] [flags].
                
                ----Flags----
                --author            Use [query] to search for a specific author. Cannot be used with --cite
                --cite              Outputs a citation for [query] in BibTex. Cannot be used with --author""",
            brief='Search through Google Scholar.'
            )
    
    async def scholarsearch(self, ctx, *args):
        with open('serverSettings.json', 'r') as data:
            serverSettings = json.load(data)

        if 'blacklist' in serverSettings[str(ctx.guild.id)].keys():
            if str(ctx.author.id) not in serverSettings[str(ctx.guild.id)]['blacklist']:
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
        else:
            serverSettings[str(ctx.guild.id)]['blacklist'] = []
            with open('serverSettings.json', 'w') as data:
                data.write(json.dumps(serverSettings, indent=4))
            return
class MyAnimeListCommands(commands.Cog, name="MyAnimeList Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
            name = 'animesearch',
            help=f"""Add a query after {commandprefix}animesearch to search through the MyAnimeList database. Send 'cancel' to cancel search.""",
            brief='Search through MyAnimeList.'
    )
    async def animesearch(self, ctx, *args):
        UserCancel = Exception
        with open('serverSettings.json', 'r') as data:
            serverSettings = json.load(data)

        if 'blacklist' in serverSettings[str(ctx.guild.id)].keys():
            if str(ctx.author.id) not in serverSettings[str(ctx.guild.id)]['blacklist']:
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
        else:
            serverSettings[str(ctx.guild.id)]['blacklist'] = []
            with open('serverSettings.json', 'w') as data:
                data.write(json.dumps(serverSettings, indent=4))
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
        adminrole           Designate the server admin role. Omit roleID to see current adminrole. Args: roleID 
        blacklist           Block a user from using the bot. Args: userID  
        whitelist           Unblock a user from using the bot. Args: userID       
        sudoer              Add a user to the sudo list. Args: userID          
        unsudoer            Remove a user to the sudo list. Args: userID""",

        brief="Admin commands"       
)
async def sudo(ctx, *args):
    args = list(args)
    command = Sudo(bot, ctx)
    await command.sudo(args)
    return

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        if "search" in error.args[0]:
            await ctx.send(f"{commandprefix}search is deprecated, use {commandprefix}wikisearch. Do {commandprefix}help search for more info")
        else:
            await ctx.send(f"Command not found. Do {commandprefix}help for available commands")

bot.add_cog(WikipediaCommands(bot))
bot.add_cog(GoogleCommands(bot))
bot.add_cog(MyAnimeListCommands(bot))

bot.run(DISCORD_TOKEN)