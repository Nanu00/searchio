import wikipedia
import discord
import asyncio
from src.log import commandlog

class WikipediaSearch:
    def __init__(
        self,
        bot,
        ctx,
        language,
        searchQuery = None):

        self.searchQuery = searchQuery
        self.bot = bot
        self.ctx = ctx
        wikipedia.set_lang(language)
    
    async def search(self):
        msg = []
        result = wikipedia.search(self.searchQuery)
        while True:
            result = [result[x:x+10] for x in range(0, len(result), 10)]
            pages = len(result)
            cur_page = 1
            
            if len(result) != 1:
                embed=discord.Embed(title=f"Titles matching '{self.searchQuery}'\n Page {cur_page}/{pages}:", description=
                    ''.join([f'[{index}]: {value}\n' for index, value in enumerate(result[cur_page-1])]))
                embed.set_footer(text=f"Requested by {self.ctx.author}")
                msg.append(await self.ctx.send(embed=embed))
                await self.bot.wait_until_ready()
                await msg[0].add_reaction('◀️')
                await msg[0].add_reaction('▶️')
                msg.append(await self.ctx.send('Please choose option'))
            
            else:
                embed=discord.Embed(title=f"Titles matching '{self.searchQuery}':", description=
                    ''.join([f'[{index}]: {value}\n' for index, value in enumerate(result[0])]))
                embed.set_footer(text=f"Requested by {self.ctx.author}")
                msg.append(await self.ctx.send(embed=embed))
                msg.append(await self.ctx.send('Please choose option'))

            def check(reaction, user):
                return user == self.ctx.author and str(reaction.emoji) in ["◀️", "▶️"]

            while True:
                try: #checks for user input or reaction input.
                    emojitask = asyncio.create_task(self.bot.wait_for("reaction_add", check=check, timeout=30))
                    responsetask = asyncio.create_task(self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author, timeout=30))
                    waiting = [emojitask,responsetask]
                    done, waiting = await asyncio.wait(waiting, return_when=asyncio.FIRST_COMPLETED) # 30 seconds wait either reply or react
                    
                    if emojitask in done: # if reaction input, change page
                        reaction, user = emojitask.result()
                        if str(reaction.emoji) == "▶️" and cur_page != pages:
                            cur_page += 1
                            embed=discord.Embed(title=f"Titles matching '{self.searchQuery}'\nPage {cur_page}/{pages}:", description=
                                ''.join([f'[{index}]: {value}\n' for index, value in enumerate(result[cur_page-1])]))
                            embed.set_footer(text=f"Requested by {self.ctx.author}")
                            await msg[0].edit(embed=embed)
                            await msg[0].remove_reaction(reaction, user)
                        
                        elif str(reaction.emoji) == "◀️" and cur_page > 1:
                            cur_page -= 1
                            embed=discord.Embed(title=f"Titles matching '{self.searchQuery}'\n Page {cur_page}/{pages}:", description=
                                ''.join([f'[{index}]: {value}\n' for index, value in enumerate(result[cur_page-1])]))
                            embed.set_footer(text=f"Requested by {self.ctx.author}")
                            await msg[0].edit(embed=embed)
                            await msg[0].remove_reaction(reaction, user)
                        
                        else:
                            await msg[0].remove_reaction(reaction, user)
                            # removes reactions if the user tries to go forward on the last page or
                            # backwards on the first page
                    
                    elif responsetask in done:
                        input = responsetask.result() 
                        if input.content == 'cancel':
                            raise UserCancel
                        elif input.content not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                            continue
                        input = int(input.content)
                        try:
                            self.searchQuery = result[cur_page-1][input]
                            page = wikipedia.page(self.searchQuery)
                            summary = page.summary[:page.summary.find('. ')+1]
                            embed=discord.Embed(title=f'Wikipedia Article: {page.original_title}', description=summary, url=page.url) #outputs wikipedia article
                            embed.set_footer(text=f"Requested by {self.ctx.author}")
                            await self.ctx.send(embed=embed)
                            
                            log = commandlog(self.ctx, "wikisearch result", f"{page.original_title}")
                            log.appendToLog()

                            for message in msg:
                                await message.delete()

                            return

                        except wikipedia.DisambiguationError as e:
                            result = str(e).split('\n')
                            result.pop(0)

                            for message in msg:
                                await message.delete()

                            break  
                except UserCancel as e:
                    log = commandlog(self.ctx, "wikisearch cancel")
                    log.appendToLog()

                    for message in msg:
                        await message.delete()

                    await self.ctx.send(f"Cancelled")
                    return
                
                except asyncio.TimeoutError:
                    for message in msg:
                        await message.delete()

                    log = commandlog(self.ctx, "wikisearch timeout")
                    log.appendToLog()

                    await self.ctx.send(f"Search timed out. Aborting")
                    return

                except Exception as e:
                    log = commandlog(self.ctx, "wikisearch error", f"{str(e)}")
                    log.appendToLog()

                    for message in msg:
                        await message.delete()
                    
                    if e:
                        await self.ctx.send(f"Error: {e}\nAborted.")
                        return
                    else:
                        await self.ctx.send(f"Error: Unknown\nAborted.")
                        return

    async def lang(self):
        #Multiple page system
        languages = list(wikipedia.languages().items())
        languages = [languages[x:x+10] for x in range(0, len(languages), 10)]
        for index1, content in enumerate(languages):
            for index2, codes in enumerate(content):
                content[index2] = ': '.join(codes) + '\n'
            languages[index1] = ''.join([i for i in content])
        pages = len(languages)
        cur_page = 1
        embed = discord.Embed(title=f'Page {cur_page}/{pages}', description=languages[cur_page-1])
        embed.set_footer(text=f"Requested by {self.ctx.author}")
        msg = await self.ctx.send(embed=embed)
        await self.bot.wait_until_ready()
        await msg.add_reaction('◀️')
        await msg.add_reaction('▶️')
        
        def check(reaction, user):
            return user == self.ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
        
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=15, check=check)
                # waiting for a reaction to be added - times out after 30 seconds

                if str(reaction.emoji) == "▶️" and cur_page != pages:
                    cur_page += 1
                    embed = discord.Embed(title=f'Page {cur_page}/{pages}', description=languages[cur_page-1])
                    embed.set_footer(text=f"Requested by {self.ctx.author}")
                    await msg.edit(embed=embed)
                    await msg.remove_reaction(reaction, user)
                
                elif str(reaction.emoji) == "◀️" and cur_page > 1:
                    cur_page -= 1
                    embed = discord.Embed(title=f'Page {cur_page}/{pages}', description=languages[cur_page-1])
                    embed.set_footer(text=f"Requested by {self.ctx.author}")
                    await msg.edit(embed=embed)
                    await msg.remove_reaction(reaction, user)
                
                else:
                    await msg.remove_reaction(reaction, user)
                    # removes reactions if the user tries to go forward on the last page or
                    # backwards on the first page
            except asyncio.TimeoutError:
                await msg.delete()
                break

class UserCancel(Exception):
    pass