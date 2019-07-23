from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from lib.cas_entry import CasEntry
from controller.scheduler_module import StreamScheduler
from lib.basemodule import Singleton
from lib.debugmodule import Log
import time


class MyEventHandler(FileSystemEventHandler):
    def __init__(self, observer, stream_schd, dir_path, url):
        self.observer = observer
        self.stream_schd = stream_schd
        self.dir_path = dir_path
        self.url = url
        self.tag = 'MyEventHandler'
        self.wait = 1
        self.retry = 10

    def on_created(self, event):
        # TODO: process when a file created in the selected directory
        if event.event_type == 'created':
            Log.d(self.tag, 'file creation detected. waiting for creating completed for %ds...' % self.wait)
            time.sleep(self.wait)

            entry = CasEntry('')  # make empty entry
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
            # self.send_stream(entry, mode='cas')  # 분광 빼고 전부
            # self.send_stream(entry, mode='cas_ird')  # 분광만
            # self.send_stream(entry, mode='simple')  # 간략 데이터
            self.send_stream(entry, mode='test')  # test 데이터

        else:
            pass

    def send_stream(self, entry, mode):
        post_data = {}

        if mode == 'cas':
            post_data = entry.get_category(category='basic')
        elif mode == 'cas_ird':
            post_data = entry.get_category(category='ird')
        elif mode == 'simple':
            post_data = entry.get_category(category='simple')
        elif mode == 'test':
            post_data = entry.get_category(category='simple')
        elif mode == 'all':
            post_data = entry.get_category(category='all', str_key_type=True)

        self.stream_schd.put({'url': self.url, 'post_data': post_data})


class CasEntryStreamer(Singleton):
    def __init__(self):
        self.observer = None
        self.stream_schd = None
        self.is_streaming = False
        self.local_dirpath = ''
        self.url = ''

    def set_observer(self, path, url):
        if path:
            self.local_dirpath = path
        else:
            self.local_dirpath = ''

        self.url = url

        self.observer = Observer()
        event_handler = MyEventHandler(self.observer, self.stream_schd, self.local_dirpath, self.url)
        self.observer.schedule(event_handler, self.local_dirpath, recursive=True)

    def streaming_on(self, flags):
        if not self.observer:
            self.set_observer(self.local_dirpath)
        self.stream_schd = StreamScheduler()
        self.observer.start()
        self.stream_schd.start_thread()
        self.is_streaming = True

    def streaming_off(self):
        self.observer.stop()
        self.observer = None
        self.stream_schd.stop_thread()
        self.is_streaming = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.streaming_off()
        if self.stream_schd.is_on:
            self.stream_schd.stop_thread()


if __name__ == "__main__":
    streamer = CasEntryStreamer()
    streamer.set_observer('C:/Users/JakePark/Desktop/tmp', 'http://210.102.142.14:4000/api/nl/witlab/cas/')
    streamer.streaming_on()

