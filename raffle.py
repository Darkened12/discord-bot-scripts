import random
from discord.ext.commands import Bot
from discord import Embed


bot = Bot(command_prefix='your bot command prefix here')

message_channel_id = 000000000000000000  # where the message is
message_id = 000000000000000000  # message where the reactions are
cmd_user_id = 000000000000000000  # user allowed to use the command
announcement_channel_id = 000000000000000000  # self explanatory


async def async_iter(iterator):
    """Returns an async generator"""
    for item in iterator:
        yield item


@bot.event
async def on_ready():
    global users
    users = []
    print('Ready!')
    channel = bot.get_channel(message_channel_id)
    message = await channel.fetch_message(message_id)

    async for reaction in async_iter(message.reactions):
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