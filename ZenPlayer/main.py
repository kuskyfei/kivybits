"""
ZenPlayer
=========

ZenPlayer is a minimal audio/video player that explores the ability of the
Kivy framework.

"""
__author__ = 'ZenCODE'

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty
from os import path, listdir
#from kivy.core.audio import SoundLoader
from audioplayer import SoundLoader

Builder.load_string('''
<MediaButton>:
    image: image
    Image:
        id: image
        pos_hint: {'x': 0, 'y': 0}
        size_hint: 1, 1
        on_touch_down: self.collide_point(*args[1].pos) and root.dispatch('on_click')
''')


class MediaButton(FloatLayout):
    """
    A pretty, shiny button showing the player controls
    """
    source = StringProperty('')
    image = ObjectProperty()

    def __init__(self, **kwargs):
        """ Override the constructor so we can register an event """
        super(MediaButton, self).__init__(**kwargs)
        self.register_event_type("on_click")

    def on_source(self, widget, value):
        """ The 'source' property for the image has changed. Change it. """
        self.image.source = value

    def on_click(self):
        """ The button has been clicked. """
        pass


Builder.load_string('''

<PlayingScreen>:
    # Define the buttons
    but_previous: previous
    but_stop: stop
    but_playpause: playpause
    but_next: next
    volume: volume
    progress: progress
    info_label1: info_label1
    info_label2: info_label2
    info_label3: info_label3

    album_image: album_image
    BoxLayout:
        orientation: "horizontal"
        BoxLayout:
            # Left Sidebar
            orientation: "vertical"
            size_hint_x: 0.1
        BoxLayout:
            # Center column
            size_hint_x: 0.8
            orientation: "vertical"
            padding: 10, 10, 10, 10
            Slider:
                size_hint_y: 0.1
                id: progress
            Label:
                id: info_label1
                size_hint_y: 0.05
            Label:
                id: info_label2
                size_hint_y: 0.05
            Label:
                id: info_label3
                size_hint_y: 0.05
            Image:
                size_hint_y: 0.65
                id: album_image
            BoxLayout:
                size_hint_y: 0.1
                orientation: "horizontal"
                MediaButton:
                    id: previous
                    source: 'images/previous.png'
                MediaButton:
                    id: stop
                    source: 'images/stop.png'
                    on_click: root.stop()
                MediaButton:
                    id: playpause
                    source: 'images/play.png'
                    on_click: root.playpause()
                MediaButton:
                    id: next
                    source: 'images/next.png'

        BoxLayout:
            # Right sidebar
            orientation: "vertical"
            size_hint_x: 0.1
            padding: 10
            spacing: 10
            Slider:
                id: volume
                size_hint_y: 0.9
                orientation: "vertical"
                max: 1
                on_value: root.set_volume()
            Image:
                size_hint_y: 0.1
                source: 'images/speaker.png'
''')


class PlayingScreen(Screen):
    """
    The main screen that shows whats currently playing
    """
    #TODO : Document properties once stable
    album_image = ObjectProperty()
    sound = None
    queue = []  # contains a list of (filename, albumart) pairs
    advance = True  # This flag indicates whether to advance to the next track
                    # once the currently playing one had ended
    current = 0  # The index of the currently playing track in the queue
    but_previous = ObjectProperty()
    but_stop = ObjectProperty()
    but_playpause = ObjectProperty()
    but_next = ObjectProperty()
    info_label = ObjectProperty()
    volume = ObjectProperty()
    progress = ObjectProperty()

    def init(self):
        """ Initialize the display """
        if len(self.queue) > self.current:
            self.album_image.source = self.queue[self.current][1]
            info = self._get_current_info()
            self.info_label1.text = info["artist"]
            self.info_label2.text = info["album"]
            self.info_label3.text = info["file"]
            self.volume.value = 0.5   # TODO: Remove

    def add_folder(self, folder):
        """ Add the specified folder to the queue """
        artwork = self._get_albumart(folder)
        for f in listdir(folder):
            if ".mp3" in f or ".ogg" in f or ".wav" in f:
                self.queue.append((path.join(folder, f), artwork))

    def playpause(self):
        """ Start playing any audio if nothing is playing """
        if not self.sound:
            if len(self.queue) > self.current:
                print "playing ", self.queue[self.current][0]
                self.sound = SoundLoader.load(self.queue[self.current][0])
                self.sound.bind(on_stop=self._on_stop)
                self.sound.play()
                self.album_image.source = self.queue[self.current][1]
                self.but_playpause.source = "images/pause.png"
                self.sound.volume = self.volume.value
        elif self.sound.state == "play":
            self.advance = False
            self.sound.stop()
            self.but_playpause.source = "images/play.png"
        else:
            self.sound.play()
            self.but_playpause.source = "images/pause.png"

    def stop(self):
        """ Stop any playing audio """
        if self.sound:
            self.advance = False
            self.sound.stop()
            self.but_playpause.source = "images/play.png"

    def set_volume(self):
        """ Set the volume of the currently playing track if there is one. """
        if self.sound:
            self.sound.volume = self.volume.value

    @staticmethod
    def _get_albumart(folder):
        """
        Return the full image filename from the folder
        """
        for f in ["cover.jpg", "cover.png", "cover.bmp", "cover.jpeg"]:
            full_name = path.join(folder, f)
            if path.exists(full_name):
                return full_name
        return ""

    def _get_current_info(self):
        """
        Return a dictionary containing the metadata on the track """
        try:
            parts = self.queue[self.current][0].split("/")
            return {
                "artist": parts[-3],
                "album": parts[-2],
                "file": parts[-1]}
        except:
            return {
                "artist": "-",
                "album": "-",
                "file": "-"}

    def _on_stop(self, *args):
        print "sound has stopped. args=", str(args)
        if self.advance:
            self.queue.pop(0)
            self.playpause()
        # output: sound has stopped. args=
        # (<kivy.core.audio.audio_pygame.SoundPygame object at 0xa106a7c>,)


class ZenPlayer(App):
    def build(self):
        sm = ScreenManager()
        playing = PlayingScreen()
        #TODO: Remove
        playing.add_folder('/media/Zen320/Zen/Music/MP3/In Flames/Colony')
        #playing.add_folder('/media/Zen320/Zen/Music/MP3/Ace of base/Da capo')
        playing.init()

        #def stop(dt):
        #    print "============= About to stop"
        #    playing.stop()

        #from kivy.clock import Clock
        #Clock.schedule_once(stop, 5.0)

        #TODO: Remove

        sm.switch_to(playing)
        return sm

ZenPlayer().run()