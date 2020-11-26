async def async_iter(iterator):
    """Returns an async generator"""
    for item in iterator:
        yield item


async def spam_check(message):
    """Deletes users's messages if they are sent too quickly and warn them.
        "message" must be a discord.Message object"""
    spam_limit = 3  # in seconds
    users = {}  # users will be a dict containing dicts with {user_discord_id (int): datetime.datetime object} structure
    async for message in message.channel.history(limit=5):
        if message.author.id not in users:
            users.update({message.author.id: []})
        users[message.author.id].append(message.created_at)

    spam_result = []  # will be a list of user_discord_id's
    async for user_id in async_iter(users):
        if len(users[user_id]) < 3:  # the code will ignore the user if he hasn't enough messages in channel.history
            continue
        async for datetime_obj in async_iter(users[user_id]):
            datetime_obj_index = users[user_id].index(datetime_obj)
            if datetime_obj_index == 0:  # ignoring the first message
                continue
            else:
                result = users[user_id][datetime_obj_index - 1] - datetime_obj
                # if the result value is less than the spam_limit, the loop will continue. If the loop isn't broken with
                # the break statement the final else statement will append the user to the spam_result list.
                if result.total_seconds() <= spam_limit:
                    continue
                else:
                    break
        else:
            spam_result.append(user_id)

    message_error = ''
    if len(spam_result) > 0:
        async for user_id in async_iter(spam_result):
            if message.author.id == user_id:
                await message.delete()
                # the loop below will prevent the bot from sending more than one error message in discord but the
                # message deletion will continue
                async for message in message.channel.history(limit=20):
                    if message_error in message.content:
                        break
                else:
                    await message.channel.send(f'{message.author.mention} {message_error}')
        return True
    else:
        return False