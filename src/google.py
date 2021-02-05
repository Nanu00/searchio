from src.log import commandlog
from bs4 import BeautifulSoup
import asyncio
import discord
import urllib3
import re

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

      def linkUnicodeParse(link: str):
         for linkIndex in [i for i, ltr in enumerate(link) if ltr == "%"]: #replaces Unicode codepoints w/ characters
            character = chr(int(link[linkIndex+1:linkIndex+3], 16))
            link = link[:linkIndex] + f'{character}  ' + link[linkIndex+3:]
            
         return link.replace(" ", "")

      log = commandlog(self.ctx, "googlesearch", self.searchQuery)
      log.appendToLog()

      http = urllib3.PoolManager()
      url = "https://google.com/search?pws=0&q=" + self.searchQuery.replace(" ", "+") + f"&uule=w+CAIQICI5TW91bnRhaW4gVmlldyxTYW50YSBDbGFyYSBDb3VudHksQ2FsaWZvcm5pYSxVbml0ZWQgU3RhdGVz&num=1"
      response = http.request('GET', url)
      soup = BeautifulSoup(response.data, features="lxml")
      result_number = 3
      google_snippet_result = soup.find("div", {"id": "main"}).contents[result_number]

      breaklines = ["People also search for", "Episodes"]
      wrong_first_results = ["Did you mean: ", "Showing results for ", "Tip: ", "See results about", "Including results for ", "www.shutterstock.com ", "Related searches"] # fuck shutterstock the filter doesn't even work atm

      log = commandlog(self.ctx, "googlesearch results", url)
      log.appendToLog()

      while any(map(lambda wrong_first_result: wrong_first_result in google_snippet_result.strings, wrong_first_results)):
         result_number+=1
         google_snippet_result = soup.find("div", {"id": "main"}).contents[result_number]

      printstring = ""
      for div in [d for d in google_snippet_result.findAll('div') if not d.find('div')]:  # makes the text portion of the message by finding all strings in the snippet + formatting
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
      image = google_snippet_result.find("img")  # can also be done for full html (soup) with about same result.
      # image = google_snippet_result.find("a")
      
      if image is not None:  # tries to add an image to the embed
         try:
            imgurl = linkUnicodeParse(re.findall("(?<=imgurl=).*(?=&imgrefurl)", image.parent.parent["href"])[0])
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
            link = linkUnicodeParse(re.findall("(?<=url\?q=).*(?=&sa)", link_list[0]["href"])[0])

            embed.add_field(name="Relevant Link", value=link)
            print(" link: " + link)

         except:
            print(" adding link failed")
      
      embed.set_footer(text=f"Requested by {self.ctx.author}")
      embed.url = url
      try:
         searchresult = await self.ctx.send(embed=embed)
      except Exception as e:
         print(e)

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

class UserCancel(Exception):
   pass