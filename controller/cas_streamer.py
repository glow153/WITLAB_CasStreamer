from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from lib.cas_entry import CasEntry
from controller.scheduler_module import StreamScheduler
from lib.basemodule import Singleton
from lib.debugmodule import Log
import time


class MyEventHandler(FileSystemEventHandler):
    def __init__(self, observer, stream_schd, dir_path, url, flags):
        self.observer = observer
        self.stream_schd = stream_schd
        self.dir_path = dir_path
        self.url = url
        self.flags = flags

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

            # TODO: send cas entry
            if self.flags['basic']:
                self.send_stream(entry, mode='basic')  # 분광 빼고 전부

            if self.flags['ird']:
                self.send_stream(entry, mode='ird',)  # 분광만

            if self.flags['simple']:
                self.send_stream(entry, mode='simple')  # 간략 데이터

            if self.flags['file']:
                self.send_stream(entry, mode='file')

        else:
            pass

    def send_stream(self, entry, mode):
        if mode == 'basic':
            post_data = entry.get_category(category='basic')
            footer = 'stream'
        elif mode == 'ird':
            post_data = entry.get_category(category='ird', str_key_type=True)
            footer = 'stream_ird'
        elif mode == 'simple':
            post_data = entry.get_category(category='simple')
            footer = 'stream_simple'
        elif mode == 'file':
            post_data = entry.get_category(category='simple')  # file 모드가 현재 테스트모드로 동작중
            footer = 'stream_test'
        else:
            Log.e(self.tag, 'invalid send stream mode. abort send stream.')
            return

        Log.d(self.tag, 'send stream %s ::' % entry.fname, str(post_data)[:50], '...')
        self.stream_schd.put({'url': self.url + footer, 'post_data': post_data})


class CasEntryStreamer(Singleton):
    def __init__(self):
        import queue
        self.observer = None
        self.stream_schd = None
        self.is_streaming = False
        self.tag = 'CasEntryStreamer'
        self.schd_queue = queue.Queue()

    def setup_streamer(self, local_dirpath, url, flags):
        self.observer = Observer()
        self.stream_schd = StreamScheduler(self.schd_queue)

        event_handler = MyEventHandler(self.observer, self.stream_schd, local_dirpath, url, flags)
        self.observer.schedule(event_handler, local_dirpath, recursive=True)

    def streaming_on(self):
        if not self.observer:
            Log.e(self.tag, 'observer not set. it must be set before streaming.')
            return

        self.observer.start()
        self.stream_schd.start_thread()

        self.is_streaming = True

    def streaming_off(self):
        self.observer.stop()
        self.observer = None
        self.stream_schd.stop_thread()
        self.stream_schd = None
        self.is_streaming = False
        if self.schd_queue.qsize() > 0:
            Log.e(self.tag, 'queue is not empty.')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.streaming_off()
        if self.stream_schd.is_on:
            self.stream_schd.stop_thread()


