# sdpmpd - Smart Dynamic Playlists for MPD

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


Phases
- dynamic playlists <- done
- anything better than time.sleep to check for playlist changes in the loop?
- Using last.fm and/or spotify to enable "similar artist" mode <- done
- smart, dynamic playlists <- done
- use Pydantic to validate the playlist files
- prevent songs already on the playlist from showing up, unless it's been a long time since they were played.
- complex, smart, and dynamic playlists (ie using AND or NOT)
- Create GUI
