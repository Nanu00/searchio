import datetime as dt
from datetime import datetime
from src.sudo import Sudo
import csv, os, discord, asyncio

class commandlog():
    logFieldnames = ["Time", "Guild", "User", "User_Plaintext", "Command", "Args"]
    def __init__(self, ctx, command, *args):
        self.ctx = ctx
        self.command = command
        self.args = args
    
    def appendToLog(self):
        guild = "DM"
        if self.ctx.guild.id:
            guild = self.ctx.guild.id
        
        logDict = {
            "Time": datetime.utcnow().isoformat(),
            "Guild": guild,
            "User": self.ctx.author.id,
            "User_Plaintext": str(self.ctx.author),
            "Command": self.command,
            "Args": ' '.join(list(self.args)).strip()
        }
        lines = []
        with open("logs.csv", "r+", encoding='utf-8-sig') as file:
            for row in csv.DictReader(file):
                logTime = datetime.fromisoformat(row["Time"])
                if datetime.utcnow()-logTime < dt.timedelta(weeks=4):
                    lines.append(row)
        
        with open("logs.csv", "w", newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=self.logFieldnames)
            writer.writeheader()
            for items in lines:
                writer.writerow(items)
            writer.writerow(logDict)              
        return
    
    async def logRequest(self, bot):
        # if await bot.is_owner(self.ctx.author):
        #     dm = await self.ctx.author.create_dm()
        #     await dm.send(file=discord.File(r'logs.csv'))
        #     return
    
        if Sudo.isSudoer(bot, self.ctx):
            try:
                with open("logs.csv", 'r', encoding='utf-8-sig') as file: 
                    for line in csv.DictReader(file): 
                        if int(line["Guild"]) == self.ctx.guild.id:
                            with open(f"./src/cache/{self.ctx.guild}_guildLogs.csv", "a+", newline='', encoding='utf-8-sig') as newFile:
                                writer = csv.DictWriter(newFile, fieldnames=self.logFieldnames)
                                writer.writerow(line)

                dm = await self.ctx.author.create_dm()
                await dm.send(file=discord.File(f"./src/cache/{self.ctx.guild}_guildLogs.csv"))
                os.remove(f"./src/cache/{self.ctx.guild}_guildLogs.csv")
            
            except Exception as e:
                print(e)
            
            finally: 
                return
        
        else:
            try:
                with open("logs.csv", 'r', encoding='utf-8-sig') as file: 
                    for line in csv.DictReader(file): 
                        if int(line["User"]) == self.ctx.author.id:
                            with open(f"./src/cache/{self.ctx.author}_personalLogs.csv", "a+", newline='', encoding='utf-8-sig') as newFile:
                                writer = csv.DictWriter(newFile, fieldnames=self.logFieldnames)
                                writer.writerow(line)

                dm = await self.ctx.author.create_dm()
                await dm.send(file=discord.File(f"./src/cache/{self.ctx.author}_personalLogs.csv"))
                os.remove(f"./src/cache/{self.ctx.author}_personalLogs.csv")
            
            except Exception as e:
                print(e)
            
            finally: 
                return