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
    if not args:
        await ctx.send('Enter search query:')
        try:
            userquery = await bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout = 30) # 30 seconds to reply
            userquery = userquery.content
        except asyncio.TimeoutError:
            await ctx.send(f'{ctx.author.mention} Error: You took too long. Aborting')
    else: 
        userquery = args[0]
    search = query.Query(userquery)
    while True:
        result = search.searchwikipedia()
        if type(result) is list:
            embed=discord.Embed(title=f"Titles matching '{userquery}':", description=''.join([f'[{index}]: {value}\n' for index, value in enumerate(result)])) #1st 10 results
            await ctx.send(embed=embed)
            await ctx.send('Please choose option')
            try:
                input = await bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout = 30) # 30 seconds to reply 
                input = int(input.content)
                search.articletitle = result[input]
                search.choice = True
                break
            except asyncio.TimeoutError:
                await ctx.send(f'{ctx.author.mention} Error: You took too long. Aborting')
                break
            except:
                await ctx.send(f'Sorry, I did not understand that. Aborting')
                pass
            continue
        elif result == False: await ctx.send(f"No results found for '{search.articletitle}'.")
        else:
            embed=discord.Embed(title=f'Wikipedia Article: {result.original_title}', description=result.summary, url=result.url)
            await ctx.send(embed=embed)
            break
        
@bot.command(
        name = 'scrape',
        help=""" Command form: scrape <pagetitle> <arguments>
            Arguments (multiple are accepted): \n 
            `--categories` : Returns the categories that the page is a part of \n
            `--coordinates` : Returns the coordinates of the object in the page (if applicable) in lat,long format \n
            `--images` : Returns a list of URLs of the images on the page
            `--links` : Returns a list of titles referenced by the page
            `--references` : Returns a list of URLs of external links in the page
            `--sections` : Returns the table of contents of the page
            `--summary` : Returns a summary of the page""",
        brief="Scrape info from a Wikipedia article (WIP)"
    )

async def scrape(ctx, *args):
    # try:
    if not args:
        await ctx.send('Enter pagetitle and arguments:')
        try:
            args = await bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout = 30) # 30 seconds to reply
            args = userquery.content
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
        output['images'] = '\n'.join(result.images)
    if '--links' in args:
        output['links'] = '\n'.join(result.links)
    if '--references' in args:
        output['references'] = '\n'.join(result.references)
    if '--sections' in args:
        output['sections'] = '\n'.join(result.sections)
    if '--summary' in args:
        output['summary'] = str(result.summary)

    for key,value in output.items():
        embed = discord.Embed(title=key, description=value)
        await ctx.send(embed=embed)

    # except:
    #     await ctx.send(f'Sorry, I did not understand that.')


bot.run(DISCORD_TOKEN)