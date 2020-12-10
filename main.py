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
            while True:  
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
                    await ctx.send(f'Sorry, I did not understand that. Please choose option (a number from 0-{len(result)-1})')
                    pass
            continue

        else:
            embed=discord.Embed(title=f'Wikipedia Article: {result.original_title}', description=result.summary, url=result.url)
            await ctx.send(embed=embed)
            break
        



@bot.command(
        name = 'scrape',
        help="WIP",
        brief="Scrape info from a Wikipedia article (WIP)"
    )

async def scrape(ctx, *args):
    await ctx.send('WIP')

bot.run(DISCORD_TOKEN)