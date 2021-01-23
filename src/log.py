import datetime as dt
from datetime import datetime
import csv

class commandlog():
    def __init__(self, ctx, command, *args):
        self.ctx = ctx
        self.command = command
        self.args = args
    
    def appendToLog(self):
        logDict = {
            "Time": datetime.utcnow().isoformat(),
            "Guild": self.ctx.guild.id,
            "User": self.ctx.author.id,
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
            writer = csv.DictWriter(file, fieldnames=["Time", "Guild", "User", "Command", "Args"])
            writer.writeheader()
            for items in lines:
                writer.writerow(items)
            writer.writerow(logDict)              
        return