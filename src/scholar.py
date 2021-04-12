from scholarly import scholarly
from src.utils import Log, ErrorHandler
import discord, asyncio, random

class ScholarSearch:
    def __init__(
        self,
        bot,
        ctx,
        args,
        searchQuery = None):

        self.searchQuery = searchQuery
        self.bot = bot
        self.ctx = ctx
        self.args = args
    
    async def search(self):
        try:
            await asyncio.sleep(random.uniform(0,2))
            if 'author' in self.args:
                result = next(scholarly.search_author(self.searchQuery))
            elif 'cite' in self.args:
                result = scholarly.search_pubs(self.searchQuery)
                result = scholarly.bibtex(next(result))
            else: 
                result = next(scholarly.search_pubs(self.searchQuery))

            Log.appendToLog(self.ctx, "scholar", self.searchQuery)

            def check(reaction, user):
                return user == self.ctx.author and str(reaction.emoji) in ["🗑️"]

            if not result:
                await self.ctx.send(f"Sorry, no results were found for {self.searchQuery}")
            
            elif 'cite' in self.args:
                searchresult = await self.ctx.send(f"""```
                {result}
                ```""")
                
                Log.appendToLog(self.ctx, "scholar result", 'citation')

                try:
                    await searchresult.add_reaction('🗑️')
                    reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=60)
                    if str(reaction.emoji) == '🗑️':
                        await searchresult.delete()
                
                except asyncio.TimeoutError as e: 
                    await searchresult.clear_reactions()
                
                except Exception as e:
                    await searchresult.delete()

            elif result['container_type'] == 'Author':
                embed=discord.Embed(title=result['name'])                  
                embed.add_field(name="Scholar ID", value=result['scholar_id'], inline=True)
                embed.add_field(name="Affiliation", value=result['affiliation'], inline=True)
                embed.add_field(name="Email Domain", value=result['email_domain'] if 'email_domain' in result.keys() else 'None', inline=True)
                embed.add_field(name="Cited By", value=result['cited_by'] if 'cited_by' in result.keys() else 'None', inline=True)
                embed.add_field(name="Interests", value=', '.join(result['interests']).strip() if 'interests' in result.keys() else 'None')

                embed.set_thumbnail(url=result['url_picture'])
                embed.set_footer(text=f"Requested by {self.ctx.author}")
                searchresult = await self.ctx.send(embed=embed)
                
                Log.appendToLog(self.ctx, "scholar result", result['name'])
                
                try:
                    await searchresult.add_reaction('🗑️')
                    reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=60)
                    if str(reaction.emoji) == '🗑️':
                        await searchresult.delete()
                
                except asyncio.TimeoutError as e: 
                    await searchresult.clear_reactions()
                
                except Exception as e:
                    await searchresult.delete()

            elif result['container_type'] == 'Publication':
                embed=discord.Embed(title=result['bib']['title'], 
                                description=result['bib']['abstract'], 
                                url=result['eprint_url'] if 'eprint_url' in result.keys() else result['pub_url'])
                embed.add_field(name="Authors", value=', '.join(result['bib']['author']).strip(), inline=True) 
                
                embed.add_field(name="Publisher", value=result['bib']['venue'], inline=True)                
                embed.add_field(name="Publication Year", value=result['bib']['pub_year'], inline=True)
                embed.add_field(name="Cited By", value=result['num_citations'] if 'num_citations' in result.keys() else '0', inline=True)
                
                embed.add_field(name="Related Articles", value=f'https://scholar.google.com{result["url_related_articles"]}', inline=True)

                embed.set_footer(text=f"Requested by {self.ctx.author}")
                searchresult = await self.ctx.send(embed=embed)
                
                Log.appendToLog(self.ctx, "scholar result", result['bib']['title'])
                
                try:
                    await searchresult.add_reaction('🗑️')
                    reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=60)
                    if str(reaction.emoji) == '🗑️':
                        await searchresult.delete()
                
                except asyncio.TimeoutError as e: 
                    await searchresult.clear_reactions()
                
                except Exception as e:
                    await searchresult.delete()

        except Exception as e:
            await ErrorHandler(self.bot, self.ctx, e, 'scholar', self.searchQuery)
        finally: return