from mpd import MPDClient
from random import choice

def build_playlist(our_client: MPDClient, tag_type: str, search_term: str, strict: bool = False)->list[dict]:
    """Build a playlist that will be used to dynamically feed the MPD server.

    This may be combined with multiple results from this function to build out the playlist.
    """
    if strict:
        return our_client.find(tag_type, search_term)
    else:
        return our_client.search(tag_type, search_term)

if __name__ == '__main__':
    client = MPDClient()
    client.connect("localhost", 6600)
    playlist = build_playlist(client, "artist", "Anberlin")
    # check to see if playlist is empty
    status = client.status()
    if status['playlistlength'] == '0':
        # seed with 2 songs
        client.add(choice(playlist)['file'])
        client.add(choice(playlist)['file'])
    while True:
        status = client.status()
        if int(status['song']) >= int(status['playlistlength'])-1:
            client.add(choice(playlist)['file'])  # will eventually want to make sure not adding a song currently on the playlist or at least not within the last X number of songs.
    print(client.status())
    #for song in playlist:
    #    client.add(song['file'])
    #print(client.currentsong())
    #print(client.find("any", "Relient K"))
    #print(client.status())
    client.disconnect()