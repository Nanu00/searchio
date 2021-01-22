from googlesearch import search
from src.log import commandlog
import discord
import asyncio

class GoogleSearch:
   def __init__(
      self,
      bot,
      ctx,
      language,
      searchQuery = None):

      self.searchQuery = searchQuery
      self.bot = bot
      self.ctx = ctx
      self.lang = language

   async def search(self):
      embed=discord.Embed(title=f"Google Search Results for '{self.searchQuery}'", description =
         ''.join([f"- {i} \n\n" for i in search(query=self.searchQuery, tld='com',lang=self.lang,num=5,stop=5,pause=1, safe="on")])
      )   
      embed.set_footer(text=f"Requested by {self.ctx.author}")
      await self.ctx.send(embed=embed)

      log = commandlog(self.ctx, "googlesearch result", f"{self.searchQuery}")
      log.appendToLog()
      return
