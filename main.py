import os
import threading

try:
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.textinput import TextInput
except ImportError:  # pragma: no cover - fallback for headless/test environments
    class _DummyWidget:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class BoxLayout(_DummyWidget):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.children = []

        def add_widget(self, widget):
            self.children.append(widget)

    class Label(_DummyWidget):
        pass

    class TextInput(Label):
        pass

    class Button(Label):
        def bind(self, **kwargs):
            return None

    class App:
        def build(self):
            return None

        def run(self):
            return None

    class Clock:
        @staticmethod
        def schedule_once(callback, timeout, *args, **kwargs):
            return callback(timeout, *args, **kwargs)

try:
    import yt_dlp
except ImportError:  # pragma: no cover - allow code to be imported in CI without the package
    class _FallbackYoutubeDL:
        def __init__(self, opts):
            self.opts = opts

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def download(self, urls):
            raise RuntimeError("yt_dlp is not installed")

    yt_dlp = type("yt_dlp", (), {"YoutubeDL": _FallbackYoutubeDL})()


class Downloader(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=30, spacing=20)
        self.add_widget(Label(text="Music Downloader", font_size=40, size_hint_y=0.2))

        self.url_input = TextInput(hint_text="Paste YouTube Link Here...", size_hint_y=0.2, font_size=30)
        self.add_widget(self.url_input)

        self.status = Label(text="Ready", font_size=30, size_hint_y=0.2)
        self.add_widget(self.status)

        btn = Button(text="DOWNLOAD", size_hint_y=0.4, font_size=40, background_color=(0.1, 0.7, 0.1, 1))
        btn.bind(on_press=self.start_download)
        self.add_widget(btn)

    def _set_status(self, text):
        self.status.text = text

    def start_download(self, instance):
        url = (self.url_input.text or '').strip()
        if not url or 'http' not in url:
            self._set_status("Please paste a valid link!")
            return

        self._set_status("Downloading... Please Wait")
        threading.Thread(target=self.download_audio, args=(url,), daemon=True).start()

    def download_audio(self, url):
        try:
            download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
            if os.name == 'nt':
                download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
            else:
                android_dir = '/storage/emulated/0/Download'
                if os.path.isdir(android_dir):
                    download_dir = android_dir

            os.makedirs(download_dir, exist_ok=True)

            ydl_opts = {
                'format': 'm4a/bestaudio/best',
                'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            Clock.schedule_once(lambda dt: self._set_status("Success! Check Downloads folder."), 0)
        except Exception:
            Clock.schedule_once(lambda dt: self._set_status("Error! Download failed."), 0)


class MyApp(App):
    def build(self):
        return Downloader()


if __name__ == '__main__':
    MyApp().run()
