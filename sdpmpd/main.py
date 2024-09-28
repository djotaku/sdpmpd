from mpd import MPDClient
from random import choice
from xdgenvpy import XDGPedanticPackage
from json import loads
import sys
import requests
from pydantic import BaseModel, ValidationError
import pathlib


class DynamicPlaylist(BaseModel):
    tag_type: str  # eg artist, album, tag
    value: str  # what you're searching for
    strict: bool  # case-sensitive if true
    similar: bool | None = False  # if true, get similar artists from last.fm


class Config(BaseModel):
    playlist_location: str
    last_fm_key: str = None
    last_fm_secret: str = None


def search_database(our_client: MPDClient, tag_type: str, search_term: str, strict: bool = False) -> list[dict]:
    """Returns results that will be used to dynamically feed the MPD server.

    This may be combined with multiple results from this function to build out the playlist.
    """
    if strict:
        return our_client.find(tag_type, search_term)
    else:
        return our_client.search(tag_type, search_term)


def get_config() -> Config:
    xdg = XDGPedanticPackage('sdpmpd')
    return Config(**loads(pathlib.Path(f'{xdg.XDG_CONFIG_HOME}/config.json').read_text()))


def get_playlist_parameters(our_config: Config, our_playlist_file: str) -> DynamicPlaylist:
    with open(f'{our_config.playlist_location}/{our_playlist_file}') as playlist_file_handle:
        try:
            our_playlist_parameters = DynamicPlaylist(**loads(playlist_file_handle.read()))
        except FileNotFoundError:
            print("Couldn't find that playlist.")
            sys.exit()
        except ValidationError as e:
            print(e.errors())
            sys.exit()
    return our_playlist_parameters


def compile_search_results(our_playlist_parameters: DynamicPlaylist, our_config: Config, our_client:MPDClient)-> list:
    playlists = []
    if not our_playlist_parameters.similar:
        search_results = search_database(our_client, our_playlist_parameters.tag_type, our_playlist_parameters.value,
                                         our_playlist_parameters.strict)
        playlists.append(search_results)
    else:
        payload = {"artist": our_playlist_parameters.value, "api_key": our_config.last_fm_key, "format": "json"}
        request = requests.get("http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar", params=payload)
        similar_artists_result = request.json()
        similar_artists_list = similar_artists_result.get('similarartists').get('artist')
        similar_artists = [artist.get('name') for artist in similar_artists_list]
        similar_artists.append(our_playlist_parameters.value) # also contain the artist we searched for
        for artist in similar_artists:
            # purposely leaving this as a list of lists so that there can be more variety in the playlist
            # eg let's say you have lots of songs by artist A. If just combined them all, then it would randomly
            # select lots of songs by artist A to the detriment of the variety of the similar artists playlist
            if playlist := search_database(our_client, "artist", artist):
                playlists.append(playlist)
    return playlists

def update_playlist(search_results: list, our_client: MPDClient):
     status = our_client.status()
     playlist_length = int(status.get('playlistlength'))
     if  playlist_length == '0':
         # seed with 2 songs
         chosen_playlist = choice(search_results)
         our_client.add(choice(chosen_playlist)['file'])
         chosen_playlist = choice(search_results)
         our_client.add(choice(chosen_playlist)['file'])
         our_client.play()
     status = our_client.status()
     if status.get('state') == "stop" or int(status.get('song')) >= playlist_length - 1:
         chosen_playlist = choice(search_results)
         our_client.add(choice(chosen_playlist)[
                            'file'])  # will eventually want to make sure not adding a song currently on the playlist or at least not within the last X number of songs.
         if status.get('state') == "stop":
             our_client.play(playlist_length-1)

if __name__ == '__main__':
    config = get_config()
    playlist_file = sys.argv[1]
    playlist_parameters = get_playlist_parameters(config, playlist_file)
    client = MPDClient()
    client.connect("localhost", 6600)
    compiled_search_results = compile_search_results(playlist_parameters, config)
    while True:
        update_playlist(compiled_search_results)
    client.disconnect()
