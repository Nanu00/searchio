import random, discord, asyncio

class AprilFools:
    def __init__(self, bot, ctx):
        self.bot = bot
        self.ctx = ctx
        self.captchaEmojis = {'apple': '🍎', 'ski': '⛷️', 'bomb':'💣', 'fire':'🔥', 'heart':'❤️', 'party':'🎉', 'poop':'💩', 'syringe':'💉', 'dog':'🐕', 'unicorn':'🦄'}
    
    async def CAPTCHA(self):
        def check(reaction, user):
            return user == self.ctx.author and str(reaction.emoji) in list(self.captchaEmojis.values())
        
        if random.random() < 0.25:
            emojiName, emoji = random.choice(list(self.captchaEmojis.items()))
            embed = discord.Embed(title="CAPTCHA", description=f"You have been randomly selected to submit a CAPTCHA test. Please react with the '{emojiName}' emoji to continue.")
            message = await self.ctx.send(embed=embed)
            try: 
                tempEmojiList = {emoji}
                while len(tempEmojiList) < 4:
                    tempEmojiList.add(random.choice(list(self.captchaEmojis.values())))
                
                for emojis in tempEmojiList:
                    await message.add_reaction(emojis)

                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=60)
                await message.delete()
                if str(reaction.emoji) == emoji:
                    return True
                else: return False
            except asyncio.TimeoutError as e: 
                await message.clear_reactions()
    
        else: return True