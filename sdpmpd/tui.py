import main

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static
from textual.containers import Horizontal, VerticalScroll

class PlaylistList(Static):
    def compose(self) -> ComposeResult:
        yield ListView()

class SmartDynamicPlaylistApp(App):
    config = main.get_config()

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Header()
        yield Footer()
        yield Horizontal(VerticalScroll(PlaylistList(name="playlist")), VerticalScroll())

        test_dict = {"key1": "value_1", "key_2": "value_2"}
        playlist = self.query_one(PlaylistList)
        for key in test_dict:
            playlist.append(ListItem(Label(key)))

if __name__ == '__main__':
    app = SmartDynamicPlaylistApp()
    app.run()