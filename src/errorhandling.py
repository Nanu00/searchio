from src.log import commandlog
import traceback, random, csv, discord, asyncio

async def ErrorHandler(bot, ctx, error):
    with open("logs.csv", 'r', encoding='utf-8-sig') as file: 
        doesErrorCodeMatch = False
        errorCode = "%06x" % random.randint(0, 0xFFFFFF)
        while doesErrorCodeMatch == False:
            for line in csv.DictReader(file): 
                if line["Command"] == error:
                    if line["Args"] == errorCode:
                        doesErrorCodeMatch = True
                        errorCode = "%06x" % random.randint(0, 0xFFFFFF)
                        pass
            break
    
    log = commandlog(ctx, "error", errorCode)
    log.appendToLog()
    
    errorLoggingChannel = await bot.fetch_channel(829172391557070878)
    await errorLoggingChannel.send(f"```Error {errorCode}\nIn Guild: {ctx.guild.id}:\n{traceback.format_exc()}```")

    embed = discord.Embed(description=f"An unknown error has occured. Please try again later. \nError Code {errorCode}")
    errorMsg = await ctx.send(embed=embed)
    asyncio.sleep(60)
    errorMsg.delete()
    return