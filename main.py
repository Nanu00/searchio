from discord import emoji
from discord.ext.commands.core import command
from discord.message import Message
import query
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import asyncio
from datetime import datetime

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix='$')
logDict = {}
class commandlog():
    def __init__(self, ctx, command, *args):
        self.ctx = ctx
        self.command = command
        self.args = args
    
    def appendToLog(self):
        currentLogKey = datetime.utcnow().replace(microsecond=0)
        logDict[currentLogKey.strftime("%y%m%d-%H%M%S")] = {
            "Time": currentLogKey,
            "Guild": self.ctx.guild.id,
            "User": str(self.ctx.author),
            "Command": self.command,
            "Args": ' '.join(list(self.args)).strip()
        }
    
        if len(logDict) > 50:
            del logDict[min(logDict.keys())]

        return
    
    def sendLog(ctx, isOwner:bool = False):
        if len(logDict) > 50:
            del logDict[min(logDict.keys())]

        if isOwner == False:
            embed=discord.Embed(title=f"Logs {datetime.utcnow().strftime('%y%m%d')}")
            time = ""
            user = ""
            command = ""
            args = ""

            for values in logDict.values():
                if values["Guild"] == ctx.guild.id and values["Time"].strftime("%y%m%d") == datetime.utcnow().strftime("%y%m%d"):
                    time += f"{values['Time'].strftime('%H%M%S')}\n"
                    user += f"{values['User']}\n"
                    command += f"{values['Command']}\n"
                    if values["Args"]:
                        args += f"{values['Args']}\n"
                    else: args += "\n"
            
            embed.add_field(name="Time", value=time, inline=True)
            embed.add_field(name="User", value=user, inline=True)
            embed.add_field(name="Command", value=command, inline=True)
            embed.add_field(name="Args", value=args, inline=True)

            return embed

async def on_message(message):
    if message.author == bot.user:
        return
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="command prefix '$'"))

@bot.command(
        name = 'search',
        help="""Add a query after $search to search through the Wikipedia databases. Send 'cancel' to cancel search.\n
            Multilanguage support with --lang followed by an ISO 3166 country code. See $lang for a full list of supported languages""",
        brief='Search for a Wikipedia article'
    )
async def search(ctx, *args):
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
        language = 'en'
        if '--lang' in args:
            language = args[args.index('--lang')+1]
            del args[args.index('--lang'):]
        userquery = ' '.join(args).strip() #turns multiword search into single string
        search = query.Query(userquery, language)
    log = commandlog(ctx, "search", userquery)
    log.appendToLog()

    while True:
        try:
            result = search.searchwikipedia()
            if type(result) is list: #creates a list of returned results
                
                result = [result[x:x+10] for x in range(0, len(result), 10)]
                pages = len(result)
                cur_page = 1
                if len(result) != 1:
                    embed=discord.Embed(title=f"Titles matching '{search.articletitle}'\n Page {cur_page}/{pages}:", description=
                        ''.join([f'[{index}]: {value}\n' for index, value in enumerate(result[cur_page-1])]))
                    embed.set_footer(text=f"Requested by {ctx.author}")
                    msg = await ctx.send(embed=embed)
                    await bot.wait_until_ready()
                    await msg.add_reaction('◀️')
                    await msg.add_reaction('▶️')
                    await ctx.send('Please choose option')
                else:
                    embed=discord.Embed(title=f"Titles matching '{search.articletitle}':", description=
                        ''.join([f'[{index}]: {value}\n' for index, value in enumerate(result[0])]))
                    embed.set_footer(text=f"Requested by {ctx.author}")
                    msg = await ctx.send(embed=embed)
                    await ctx.send('Please choose option')
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
        
                while True:
                    try: #checks for user input or reaction input.
                        emojitask = asyncio.create_task(bot.wait_for("reaction_add", check=check, timeout=30))
                        responsetask = asyncio.create_task(bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=30))
                        waiting = [emojitask,responsetask]
                        done, waiting = await asyncio.wait(waiting, return_when=asyncio.FIRST_COMPLETED) # 30 seconds wait either reply or react
                        
                        if emojitask in done: # if reaction input, change page
                            reaction, user = emojitask.result()
                            if str(reaction.emoji) == "▶️" and cur_page != pages:
                                cur_page += 1
                                embed=discord.Embed(title=f"Titles matching '{search.articletitle}'\nPage {cur_page}/{pages}:", description=
                                    ''.join([f'[{index}]: {value}\n' for index, value in enumerate(result[cur_page-1])]))
                                embed.set_footer(text=f"Requested by {ctx.author}")
                                await msg.edit(embed=embed)
                                await msg.remove_reaction(reaction, user)
                            
                            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                                cur_page -= 1
                                embed=discord.Embed(title=f"Titles matching '{search.articletitle}'\n Page {cur_page}/{pages}:", description=
                                    ''.join([f'[{index}]: {value}\n' for index, value in enumerate(result[cur_page-1])]))
                                embed.set_footer(text=f"Requested by {ctx.author}")
                                await msg.edit(embed=embed)
                                await msg.remove_reaction(reaction, user)
                            
                            else:
                                await msg.remove_reaction(reaction, user)
                                # removes reactions if the user tries to go forward on the last page or
                                # backwards on the first page
                        elif responsetask in done:
                            input = responsetask.result() 
                            if input.content == 'cancel':
                                raise UserCancel
                            input = int(input.content)
                            search.articletitle = result[cur_page-1][input] #updates query to user choice
                            search.choice = True
                            break

                    except asyncio.TimeoutError:
                        raise
                    except UserCancel:
                        raise
                    except:
                        await ctx.send(f'Sorry, I did not understand that. Please pick a valid choice: 0 to {len(result[cur_page])}')
                        pass
                        continue
            
            elif result == False: 
                await ctx.send(f"No results found for '{search.articletitle}'.") #triggered when no results are found
                break

            else:
                summary = result.summary[:result.summary.find('. ')+1]
                embed=discord.Embed(title=f'Wikipedia Article: {result.original_title}', description=summary, url=result.url) #outputs wikipedia article
                embed.set_footer(text=f"Requested by {ctx.author}")
                await ctx.send(embed=embed)
                log = commandlog(ctx, "search result", f"{result.original_title}")
                log.appendToLog()
                break
        
        except asyncio.TimeoutError:
            await ctx.send(f'{ctx.author.mention} Error: You took too long. Aborting')
            log = commandlog(ctx, "error", "timeout")
            log.appendToLog()
            break

        except UserCancel as e:
            await ctx.send('Aborting')
            log = commandlog(ctx, "error", f"unknown/userabort: {e}")
            log.appendToLog()
            break
    
    emojitask.cancel()
        
