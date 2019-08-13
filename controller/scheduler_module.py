import threading
import time
import requests

from lib.debugmodule import Log


class StreamScheduler(threading.Thread):
    def __init__(self, schd_queue):
        threading.Thread.__init__(self)
        self.q = schd_queue
        self.is_on = False
        self.is_running = False
        self.tag = 'StreamScheduler'

    def run(self):
        """
        queue에 들어있는 send command 하나씩 꺼내서 url로 전송
        :return: none
        """
        while self.is_on:
            if self.q.qsize() > 0:
                # get one send command dict
                send_cmd = self.q.get()

                # validate send command
                try:
                    url = send_cmd['url']
                    post_data = send_cmd['post_data']
                except KeyError:
                    Log.e(self.tag, 'send command format error:', send_cmd)
                    continue  # discard command dict

                # send to backend server
                retry = 10
                # while resend:
                i = 0
                for i in range(1, retry+1):
                    try:
                        Log.d(self.tag, 'tried: %d, url: %s' % (i, url))
                        Log.d(self.tag, 'body:', str(post_data)[:70]+'...')
                        response = requests.post(url, json=post_data)
                        # response = requests.post(url, data=post_data) => data가 아니라 json
                    except Exception as e:
                        Log.e(self.tag, 'streaming error:', e.__class__.__name__)
                        time.sleep(0.5)
                        continue  # retry
                    else:
                        try:
                            if response.status_code == 200:
                                Log.e(self.tag, response.text)
                                break  # succeed stream
                            else:
                                Log.e(self.tag, 'http post error: %d' % response.status_code)
                                continue  # retry
                        except:
                            Log.e(self.tag, 'no response.')
                            continue  # retry

                if i >= 10:
                    Log.d(self.tag, 'tried %d times, reinsert into queue.' % i)
                    self.q.put(send_cmd)
            # Log.e(self.tag, 'send thread running...')
            time.sleep(1)

    def start_thread(self):
        if not self.is_on:
            self.is_on = True
            self.is_running = True
            self.start()
        else:
            self.is_running = True
        Log.d(self.tag, 'stream scheduler started.')

    def stop_thread(self):
        self.is_on = False
        Log.d(self.tag, 'stream scheduler stopped.')

    def put(self, d: dict):
        """
        send command를 queue에 삽입
        :param d: send command. :type: dict
            {
                'url': remote url,
                'post_data': CAS entry data
            }
        :return:
        """
        Log.d(self.tag, 'send command has been put in queue. cmd type:', d['url'].split('/')[-1])
        self.q.put(d)
