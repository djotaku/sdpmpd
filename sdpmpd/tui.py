import main

from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static, Button, Pretty
from textual.containers import Horizontal, VerticalScroll

class PlaylistList(Static):
    config = main.get_config()

    list_of_playlists = ListView()
    playlist_dict = {}

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.list_of_playlists.clear()
        path = Path(self.config.playlist_location)
        playlists = list(path.glob('*'))
        self.playlist_dict = {item.name: item for item in playlists}
        for key in self.playlist_dict:
            self.list_of_playlists.append(ListItem(Label(key), name=key))

    def on_list_view_selected(self, event: ListView.Selected):
        playlist_name = event.item.name
        file_in_path = self.playlist_dict[playlist_name]
        playlist_params = main.get_playlist_parameters(self.config, playlist_name)
        #app.query_one(PlaylistInfo).our_pretty_data.update(playlist_params)
        app.query_one(PlaylistInfo).update_pretty(playlist_params)


    def compose(self) -> ComposeResult:
        yield self.list_of_playlists
        yield Button("Refresh Playlist", id="refresh_playlist", variant="success")


class PlaylistInfo(Static):
    config = main.get_config()
    our_pretty_data = Pretty(None, name="playlist_content", id="playlist_content")
    playlist_parameters = None

    def update_pretty(self, new_pretty):
        self.our_pretty_data.update(new_pretty)
        self.playlist_parameters = new_pretty

    def on_button_pressed(self, event: Button.Pressed) -> None:
        client = main.MPDClient()
        client.connect("localhost", 6600)
        compiled_search_results = main.compile_search_results(self.playlist_parameters, self.config, client)
        main.update_playlist(compiled_search_results, client)

        # still need to set up some kind of trigger so that the update playlist keeps running every second


    def compose(self) -> ComposeResult:
        yield self.our_pretty_data
        yield Button("Run Playlist", id="run_playlist")

class SmartDynamicPlaylistApp(App):




    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Header()
        yield Footer()
        yield Horizontal(VerticalScroll(PlaylistList(name="playlist")), VerticalScroll(PlaylistInfo(name="playlist_info")))


if __name__ == '__main__':
    app = SmartDynamicPlaylistApp()
    app.run()