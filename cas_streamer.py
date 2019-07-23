from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from entries.cas_entry import CasEntry
from basemodule import Singleton
from debugmodule import Log
import time


class MyEventHandler(FileSystemEventHandler):
    # post_url 추가
    def __init__(self, observer, dirpath, post_url):
        self.observer = observer
        self.dirpath = dirpath
        self.post_url = post_url
        self.tag = 'MyEventHandler'
        self.wait = 1
        self.retry = 10

    def on_created(self, event):
        # TODO: process when a file created in the selected directory
        if event.event_type == 'created':
            Log.d(self.tag, 'file creation detected. waiting for creating completed for %ds...' % self.wait)
            time.sleep(self.wait)

            entry = CasEntry('')
            for i in range(self.retry):
                entry = CasEntry(event.src_path)
                if entry.valid:
                    break
                else:
                    Log.e(self.tag, 'new file is not valid. retrying...(%d / %d)' % (i + 1, self.retry))
                    time.sleep(1)

            if not entry.valid:
                Log.e(self.tag, 'ISD file parsing error. streaming aborted.')
                return

            Log.d(self.tag, 'send %s ::' % event.src_path, str(entry.get_category())[:50], '...')
            # TODO: send cas entry
            self.send_entry(entry, mode='cas')  # 분광 빼고 전부
            self.send_entry(entry, mode='cas_ird')

        else:
            pass

    def send_entry(self, entry, mode):
        import requests

        if mode == 'cas':
            post_data = entry.get_category(category='except_sp_ird')
            endpoint = 'stream'
        elif mode == 'cas_ird':
            post_data = {'datetime': entry.get_datetime(tostr=True),
                         'sp_ird': entry.get_category(category='sp_ird', str_key_type=True)}
            endpoint = 'stream_ird'
        else:  # mode == 'all':.
            endpoint = 'stream'

        response = None
        # post_url 사용
        while not response:
            try:
                Log.d(self.tag, 'method: POST, url: ' + self.post_url + endpoint)
                Log.d(self.tag, 'body:', str(post_data)[:50], '...')
                response = requests.post(self.post_url + endpoint, json=post_data)
                time.sleep(1)
            except Exception as e:
                Log.e(self.tag, 'http post error:', e.__class__.__name__)
                time.sleep(1)

        if(type(response) != str):
            Log.d(self.tag, 'response: ', response.text)

class CasEntryStreamer(Singleton):
    def __init__(self):
        self.observer = None
        self.is_streaming = False

    # post url 추가
    def set_observer(self, path=None, post_url=None):
        if path:
            self.remote_dirpath = path
        else:
            self.remote_dirpath = ''

        # post_url 추가
        if post_url:
            self.post_url = post_url
        else:
            self.post_url = ''

        self.observer = Observer()
        # post_url 추가
        event_handler = MyEventHandler(self.observer, self.remote_dirpath, self.post_url)
        self.observer.schedule(event_handler, self.remote_dirpath, recursive=True)

    def streaming_on(self):
        if not self.observer:
            self.set_observer(self.remote_dirpath, self.post_url)
        self.observer.start()
        self.is_streaming = True

    def streaming_off(self):
        self.observer.stop()
        self.observer = None
        self.is_streaming = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.streaming_off()


if __name__ == "__main__":
    streamer = CasEntryStreamer()
    streamer.set_observer('C:/Users')
    streamer.streaming_on()

