from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
import yt_dlp
import threading

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

    def start_download(self, instance):
        url = self.url_input.text
        if "http" not in url:
            self.status.text = "Please paste a valid link!"
            return
        self.status.text = "Downloading... Please Wait"
        threading.Thread(target=self.download_audio, args=(url,)).start()

    def download_audio(self, url):
        try:
            ydl_opts = {
                'format': 'm4a/bestaudio/best',
                'outtmpl': '/storage/emulated/0/Download/%(title)s.%(ext)s',
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status.text = "Success! Check Downloads folder."
        except Exception as e:
            self.status.text = "Error! Download failed."

class MyApp(App):
    def build(self):
        return Downloader()

if __name__ == '__main__':
    MyApp().run()
