import discord
import asyncio
from src.log import commandlog
import json

class Sudo:
    def __init__(
        self,
        bot,
        ctx):

        self.bot = bot
        self.ctx = ctx

        #Reads settings of server
        with open('serverSettings.json', 'r') as data:
            self.serverSettings = json.load(data)

        if str(self.ctx.guild.id) not in self.serverSettings: #If settings entry does not exists, creates entry
            self.serverSettings[str(self.ctx.guild.id)] = {
                'blacklist': [],
                'adminrole': None,
                'sudoer': []
            }
            with open('serverSettings.json', 'w') as data:
                data.write(json.dumps(self.serverSettings, indent=4))

    async def adminrole(self, args):
        if len(args) > 1:
            self.serverSettings[str(self.ctx.guild.id)]['adminrole'] = args[1]
            adminRole = self.ctx.guild.get_role(int(args[1]))
            await self.ctx.send(f"'{adminRole.name}' is now the admin role")
        else:
            if len(self.serverSettings[str(self.ctx.guild.id)]['adminrole']) !=0:
                adminRole = self.ctx.guild.get_role(int(self.serverSettings[str(self.ctx.guild.id)]['adminrole']))
                await self.ctx.send(f"'{adminRole}' is the admin role")
            else:
                await self.ctx.send("No admin role has been set")
        
        return

    async def say(self, args):
        isOwner = await self.bot.is_owner(self.ctx.author)
        if isOwner == True and "--channel" in args:
            channel = int(args[args.index("--channel")+1])
            channel = await self.bot.fetch_channel(channel)
        elif "--channel" in args:
            channel = int(args[args.index("--channel")+1]) #Prevents non-owner sudoers from using bot in other servers
            channel = self.ctx.guild.get_channel(channel)

        if "--channel" in args:
                args.pop(args.index("--channel")+1)
                args.pop(args.index("--channel"))
                await channel.send(' '.join(args[1:]).strip())
        else: await self.ctx.send(' '.join(args[1:]).strip())

        return
    
    async def blacklist(self, args):
        if len(args) > 1:
            self.serverSettings[str(self.ctx.guild.id)]['blacklist'].append(str(args[1]))
            userinfo = await self.bot.fetch_user(int(args[1]))
            await self.ctx.send(f"'{str(userinfo)}' blacklisted")
        return
    
    async def whitelist(self, args):
        if len(args) > 1:
            try:
                self.serverSettings[str(self.ctx.guild.id)]['blacklist'].remove(str(args[1]))
                userinfo = await self.bot.fetch_user(int(args[1]))
                await self.ctx.send(f"'{str(userinfo)}' removed from blacklist")
            except ValueError:
                userinfo = await self.bot.fetch_user(int(args[1]))
                await self.ctx.send(f"'{str(userinfo)}' not in blacklist")
        return

    async def sudoer(self, args):
        if args[1] not in self.serverSettings[str(self.ctx.guild.id)]['sudoer']:
            self.serverSettings[str(self.ctx.guild.id)]['sudoer'].append(args[1])
            sudoerName = await self.bot.fetch_user(int(args[1]))
            await self.ctx.send(f"'{str(sudoerName)}' is now a sudoer")
        else: 
            sudoerName = await self.bot.fetch_user(int(args[1]))
            await self.ctx.send(f"'{str(sudoerName)}' is already a sudoer")
        return
    
    async def unsudoer(self, args):
        if args[1] in self.serverSettings[str(self.ctx.guild.id)]['sudoer']: 
            self.serverSettings[str(self.ctx.guild.id)]['sudoer'].remove(args[1])
            sudoerName = await self.bot.fetch_user(int(args[1]))
            await self.ctx.send(f"'{str(sudoerName)}' has been removed from sudo")
        else: 
            sudoerName = await self.bot.fetch_user(int(args[1]))
            await self.ctx.send(f"'{str(sudoerName)}' is not a sudoer")
        return

    async def sudo(self, args):
    
        #Checks if sudoer is owner
        isOwner = await self.bot.is_owner(self.ctx.author) 
        
        #Checks if sudoer is server owner
        if self.ctx.guild:
            isServerOwner = bool(self.ctx.author.id == self.ctx.guild.owner_id)
        else: isServerOwner = False

        #Checks if sudoer has the designated adminrole or is a sudoer
        try:
            hasAdmin = bool(self.serverSettings[str(self.ctx.guild.id)]['adminrole'] in [str(role.id) for role in self.ctx.author.roles])
            isSudoer = bool(str(self.ctx.author.id) in self.serverSettings[str(self.ctx.guild.id)]['sudoer'])
        except: pass
        
        if isOwner or isServerOwner or hasAdmin or isSudoer:
            if not args:
                await self.ctx.send("""
                We trust you have received the usual lecture from the local System Administrator. It usually boils down to these three things:
                #1) Respect the privacy of others.
                #2) Think before you type.
                #3) With great power comes great responsibility.
                """)
            elif args[0] == 'say':
                await self.say(args)
            elif args[0] == 'adminrole':
                await self.adminrole(args)
            elif args[0] == 'blacklist':
                await self.blacklist(args)
            elif args[0] == 'whitelist':
                await self.whitelist(args)
            elif args[0] == 'sudoer':
                await self.sudoer(args)
            elif args[0] == 'unsudoer':
                await self.unsudoer(args)
                
        else: await self.ctx.send(f"{self.ctx.author} is not in the sudoers file.  This incident will be reported.")

        with open('serverSettings.json', 'w') as data:
            data.write(json.dumps(self.serverSettings, indent=4))
        return