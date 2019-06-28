from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from entries.cas_entry import CasEntry
from basemodule import Singleton
from debugmodule import Log
import time


class MyEventHandler(FileSystemEventHandler):
    def __init__(self, observer, dirpath):
        self.observer = observer
        self.dirpath = dirpath
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
            # self.send_entry(entry, mode='cas_ird')  # 분광 빼고 전부

        else:
            pass

    def send_entry(self, entry, mode):
        import requests
        post_data = entry.get_category(category=mode, str_key_type=True)

        if mode == 'cas':
            post_data = entry.get_category(category='except_sp_ird')
            endpoint = 'stream'
        elif mode == 'cas_ird':
            post_data = {'datetime': entry.get_datetime(tostr=True),
                         'data': entry.get_category(category='sp_ird', str_key_type=True)}
            endpoint = 'stream_ird'
        else:  # mode == 'all':
            endpoint = 'stream'

        response = None
        while not response:
            try:
                Log.d(self.tag, 'method: POST, url: http://210.102.142.14:8880/api/nl/witlab/cas/' + endpoint)
                Log.d(self.tag, 'body:', str(post_data)[:50], '...')
                response = requests.post('http://210.102.142.14:8880/api/nl/witlab/cas/' + endpoint, json=post_data)
                time.sleep(1)
            except Exception as e:
                Log.e(self.tag, 'http post error:', e.__class__.__name__)
                time.sleep(1)

        Log.d(self.tag, 'response: ', response.text)


class CasEntryStreamer(Singleton):
    def __init__(self):
        self.observer = None
        self.is_streaming = False

    def set_observer(self, path=None):
        if path:
            self.remote_dirpath = path
        else:
            self.remote_dirpath = ''

        self.observer = Observer()
        event_handler = MyEventHandler(self.observer, self.remote_dirpath)
        self.observer.schedule(event_handler, self.remote_dirpath, recursive=True)

    def streaming_on(self):
        if not self.observer:
            self.set_observer(self.remote_dirpath)
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
    streamer.set_observer('C:/Users/JakePark/Desktop/tmp')
    streamer.streaming_on()

