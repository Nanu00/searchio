import json
import urllib.request as ureq
import discord, asyncio, random, datetime
from src.utils import Log, ErrorHandler

class xkcd:
    def __init__(self, num = ''):
        base_url = 'https://xkcd.com/'
        
        if num == 'random':
            self.num = random.randrange(1, xkcd('').num)
        elif str(num).isnumeric() or num == '':
            self.num = num
        else:
            raise ValueError("Input is not valid")
        
        self.url = base_url + str(self.num)
        json_url = self.url + '/info.0.json'
        
        mdata = json.load(ureq.urlopen(json_url))

        self.date = datetime.date(mdata['year'], mdata['month'], mdata['day'])
        self.img_url = mdata['img']
        self.title = mdata['title']
        self.alt = mdata['alt']
        self.num = mdata['num']

class xkcdSearch:
    def __init__(self, bot, ctx, searchQuery=None):
        self.searchQuery = searchQuery
        self.bot = bot
        self.ctx = ctx

    async def search(self):
        try:
            x = xkcd(searchQuery)
            
            embed = discord.Embed(title=x.title, description=x.alt, timestamp=x.date)
            embed.set_image(url=x.img_url)
            embed.set_footer(f"Requested by {self.ctx.author}")

            await self.ctx.send(embed=embed)
            # Log.appendToLog(self.ctx, "xkcd", self.searchQuery)

        except UserCancel as e:
            await self.ctx.send(f"Cancelled")
            return

        except ValueError:
            await self.ctx.send("Invalid input, aborting")
            return

        except asyncio.TimeOutError:
            await self.ctx.send(f"Search timed out. Aborting")
            return

        except Exception as e:
            await ErrorHandler(self.bot, self.ctx, e, 'youtube', self.searchQuery)
        finally: return

class UserCancel(Exception):
    pass