@bot.command(
        name = 'scrape',
        help=""" Command form: scrape <pagetitle> <arguments>
            Arguments (multiple are accepted): \n 
            --categories : Returns the categories that the page is a part of \n
            --coordinates : Returns the coordinates of the object in the page (if applicable) in lat,long format \n
            --images : Returns a list of URLs of the images on the page
            --links : Returns a list of titles referenced by the page
            --references : Returns a list of URLs of external links in the page
            --sections : Returns the table of contents of the page
            --summary : Returns a summary of the page""",
        brief="Scrape info from a Wikipedia article"
    )

async def scrape(ctx, *args):
    try:
        if not args:
            await ctx.send('Enter pagetitle and arguments:')
            try:
                args = await bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout = 30) # 30 seconds to reply
                args = args.content
            except asyncio.TimeoutError:
                await ctx.send(f'{ctx.author.mention} Error: You took too long. Aborting')
                log.appendToLog(ctx, "error", "timeout")
        pagetitle = ''
        for value in args:
            if '--' not in value:
                pagetitle += value + ' '
            
        scrape = query.Query(pagetitle.rstrip())
        result = scrape.articlescrape()
        output = {}

        args = [value for value in args if '--' in value]

        if '--categories' in args:
            output['categories'] = ','.join(result.categories)
        if '--coordinates' in args:
            output['coordinates'] = ','.join(result.coordinates)
        if '--images' in args:
            try:
                output['images'] = '\n'.join(result.images)
            except Exception as e:
                output['images'] = e
        if '--links' in args:
            output['links'] = '\n'.join(result.links)
        if '--references' in args:
            output['references'] = '\n'.join(result.references)
        if '--sections' in args:
            output['sections'] = "Wikipedia doesn't release sections at this time" #'\n'.join(result.sections)
        if '--summary' in args:
            output['summary'] = str(result.summary) if len(result.summary) < 2000 else result.summary[:1997]+'...' #checks if summary is too long

        log = commandlog(ctx, "scrape", args)
        log.appendToLog()

        for key,value in output.items():
            embed = discord.Embed(title=key, description=value)
            embed.set_footer(text=f"Requested by {ctx.author}")
            await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f'Sorry, there is an error with processing your request.')
        log = commandlog(ctx, "error", f"unknown/userabort: {e}")
        log.appendToLog()

@bot.command(
        name = 'lang',
        help="""Lists Wikipedia's supported wikis in ISO codes. Common language codes are:
        zh: 中文
        es: Español
        en: English
        pt: Português
        hi: हिन्दी
        bn: বাংলা
        ru: русский
        """,
        brief="List supported languages (WIP)"
)
async def lang(ctx):
    log = commandlog(ctx, "lang")
    log.appendToLog()
    #Multiple page system
    result = query.Query(None)
    languages = list(result.languages().items())
    languages = [languages[x:x+10] for x in range(0, len(languages), 10)]
    for index1, content in enumerate(languages):
        for index2, codes in enumerate(content):
            content[index2] = ': '.join(codes) + '\n'
        languages[index1] = ''.join([i for i in content])
    pages = len(languages)
    cur_page = 1
    embed = discord.Embed(title=f'Page {cur_page}/{pages}', description=languages[cur_page-1])
    embed.set_footer(text=f"Requested by {ctx.author}")
    msg = await ctx.send(embed=embed)
    await bot.wait_until_ready()
    await msg.add_reaction('◀️')
    await msg.add_reaction('▶️')
    
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
    
    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=15, check=check)
            # waiting for a reaction to be added - times out after 30 seconds

            if str(reaction.emoji) == "▶️" and cur_page != pages:
                cur_page += 1
                embed = discord.Embed(title=f'Page {cur_page}/{pages}', description=languages[cur_page-1])
                embed.set_footer(text=f"Requested by {ctx.author}")
                await msg.edit(embed=embed)
                await msg.remove_reaction(reaction, user)
            
            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                cur_page -= 1
                embed = discord.Embed(title=f'Page {cur_page}/{pages}', description=languages[cur_page-1])
                embed.set_footer(text=f"Requested by {ctx.author}")
                await msg.edit(embed=embed)
                await msg.remove_reaction(reaction, user)
            
            else:
                await msg.remove_reaction(reaction, user)
                # removes reactions if the user tries to go forward on the last page or
                # backwards on the first page
        except asyncio.TimeoutError:
            await msg.delete()
            break

@bot.command(
        name = 'log'
        
)
@commands.is_owner()
async def logging(ctx): 
    await ctx.send(embed=commandlog.sendLog(ctx))
    
@logging.error
async def logging_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        print(error)

bot.run(DISCORD_TOKEN)