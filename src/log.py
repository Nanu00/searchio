import datetime as dt
from datetime import datetime
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
        if await bot.is_owner(ctx.author):
            dm = await ctx.author.create_dm()
            await dm.send(file=discord.File(r'logs.csv'))
    
        else:
            with open("logs.csv", 'r', encoding='utf-8-sig') as file: 
                for line in csv.DictReader(file): 
                    if int(line["User"]) == self.ctx.author.id:
                        with open(f"{self.ctx.author.id}_personal_logs.csv", "a+", newline='', encoding='utf-8-sig') as newFile:
                            writer = csv.DictWriter(newFile, fieldnames=self.logFieldnames)
                            try: 
                                writer.writerow(line)
                            except Exception as e:
                                print(e)

            dm = await self.ctx.author.create_dm()
            await dm.send(file=discord.File(f"{self.ctx.author.id}_personal_logs.csv"))
            os.remove(f"{self.ctx.author.id}_personal_logs.csv")