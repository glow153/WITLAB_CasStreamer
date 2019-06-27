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
                    Log.e(self.tag, 'new ISD file is not valid. retrying...(%d / %d)' % (i + 1, self.retry))
                    time.sleep(1)

            if not entry.valid:
                Log.e(self.tag, 'ISD file parsing error. streaming aborted.')
                return

            Log.d(self.tag, 'send %s ::' % event.src_path, str(entry.get_category(category='all'))[:50], '...')
            # TODO: send cas entry

        else:
            pass


class CasEntryStreamer(Singleton):
    def __init__(self):
        self.observer = None

    def set_observer(self, path=None):
        if path:
            self.remote_dirpath = path
        else:
            self.remote_dirpath = ''

        self.observer = Observer()
        event_handler = MyEventHandler(self.observer, self.remote_dirpath)
        self.observer.schedule(event_handler, self.remote_dirpath, recursive=True)

    def streaming_on(self):
        self.observer.start()

    def streaming_off(self):
        self.observer.stop()
        self.observer = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.streaming_off()


if __name__ == "__main__":
    streamer = CasEntryStreamer()
    streamer.set_observer('C:/Users/JakePark/Desktop/tmp')
    streamer.streaming_on()

