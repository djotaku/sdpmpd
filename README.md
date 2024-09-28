# sdpmpd - Smart Dynamic Playlists for MPD

First go to last.fm and get your API key if you want to use similar artists. 

config.json v1:
```json
{
  "last_fm_key": "something",
  "last_fm_secret": "something",
  "playlist_location": "path_to_playlists"
}
```

playlist file v1:

```json
{
  "tag_type": "eg: album, artist, tag, etc",
  "value": "the name of the artist or album or tag",
  "strict": true,
  "similar": true
}
```
Create a playlist at the past in your config. For now while there isn't a package:

Go into the sdpmpd folder and launch with:

python main.py name_of_playlist

## Currently Implemented
- dynamic playlists
- Using last.fm to enable "similar artist" mode
- smart, dynamic playlists
- Basic TUI that runs a playlist

## TODO
- CLI: anything better than time.sleep to check for playlist changes in the loop?
- Create TUI with Textual
  - figure out how to keep firing off the update_playlist function
  - figure out how to stop that so that you can switch playlists
  - make button only appear after a playlist selected?
  - UI for editing/creating playlists
- prevent songs already on the playlist from showing being added, unless it's been a long time since they were played.
- complex, smart, and dynamic playlists (ie using AND, OR, NOT)