# This will save the user's steam link and show active rooms when the command is used

import requests


class Lobby:
    def __init__(self, steam_profiles, steam_key):
        """steam_profiles will contain a dict with {discord_id: steam_id} structure"""
        self.steam_profiles = steam_profiles
        self.STEAM_KEY = steam_key
        self.GET_SUMMARIES = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'

    @staticmethod
    def convert_url_to_steamid(url, steam_key):
        """Parse a direct link to a profile or a steam custom name and returns its steamid64 number"""
        if '/' in url:
            if url[-1] == '/':
                url = url[:-1]
            url = url.split('/')[-1]
        if url.isdecimal():
            return url
        response = requests.get(f'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={steam_key}&vanityurl={url}')
        return response.json()['response']['steamid']

    def get_single_user_data(self, steamid):
        """Gets a player's summary information without parsing"""
        response = requests.get(f'{self.GET_SUMMARIES}?key={self.STEAM_KEY}&steamids={steamid}')
        try:
            return response.json()['response']['players'][0]
        except IndexError:
            raise IndexError('steamid not found!')

    def get_player_status(self, steamid):
        """Returns a more readable and more specific information about the given steam player"""
        player = self.get_single_user_data(steamid)

        return {
            player['personaname']: {
                'playing': player['gameextrainfo'] if 'gameextrainfo' in player else False,
                'steamid': player['steamid'],
                'has_lobby': player['lobbysteamid'] if 'lobbysteamid' in player else False,
                'visibility': player['communityvisibilitystate']
            }
        }

    def get_all_current_lobbies(self):
        """Gets all active lobbies from all users registered in steam_profiles"""
        players_id = [self.steam_profiles[player] for player in self.steam_profiles]
        response = requests.get(f'{self.GET_SUMMARIES}?key={self.STEAM_KEY}&steamids={players_id}')
        steam_players = response.json()['response']['players']
        lobbies = {}

        for player in steam_players:
            if 'lobbysteamid' in player:
                gameextrainfo = player['gameextrainfo']
                lobbysteamid = player['lobbysteamid']
                personaname = player['personaname']
                steamid = player['steamid']

                if gameextrainfo in lobbies:
                    if lobbysteamid in lobbies[gameextrainfo]:
                        lobbies[gameextrainfo][lobbysteamid].update({personaname: steamid})
                    else:
                        lobbies[gameextrainfo].update({lobbysteamid: {personaname: steamid}})
                else:
                    lobbies.update({gameextrainfo: {lobbysteamid: {personaname: steamid}}})

        return lobbies
