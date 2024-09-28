import main

from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static, Button, Pretty, Select, Input, Checkbox
from textual.containers import Horizontal, VerticalScroll

import json

class PlaylistList(Static):
    config = main.get_config()

    list_of_playlists = ListView()
    playlist_dict = {}

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        match button_id:
            case "refresh_playlist":
                self.list_of_playlists.clear()
                path = Path(self.config.playlist_location)
                playlists = list(path.glob('*'))
                self.playlist_dict = {item.name: item for item in playlists}
                for key in self.playlist_dict:
                    self.list_of_playlists.append(ListItem(Label(key), name=key))
            case "create_playlist":
                app.action_add_create_edit_playlist()

    def on_list_view_selected(self, event: ListView.Selected):
        playlist_name = event.item.name
        file_in_path = self.playlist_dict[playlist_name]
        playlist_params = main.get_playlist_parameters(self.config, playlist_name)
        app.action_add_playlist_info()
        app.query_one(PlaylistInfo).update_pretty(playlist_params)

    def compose(self) -> ComposeResult:
        yield Button("Refresh Playlist", id="refresh_playlist", variant="success")
        yield Button("Create Playlist", id="create_playlist", variant="primary")
        yield self.list_of_playlists

class EditPlaylistInfo(Static):
    config = main.get_config()
    client = main.MPDClient()
    tag = ""

    def save_playlist(self):
        tag = self.tag
        value = self.query_one("#value").value
        strict = self.query_one('#strict_checkbox').value
        similar = self.query_one('#similar_checkbox').value
        playlist_name = self.query_one('#playlist_name').value
        with open(f"{self.config.playlist_location}/{playlist_name}", 'w') as playlist_file:
            data = json.dumps({"tag_type": tag, "value": value, "strict": strict, "similar":similar})
            playlist_file.write(data)



    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        match button_id:
            case "save_playlist":
                self.save_playlist()
            case "close_playlist_editor":
                app.action_close_create_edit_playlist()

    def compose(self) -> ComposeResult:
        yield Label("Tag")
        self.client.connect("localhost", 6600)
        potential_tags = self.client.tagtypes()
        self.client.disconnect()
        yield Select.from_values(potential_tags)
        yield Input(placeholder="Value to search on", id="value")
        yield Label("If strict selected, case sensitive search")
        yield Checkbox("strict", id="strict_checkbox")
        yield Label("If similar selected, will search last.fm for similar artists")
        yield Checkbox("similar", id="similar_checkbox")
        yield Input(placeholder="name for playlist", id="playlist_name")
        yield Button("Save playlist", id="save_playlist")
        yield Button("Close Playlist Editor", id="close_playlist_editor")

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        self.tag = str(event.value)

class PlaylistInfo(Static):
    config = main.get_config()
    our_pretty_data = Pretty(None, name="playlist_content", id="playlist_content")
    playlist_parameters = None
    compiled_search_results = None
    client = main.MPDClient()

    def on_mount(self):
        self.update_timer = self.set_interval(1, self.add_next_song, pause=True)

    def update_pretty(self, new_pretty):
        self.our_pretty_data.update(new_pretty)
        self.playlist_parameters = new_pretty

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        match button_id:
            case "run_playlist":
                self.client.connect("localhost", 6600)
                self.compiled_search_results = main.compile_search_results(self.playlist_parameters, self.config,
                                                                           self.client)
                main.update_playlist(self.compiled_search_results, self.client)
                self.client.disconnect()
                self.update_timer.resume()
            case "stop_playlist":
                self.update_timer.pause()

    def add_next_song(self):
        self.client.connect("localhost", 6600)
        main.update_playlist(self.compiled_search_results, self.client)
        self.client.disconnect()

    def compose(self) -> ComposeResult:
        yield self.our_pretty_data
        yield Button("Run Playlist", id="run_playlist")
        yield Button("Stop Playlist", id="stop_playlist")
        yield Button("Edit Playlist", id="edit_playlist")


class SmartDynamicPlaylistApp(App):

    app_config = main.get_config()
    playlist_info = None
    edit_playlist = None

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Header()
        yield Footer()
        yield Horizontal(VerticalScroll(PlaylistList(name="playlist")),
                         VerticalScroll(id="playlist_area"))

    def action_add_playlist_info(self) -> None:
        if not self.playlist_info:
            self.playlist_info = PlaylistInfo(name="playlist_info")
            self.query_one("#playlist_area").mount(self.playlist_info)

    def action_add_create_edit_playlist(self):
        if not self.edit_playlist:
            self.edit_playlist = EditPlaylistInfo(name="edit_playlist")
            self.query_one("#playlist_area").mount(self.edit_playlist)

    def action_close_create_edit_playlist(self):
        self.query("EditPlaylistInfo").remove()
        self.edit_playlist = None

if __name__ == '__main__':
    app = SmartDynamicPlaylistApp()
    app.run()
