from youtube_search import YoutubeSearch as ytsearch
from src.utils import Log, ErrorHandler
import discord, asyncio, random

class YoutubeSearch:
    def __init__(
        self,
        bot,
        ctx,
        searchQuery = None):

        self.searchQuery = searchQuery
        self.bot = bot
        self.ctx = ctx
    
    async def search(self):
        try:
            msg = []
            async with self.ctx.typing():
                try:
                    await asyncio.sleep(random.uniform(0,2))
                    result = ytsearch(self.searchQuery, max_results=10).to_dict()
                    resultTitles = [video['title'] for video in result]
                
                except Exception as e:
                    await self.ctx.send(f"Error: {e}\nAborted.")
                    return

                Log.appendToLog(self.ctx, "ytsearch", self.searchQuery)
                
                embed=discord.Embed(title=f"Titles matching '{self.searchQuery}':", description=
                    ''.join([f'[{index}]: {value}\n' for index, value in enumerate(resultTitles)]))
                embed.set_footer(text=f"Requested by {self.ctx.author}")
                msg.append(await self.ctx.send(embed=embed))
                msg.append(await self.ctx.send('Please choose option [0-9]'))
            try:
                while True: 
                    input = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author, timeout=30)
                    await input.delete()
                    if input.content == 'cancel':
                        raise UserCancel
                    elif input.content not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                        await msg[-1].delete()
                        del msg[-1]
                        msg.append(await self.ctx.send('Invalid response. Please choose option [0-9]'))
                        continue
                    else:
                        result = result[int(input.content)]
                        Log.appendToLog(self.ctx, "ytsearch", result['title'])

                        for message in msg:
                            await message.delete()

                        embed=discord.Embed(title=result['title'], 
                            description=result['long_desc'] if 'long_desc' in result.keys() else 'None', 
                            url=f"https://www.youtube.com{result['url_suffix']}")                  
                        embed.add_field(name="Channel", value=result['channel'], inline=True)
                        embed.add_field(name="Duration", value=result['duration'], inline=True)
                        embed.add_field(name="Views", value=result['views'], inline=True)
                        embed.add_field(name="Publish Time", value=result['publish_time'], inline=True)

                        embed.set_thumbnail(url=result['thumbnails'][0])
                        embed.set_footer(text=f"Requested by {self.ctx.author}")
                        searchresult = await self.ctx.send(embed=embed)

                        def check(reaction, user):
                            return user == self.ctx.author and str(reaction.emoji) in ["🗑️"]

                        try:
                            await searchresult.add_reaction('🗑️')
                            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=60)
                            if str(reaction.emoji) == '🗑️':
                                await searchresult.delete()
                        
                        except asyncio.TimeoutError as e: 
                            await searchresult.clear_reactions()
                        
                        except Exception as e:
                            await searchresult.delete()

            except UserCancel as e:
                await self.ctx.send(f"Cancelled")
                return
                    
            except asyncio.TimeoutError:
                await self.ctx.send(f"Search timed out. Aborting")
                return

        except Exception as e:
            await ErrorHandler(self.bot, self.ctx, e)
        finally: return

class UserCancel(Exception):
    pass