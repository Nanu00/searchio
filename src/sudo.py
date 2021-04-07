import discord, asyncio, json, textwrap, difflib

class Sudo:
    def __init__(
        self,
        bot,
        ctx,
        serverSettings):

        self.bot = bot
        self.ctx = ctx
        self.serverSettings = serverSettings

    @staticmethod
    def settingsCheck(serverSettings, serverID):
        serverID = str(serverID)
        if serverID not in serverSettings.keys():
            serverSettings[serverID] = {}
        if 'blacklist' not in serverSettings[serverID].keys():
            serverSettings[serverID]['blacklist'] = []
        if 'commandprefix' not in serverSettings[serverID].keys():
            serverSettings[serverID]['commandprefix'] = '&'
        if 'adminrole' not in serverSettings[serverID].keys():
            serverSettings[serverID]['adminrole'] = None
        if 'sudoer' not in serverSettings[serverID].keys():
            serverSettings[serverID]['sudoer'] = []
        if 'safesearch' not in serverSettings[serverID].keys():
            serverSettings[serverID]['safesearch'] = False
        for searchEngines in ['wikipedia', 'scholar', 'google', 'mal', 'youtube']:
            if searchEngines not in serverSettings[serverID].keys():
                serverSettings[serverID][searchEngines] = True
        
        with open('serverSettings.json', 'w') as data:
            data.write(json.dumps(serverSettings, indent=4))
        return

    @staticmethod
    def isSudoer(bot, ctx, serverSettings=None):
        if serverSettings == None:
            with open('serverSettings.json', 'r') as data:
                serverSettings = json.load(data)

        #Checks if sudoer is owner
        isOwner = ctx.author.id == bot.owner_id
        
        #Checks if sudoer is server owner
        if ctx.guild:
            isServerOwner = ctx.author.id == ctx.guild.owner_id
        else: isServerOwner = False

        #Checks if sudoer has the designated adminrole or is a sudoer
        try:
            hasAdmin = True if serverSettings[str(ctx.guild.id)]['adminrole'] in [str(role.id) for role in ctx.author.roles] else False
            isSudoer = True if str(ctx.author.id) in serverSettings[str(ctx.guild.id)]['sudoer'] else False
        except: pass
        finally: return any([isOwner, isServerOwner, hasAdmin, isSudoer])

    def printPrefix(self):
        if self.ctx == None or self.ctx.guild == None:
            return '&'
        else: return self.serverSettings[str(self.ctx.guild.id)]['commandprefix']

    async def userSearch(self, search):
        try:
            if search.isnumeric():
                user = self.ctx.guild.get_member(int(search))
            else:
                user = self.ctx.guild.get_member_named(search)
            
            if user == None:
                await self.ctx.send(f"No user named {search} was found in the guild")
                pass
            else: return user
        except Exception:
            raise

    async def echo(self, args):
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
        if 'blacklist' not in self.serverSettings[str(self.ctx.guild.id)].keys():
            self.serverSettings[str(self.ctx.guild.id)]['blacklist'] = []

        if len(args) > 1:
            try:
                user = await self.userSearch(' '.join(args))
                self.serverSettings[str(self.ctx.guild.id)]['blacklist'].append(str(user.id))
                await self.ctx.send(f"{str(user)} blacklisted")
            except Exception as e:
                pass
        return
    
    async def whitelist(self, args):
        if 'blacklist' not in self.serverSettings[str(self.ctx.guild.id)].keys():
            self.serverSettings[str(self.ctx.guild.id)]['blacklist'] = []

        if len(args) > 1:
            try:
                user = await self.userSearch(' '.join(args))
                self.serverSettings[str(self.ctx.guild.id)]['blacklist'].remove(str(user.id))
                await self.ctx.send(f"{str(user)} removed from blacklist")
            except ValueError:
                await self.ctx.send(f"{str(user)} not in blacklist")
            except Exception as e:
                pass
        return

    async def sudoer(self, args):
        if self.ctx.author.id == self.bot.owner_id or self.ctx.author.id == self.ctx.guild.owner_id:
            try:
                user = await self.userSearch(' '.join(args))
                if str(user.id) not in self.serverSettings[str(self.ctx.guild.id)]['sudoer']:
                    self.serverSettings[str(self.ctx.guild.id)]['sudoer'].append(str(user.id))
                    await self.ctx.send(f"{str(user)} is now a sudoer")
                else: 
                    await self.ctx.send(f"{str(user)} is already a sudoer")
                    
            except Exception as e:
                pass
            finally:
                return
    
    async def unsudoer(self, args):
        if self.ctx.author.id == self.bot.owner_id or self.ctx.author.id == self.ctx.guild.owner_id:
            try:
                user = await self.userSearch(' '.join(args))
                if str(user.id) in self.serverSettings[str(self.ctx.guild.id)]['sudoer']:
                    self.serverSettings[str(self.ctx.guild.id)]['sudoer'].remove(str(user.id))
                    await self.ctx.send(f"{str(user)} has been removed from sudo")
                else: 
                    await self.ctx.send(f"{str(user)} is not a sudoer")
                    
            except Exception as e:
                pass
            finally:
                return
    
    async def config(self, args):
        def check(reaction, user):
            return user == self.ctx.author and str(reaction.emoji) in ['✅', '❌']
        adminrole = self.serverSettings[str(self.ctx.guild.id)]['adminrole']
        if adminrole != None:
            adminrole = self.ctx.guild.get_role(int(adminrole)) 
        if len(args) == 0:
            embed = discord.Embed(title="Guild Configuration")
            embed.add_field(name="Administration", value=f"""
                ` Adminrole:` {adminrole.name if adminrole != None else 'None set'}
                `Safesearch:` {'✅' if self.serverSettings[str(self.ctx.guild.id)]['safesearch'] == True else '❌'}
                `    Prefix:` {self.serverSettings[str(self.ctx.guild.id)]['commandprefix']}""")
            embed.add_field(name="Search Engines", value=f"""
                `Wikipedia:` {'✅' if self.serverSettings[str(self.ctx.guild.id)]['wikipedia'] == True else '❌'}
                `  Scholar:` {'✅' if self.serverSettings[str(self.ctx.guild.id)]['scholar'] == True else '❌'}
                `   Google:` {'✅' if self.serverSettings[str(self.ctx.guild.id)]['google'] == True else '❌'}
                `      MAL:` {'✅' if self.serverSettings[str(self.ctx.guild.id)]['mal'] == True else '❌'}
                `  Youtube:` {'✅' if self.serverSettings[str(self.ctx.guild.id)]['youtube'] == True else '❌'}""")
            
            embed.set_footer(text=f"Do {self.printPrefix()}config [setting] to change a specific setting")
            await self.ctx.send(embed=embed)
        elif args[0].lower() in ['wikipedia', 'scholar', 'google', 'myanimelist', 'youtube', 'safesearch']:
            embed = discord.Embed(title=args[0].capitalize(), description=f"{'✅' if self.serverSettings[str(self.ctx.guild.id)][args[0].lower()] == True else '❌'}")
            embed.set_footer(text=f"React with ✅/❌ to enable/disable")
            message = await self.ctx.send(embed=embed)
            try:
                await message.add_reaction('✅')
                await message.add_reaction('❌')

                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=60)
                if str(reaction.emoji) == '✅':
                    self.serverSettings[str(self.ctx.guild.id)][args[0].lower()] = True
                elif str(reaction.emoji) == '❌':
                    self.serverSettings[str(self.ctx.guild.id)][args[0].lower()] = False
                await message.delete()
                await self.ctx.send(f"{args[0].capitalize()} is {'enabled' if self.serverSettings[str(self.ctx.guild.id)][args[0].lower()] == True else 'disabled'}")
                return
            except asyncio.TimeoutError as e: 
                await message.clear_reactions()
        elif args[0].lower() == 'adminrole':
            if not args[1]:
                embed = discord.Embed(title='Adminrole', description=f"{await self.ctx.guild.get_role(int(adminrole)) if adminrole != None else 'None set'}")
                embed.set_footer(text=f"Reply with the roleID of the role you want to set")
                message = await self.ctx.send(embed=embed)

                try: 
                    userresponse = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author, timeout=30)
                    await userresponse.delete()
                    await message.delete()
                    response = userresponse.content
                except asyncio.TimeoutError as e:
                    return
            else: 
                errorCount = 0
                errorMsg = None
                response = args[1]
                while errorCount <= 1:
                    if errorMsg != None:
                        await errorMsg.delete()

                    try: 
                        adminrole = self.ctx.guild.get_role(int(response))
                        self.serverSettings[str(self.ctx.guild.id)]['adminrole'] = response
                        await self.ctx.send(f"'{adminrole.name}' is now the admin role")
                        break
                    except Exception as e:
                        errorMsg = await self.ctx.send(f"{response} is not a valid roleID. Please edit your message or try again")
                        messageEdit = await self.bot.wait_for('message_edit', check=lambda var, m: m.author == self.ctx.author, timeout=60)
                        response = ''.join([li for li in difflib.ndiff(messageEdit[0].content, messageEdit[1].content) if '+' in li]).replace('+ ', '')
                        errorCount += 1
                        pass
                return
                    
        elif args[0].lower() == 'prefix':
            if not args[1]:
                embed = discord.Embed(title='Prefix', description=f"{self.serverSettings[str(self.ctx.guild.id)]['commandprefix']}")
                embed.set_footer(text=f"Reply with the prefix that you want to set")
                message = await self.ctx.send(embed=embed)

                try: 
                    userresponse = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author, timeout=30)
                    await userresponse.delete()
                    await message.delete()
                    response = userresponse.content

                except asyncio.TimeoutError as e:
                    return
            else: response = args[1]
            
            self.serverSettings[str(self.ctx.guild.id)]['commandprefix'] = response
            await self.ctx.send(f"'{response}' is now the guild prefix")
            return
                
    async def sudo(self, args):
        if args:
            if args[0] == 'echo':
                await self.echo(args)
            elif args[0] == 'blacklist':
                del args[0]
                await self.blacklist(args)
            elif args[0] == 'whitelist':
                del args[0]
                await self.whitelist(args)
            elif args[0] == 'sudoer':
                del args[0]
                await self.sudoer(args)
            elif args[0] == 'unsudoer':
                del args[0]
                await self.unsudoer(args)
            elif args[0] == 'safesearch':
                del args[0]
                await self.safesearch(args)
            elif args[0] == 'config':
                del args[0]
                await self.config(args)
            else:
                await self.ctx.send(f"'{args[0]}' is not a valid command.")
        else:
            await self.ctx.send(
                textwrap.dedent("""\
                We trust you have received the usual lecture from the local System Administrator. It usually boils down to these three things:
                #1) Respect the privacy of others.
                #2) Think before you type.
                #3) With great power comes great responsibility."""))
            

        with open('serverSettings.json', 'w') as data:
            data.write(json.dumps(self.serverSettings, indent=4))
        return