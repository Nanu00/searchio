from src.log import commandlog
from bs4 import BeautifulSoup
import asyncio
import discord
import urllib3
import re
import random

class GoogleSearch:
   def __init__(
      self,
      bot,
      ctx,
      searchQuery = None):

      self.searchQuery = searchQuery
      self.bot = bot
      self.ctx = ctx

   async def search(self):
      def check(reaction, user):
         return user == self.ctx.author and str(reaction.emoji) in ["🗑️"]

      log = commandlog(self.ctx, "googlesearch", self.searchQuery)
      log.appendToLog()
      
      http = urllib3.PoolManager()
      locales = [
         "w+CAIQICILRGVsaGksSW5kaWE",
         "w+CAIQICIXU2hhbmdoYWksU2hhbmdoYWksQ2hpbmE",
         "w+CAIQICIfTmV3IFlvcmssTmV3IFlvcmssVW5pdGVkIFN0YXRlcw",
         "w+CAIQICIZS29sa2F0YSxXZXN0IEJlbmdhbCxJbmRpYQ", 
         "w+CAIQICIlUHJvdmluY2Ugb2YgQmFyY2Vsb25hLENhdGFsb25pYSxTcGFpbg",
         "w+CAIQICIlR3JlYXRlciBMb25kb24sRW5nbGFuZCxVbml0ZWQgS2luZ2RvbQ"
      ]
      url = "https://google.com/search?pws=0&q=" + self.searchQuery.replace(" ", "+") + f"&uule={random.choice(locales)}"
      response = http.request('GET', url)
      soup = BeautifulSoup(response.data, features="lxml")
      result_number = 3
      google_snippet_result = soup.find("div", {"id": "main"}).contents[result_number]

      breaklines = ["People also search for", "Episodes"]
      wrong_first_results = ["Did you mean: ", "Showing results for ", "Tip: ", "See results about", "Including results for ", "www.shutterstock.com "] # fuck shutterstock the filter doesn't even work atm

      log = commandlog(self.ctx, "googlesearch results", url)
      log.appendToLog()

      while any(map(lambda wrong_first_result: wrong_first_result in google_snippet_result.strings, wrong_first_results)):
         result_number+=1
         google_snippet_result = soup.find("div", {"id": "main"}).contents[result_number]

      divlist = [d for d in google_snippet_result.findAll('div') if not d.find('div')]
      printstring = ""
      for div in divlist:  # makes the text portion of the message by finding all strings in the snippet + formatting
         linestring = ""
         for string in div.stripped_strings:
            linestring += string + " "
         if linestring == "View all ":  # clean this part up
            linestring = ""

         if len(printstring+linestring+"\n") < 2000 and not any(map(lambda breakline: breakline in linestring, breaklines)):
            printstring += linestring + "\n"
         else:
            break

      embed = discord.Embed(title="Search results for: "+self.searchQuery[:233] + ("..." if len(self.searchQuery) > 233 else ""), description = re.sub("\n\n+", "\n\n", printstring))
      print(self.ctx.author.name + " searched for: "+self.searchQuery[:233])
      image = google_snippet_result.find("img")  # can also be done for full html (soup) with about same result
      # image = google_snippet_result.find("a")
      
      if image is not None:  # tries to add an image to the embed
         try:
            imgurl = re.findall("(?<=imgurl=).*(?=&imgrefurl)", image.parent.parent["href"])[0]
            if "encrypted" in imgurl:
                  imgurl = re.findall("(?<=imgurl=).*(?=&imgrefurl)", google_snippet_result.findAll("img")[1].parent.parent["href"])[0]
            # imgurl = re.findall("(?<=\=).*(?=&imgrefurl)", image["href"])[0]
            print(" image: " + imgurl)
            if "Images" in google_snippet_result.strings:
                  embed.set_image(url=imgurl)
            else:
                  embed.set_thumbnail(url=imgurl)
         except:
            print(" loading image failed")

      link_list = [a for a in google_snippet_result.findAll("a", href_="") if not a.find("img")]
      
      if len(link_list) != 0:  # tries to add a link to the embed
         # this adds a broken link for youtube videos :/ no fix afaik so just don't send link when youtube
         try:
            link = re.findall("(?<=url\?q=).*(?=&sa)", link_list[0]["href"])[0]
            print(" link: " + link)
            if "youtube" not in link:
                  embed.add_field(name="Relevant Links", value=link)
            else:
                  print(" failed yt link found")
                  embed.add_field(name="sorry not all youtube links work (yet) :/", value="youtube links are a broken mess send help")
         except:
            print(" adding link failed")
      
      embed.set_footer(text=f"Requested by {self.ctx.author}")
      embed.url = url
      searchresult = await self.ctx.send(embed=embed)

      try:
         await searchresult.add_reaction('🗑️')
         reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=60)
         if str(reaction.emoji) == '🗑️':
            await searchresult.delete()
            return
      
      except asyncio.TimeoutError as e: 
         await searchresult.clear_reactions()
      
      finally: 
         return