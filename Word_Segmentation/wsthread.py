import threading
from ws import WordSegmentation as WS
from Logger.logger import Logger as Log


class WsThread(threading.Thread):

    def __init__(self, thread_name, thread_lock, set_dict):
        threading.Thread.__init__(self)
        self.setName(thread_name)
        self.set_dict = set_dict
        self.thread_lock = thread_lock

    def run(self):
        # self.thread_lock.acquire()
        ws = WS(self.set_dict)
        Log.log_green_running('Thread for ' + self.getName() + ' is running.')
        ws.wd_seg()
        Log.log_green_running('Thread for ' + self.getName() + ' finished.')
        # self.thread_lock.release()

