from mpd import MPDClient
from random import choice
from xdgenvpy import XDGPedanticPackage
from json import loads
import sys
import requests
from pydantic import BaseModel, ValidationError


class DynamicPlaylist(BaseModel):
    tag_type: str #eg artist, album, tag
    value: str # what you're searching for
    strict: bool # case-sensitive if true
    similar: bool = False # if true, get similar artists from last.fm

def build_playlist(our_client: MPDClient, tag_type: str, search_term: str, strict: bool = False)->list[dict]:
    """Build a playlist that will be used to dynamically feed the MPD server.

    This may be combined with multiple results from this function to build out the playlist.
    """
    if strict:
        return our_client.find(tag_type, search_term)
    else:
        return our_client.search(tag_type, search_term)

import pathlib
if __name__ == '__main__':
    xdg = XDGPedanticPackage('sdpmpd')
    config = loads(pathlib.Path(f'{xdg.XDG_CONFIG_HOME}/config.json').read_text())
    last_fm_api = config.get('last_fm_key')
    last_fm_secret = config.get('last_fm_secret')
    playlist_file = sys.argv[1]
    with open(f'{config["playlist_location"]}/{playlist_file}') as playlist_file_handle:
        try:
            playlist_parameters = DynamicPlaylist(**loads(playlist_file_handle.read()))
        except FileNotFoundError:
            print("Couldn't find that playlist.")
            sys.exit()
        except ValidationError as e:
            print(e.errors())
            sys.exit()
    client = MPDClient()
    client.connect("localhost", 6600)
    if not playlist_parameters.similar:
        playlist = build_playlist(client, playlist_parameters.tag_type, playlist_parameters.value, playlist_parameters.strict)
        status = client.status()
        if status['playlistlength'] == '0':
            # seed with 2 songs
            client.add(choice(playlist)['file'])
            client.add(choice(playlist)['file'])
        while True:
            status = client.status()
            if int(status['song']) >= int(status['playlistlength']) - 1:
                client.add(choice(playlist)[
                               'file'])  # will eventually want to make sure not adding a song currently on the playlist or at least not within the last X number of songs.
    else:
        payload = {"artist": playlist_parameters.value, "api_key": last_fm_api, "format":"json"}
        request = requests.get("http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar", params=payload)
        similar_artists_result = request.json()
        similar_artists_list = similar_artists_result.get('similarartists').get('artist')
        similar_artists = [artist.get('name') for artist in similar_artists_list]
        similar_artists.append(playlist_parameters.value)
        # start off with the artist we searched for
        playlists = []
        for artist in similar_artists:
            # purposely leaving this as a list of lists so that there can be more variety in the playlist
            # eg let's say you have lots of songs by artist A. If just combined them all, then it would randomly
            # select lots of songs by artist A to the detriment of the variety of the similar artists playlist
            if playlist := build_playlist(client, "artist", artist):
                playlists.append(playlist)
        # check to see if playlist is empty
        status = client.status()
        if status['playlistlength'] == '0':
            # seed with 2 songs
            chosen_playlist = choice(playlists)
            client.add(choice(chosen_playlist)['file'])
            chosen_playlist = choice(playlists)
            client.add(choice(chosen_playlist)['file'])
            client.play()
        while True:
            status = client.status()
            if int(status['song']) >= int(status['playlistlength'])-1:
                chosen_playlist = choice(playlists)
                client.add(choice(chosen_playlist)['file']) # will eventually want to make sure not adding a song currently on the playlist or at least not within the last X number of songs.
        print(client.status())
    client.disconnect()