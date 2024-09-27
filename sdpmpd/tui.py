import main

from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static, Button, Pretty
from textual.containers import Horizontal, VerticalScroll

class PlaylistList(Static):
    config = main.get_config()

    list_of_playlists = ListView()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.list_of_playlists.clear()
        path = Path(self.config.playlist_location)
        playlists = list(path.glob('*'))
        playlist_dict = {item.name: item for item in playlists}
        for key in playlist_dict:
            self.list_of_playlists.append(ListItem(Label(key)))



    def compose(self) -> ComposeResult:
        yield self.list_of_playlists
        yield Button("Refresh Playlist", id="refresh_playlist", variant="success")


class PlaylistInfo(Static):

    our_pretty_data = Pretty(None, name="playlist_content", id="playlist_content")

    def on_list_view_selected(self, event: ListView.Selected):
        selected_playlist = event.item
        config = main.get_config()
        playlist_contents = main.get_playlist_parameters(config, selected_playlist.name)
        self.our_pretty_data.update(playlist_contents)

    def compose(self) -> ComposeResult:
        yield self.our_pretty_data

class SmartDynamicPlaylistApp(App):




    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Header()
        yield Footer()
        yield Horizontal(VerticalScroll(PlaylistList(name="playlist")), VerticalScroll(PlaylistInfo(name="playlist_info")))


if __name__ == '__main__':
    app = SmartDynamicPlaylistApp()
    app.run()