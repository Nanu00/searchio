import discord
import asyncio
from src.log import commandlog
import random 

class Sudo:
    def __init__(
        self,
        bot,
        ctx):

        self.bot = bot
        self.ctx = ctx

    async def sudo(self, args):
        async def authorized(self):
            isOwner = await self.bot.is_owner(self.ctx.author)
            isServerOwner = bool(self.ctx.author == self.ctx.guild.owner)
            print(isOwner, isServerOwner)
            return any(f"{isOwner}, {isServerOwner}")

        auth = authorized()
        if auth:
            print(args)
            if args:
                if args[0] == "say":
                    if "--channel" in args:
                        channel = int(args[args.index("--channel")+1])
                        channel = await self.bot.fetch_channel(channel)
                        args.pop(args.index("--channel")+1)
                        args.pop(args.index("--channel"))
                        await channel.send(' '.join(args[1:]).strip())
                    else: await self.ctx.send(' '.join(args[1:]).strip())
                # elif args[0] == "adminrole":

            else:
                await self.ctx.send("""
                We trust you have received the usual lecture from the local System Administrator. It usually boils down to these three things:

                #1) Respect the privacy of others.
                #2) Think before you type.
                #3) With great power comes great responsibility.
                """)