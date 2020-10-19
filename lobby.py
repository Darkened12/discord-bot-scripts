# This will save the user's steam link and show active rooms when the command is used

import requests
import json
from bs4 import BeautifulSoup
from discord.ext.commands import Bot
from discord import Embed


bot = Bot(command_prefix='your command prefix here')


class LinkNotFound(Exception):
    pass


game_check = 'BlazBlue Centralfiction'  # if you want the command to work for only 1 game

@bot.event
async def on_ready():
    print('Ready!')


@bot.command()
async def lobby(ctx, *, args):
    def valid_link(link):
        """Only steam links is wanted"""
        if 'https://steamcommunity.com/' not in link:
            return False
        else:
            return True

    def create_soup_obj(link):
        """This line will be called a lot"""
        return BeautifulSoup(requests.get(link).content, 'html.parser')

    def get_game_name(soup_obj):
        """Gets the game the user is currently playing on steam"""
        game_name = soup_obj.find('div', {'class': 'profile_in_game_name'})
        if game_name is not None:
            return game_name.get_text()
        else:
            return False

    def is_ingame(soup_obj):
        """Checks if the user is playing anything"""
        test = soup_obj.find('div', {'class':'profile_in_game_name'})
        if test is None:
            return False
        else:
            return True

    def get_lobby_link(soup_obj):
        """Gets the steam room link"""
        a_tag = soup_obj.find('a', {'class': 'btn_green_white_innerfade btn_small_thin'})
        if a_tag is not None:
            return a_tag.get('href')
        else:
            raise LinkNotFound

    with open('steam_profiles.json', 'r') as file:
        steam_profiles = json.load(file)

    if 'register' in args.lower():
        deleted = False
        for user_id in steam_profiles:
            if ctx.author.id == int(user_id):
                del steam_profiles[user_id]
                deleted = True
                break
        else:
            if not valid_link(args):
                return await ctx.send("Link inválido")
            steam_profiles.update({ctx.author.id: args.replace('register ', '')})

        with open('steam_profiles.json', 'w') as file:
            json.dump(obj=steam_profiles, fp=file, indent=2)

        if not deleted:
            return await ctx.send('Registered!')
        else:
            return await ctx.send('Deleted!')

    elif 'all' in args.lower():
        await ctx.send('Just a moment...')
        embed = Embed(
            title='All BBCF active rooms:'
        )
        at_least_one_room = False
        for user in steam_profiles:
            user_obj = bot.get_user(int(user))
            steam_link = steam_profiles[user]
            soup_obj = create_soup_obj(steam_link)

            if get_game_name(soup_obj) == game_check:  # you may want to remove this line if you want multiple games
                try:
                    lobby_link = get_lobby_link(soup_obj)
                except LinkNotFound:
                    continue
                embed.add_field(name=user_obj.name, value=lobby_link)
                at_least_one_room = True
            else:
                continue
        if at_least_one_room:
            return await ctx.send(embed=embed)
        else:
            return await ctx.send("It seems like there's no active room at the moment!")

    else:
        for member in ctx.guild.members:
            if args.lower() in member.name.lower():
                chosen_user = member
                break
        else:
            return await ctx.send('User not found!')

        for user in steam_profiles:
            if int(user) == chosen_user.id:
                break
        else:
            return await ctx.send(f'{chosen_user.name} is not registered!')
        steam_link = create_soup_obj(steam_profiles[str(chosen_user.id)])

        if not is_ingame(steam_link):
            return await ctx.send("Isn't playing right now!")
        elif get_game_name(steam_link) != game_check:  # you may want to remove this line if you want multiple games
            return await ctx.send(f'Only works with {game_check} at the moment!')

        try:
            embed = Embed(
                title=f"{chosen_user.display_name}'s room:",
                description=get_lobby_link(steam_link),
                colour=chosen_user.color
            )
        except LinkNotFound:
            return await ctx.send('There was an error when trying to get the link!')
        embed.set_thumbnail(url=chosen_user.avatar_url)
        return await ctx.send(embed=embed)

bot.run('token')
