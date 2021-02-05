from src.wikipedia import WikipediaSearch
from src.log import commandlog
from src.google import GoogleSearch
from src.myanimelist import MyAnimeListSearch
from src.googlereverseimages import ImageSearch
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import asyncio
import csv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix='&')

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
            help="""Add a query after \wikisearch to search through the Wikipedia databases. Send 'cancel' to cancel search.
                Multilanguage support with --lang followed by an ISO 3166 country code. See \lang for a full list of supported languages
                Renamed from $search in preparation for more search functions""",
            brief='Search for a Wikipedia article.'
    )
    async def wikisearch(self, ctx, *args):
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
            brief="Lists supported languages"
    )
    async def wikilang(self, ctx):
        log = commandlog(ctx, "wikilang")
        log.appendToLog()

        await WikipediaSearch(bot, ctx, "en").lang()
        return
class GoogleCommands(commands.Cog, name="Google Search Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
            name = 'gsearch',
            help="""Add a query after \gsearch to search through Google. Send 'cancel' to cancel search.""",
            brief='Search Google.'
    )
    async def gsearch(self, ctx, *args):
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
            args = list(args)
            userquery = ' '.join(args).strip() #turns multiword search into single string.

        search = GoogleSearch(bot, ctx, userquery)
        await search.search()
        return

    @commands.command(
        name='image',
        help="Reads a user's reply for an image URL or takes in a URL as an arg",
        brief="Reverse image search with a given URL arg or reply"       
    )

    async def image(self, ctx, *args):
        UserCancel = Exception
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
class MyAnimeListCommands(commands.Cog, name="MyAnimeList Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
            name = 'animesearch',
            help="""Add a query after \animesearch to search through the MyAnimeList database. Send 'cancel' to cancel search.""",
            brief='Search for an anime.'
    )
    async def animesearch(self, ctx, *args):
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
        help="",
        brief=""       
)
async def sudo(ctx, *args):
    if await bot.is_owner(ctx.author):
        if args:
            args = list(args)

            if args[0] == "say":
                if "--channel" in args:
                    channel = int(args[args.index("--channel")+1])
                    channel = await bot.fetch_channel(channel)
                    args.pop(args.index("--channel")+1)
                    args.pop(args.index("--channel"))
                    await channel.send(' '.join(args[1:]).strip())
                else: await ctx.send(' '.join(args[1:]).strip())
        else:
            await ctx.send("""
            We trust you have received the usual lecture from the local System
            Administrator. It usually boils down to these three things:

            #1) Respect the privacy of others.
            #2) Think before you type.
            #3) With great power comes great responsibility.
            """)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        if "search" in error.args[0]:
            await ctx.send("&search is deprecated, use &wikisearch. Do &help search for more info")
        else:
            await ctx.send("Command not found. Do &help for available commands")

bot.add_cog(WikipediaCommands(bot))
bot.add_cog(GoogleCommands(bot))
bot.add_cog(MyAnimeListCommands(bot))

bot.run(DISCORD_TOKEN)