import random
from discord.ext.commands import Bot
from discord import Embed


bot = Bot(command_prefix='your bot command prefix here')

message_channel_id = 728024060495265847  # where the message is
message_id = 767440780544835594  # message where the reactions are
cmd_user_id = 243332147379830785  # user allowed to use the command
announcement_channel_id = 728024060495265847  # self explanatory


@bot.event
async def on_ready():
    global users
    users = []
    print('Ready!')
    channel = bot.get_channel(message_channel_id)
    message = await channel.fetch_message(message_id)

    for reaction in message.reactions:
        async for user in reaction.users():
            users.append(user.id)

        print(f'{reaction.emoji} : {reaction.count}')
        print(users)


@bot.command()
async def roll(ctx):
    if ctx.author.id != cmd_user_id:  # only cmd_user can use the command
        return

    announcement_channel = bot.get_channel(announcement_channel_id)
    cmd_user = bot.get_user(cmd_user_id)
    winner = bot.get_user(random.choice(users))

    embed = Embed(
        title='',
        description=f'by {cmd_user.mention}',
        colour=winner.color
    )
    embed.add_field(name='Winner:', value=winner.mention)
    embed.set_image(url=winner.avatar_url)

    return await announcement_channel.send(embed=embed)


bot.run('bot token here')
