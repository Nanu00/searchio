from discord import emoji
from discord.message import Message
import query
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import asyncio

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix='$')

async def on_message(message):
    if message.author == bot.user:
        return

@bot.command(
        name = 'search',
        help='Add a query after $search to search through the Wikipedia databases. Follow the prompts!',
        brief='Search for a Wikipedia article'
    )
async def search(ctx, *args):
    if not args: #checks if search is empty
        await ctx.send('Enter search query:') #if empty, asks user for search query
        try:
            userquery = await bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout = 30) # 30 seconds to reply
            userquery = userquery.content
        except asyncio.TimeoutError:
            await ctx.send(f'{ctx.author.mention} Error: You took too long. Aborting') #aborts if timeout
    else: 
        userquery = ' '.join(args).strip() #turns multiword search into single string
    search = query.Query(userquery)
    
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
                    if len(result) != 1:
                        await msg.add_reaction('◀️')
                        await msg.add_reaction('▶️')
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
                                embed=discord.Embed(title=f"Titles matching '{search.articletitle}'\n Page {cur_page}/{pages}:", description=
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
                            input = int(input.content)
                            search.articletitle = result[cur_page-1][input] #updates query to user choice
                            search.choice = True
                            break

                    except asyncio.TimeoutError:
                        raise
                    except:
                        await ctx.send(f'Sorry, I did not understand that. Please pick a valid choice: 0 to {len(result)}')
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
                break
        
        except asyncio.TimeoutError:
            await ctx.send(f'{ctx.author.mention} Error: You took too long. Aborting')
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

        for key,value in output.items():
            embed = discord.Embed(title=key, description=value)
            embed.set_footer(text=f"Requested by {ctx.author}")
            await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f'Sorry, there is an error with processing your request.')

@bot.command(
        name = 'lang',
        help="""Lists Wikipedia's supported wikis in ISO codes. Common language codes are: \n
        zh: 中文 \n
        es: Español \n
        en: English \n
        pt: Português \n
        hi: हिन्दी \n
        bn: বাংলা \n
        ru: русский \n
        """,
        brief="List supported languages (WIP)"
)
async def lang(ctx):
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
        
bot.run(DISCORD_TOKEN)