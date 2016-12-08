import datetime


class Logout(object):
    TAG = {
        'OK_BLUE': '\033[94m' + '[-]',
        'OK_GREEN': '\033[92m' + '[-]',
        'EMPHASIS': '\033[93m' + '[*]',
        'CAUTION': '\033[91m' + '[#]',
        'ENDC': '\033[0m'
    }

    def __init__(self, tag):
        self.tag = self.TAG[tag]

    def __call__(self, func):
        def wrapped(*args, **kwargs):
            print "{tag} {res} {endc}".format(
                tag=self.tag, res=func(*args, **kwargs),
                endc=self.TAG['ENDC']
            )
        return wrapped


class Logger(object):
    @staticmethod
    @Logout('OK_BLUE')
    def log_blue_running(msg):
        now = datetime.datetime.now()
        timestamp = now.strftime('%m-%d %H:%M:%S')
        return timestamp + ' ' + msg

    @staticmethod
    @Logout('OK_GREEN')
    def log_output(msg):
        now = datetime.datetime.now()
        timestamp = now.strftime('%m-%d %H:%M:%S')
        return timestamp+ ' ', [m for m in msg]

    @staticmethod
    @Logout('OK_GREEN')
    def log_green_running(msg):
        now = datetime.datetime.now()
        timestamp = now.strftime('%m-%d %H:%M:%S')
        return timestamp + ' ' + msg

    @staticmethod
    @Logout('CAUTION')
    def log_caution(msg):
        now = datetime.datetime.now()
        timestamp = now.strftime('%m-%d %H:%M:%S')
        return timestamp + ' ' + msg

    @staticmethod
    @Logout('EMPHASIS')
    def log_emphasis(msg):
        now = datetime.datetime.now()
        timestamp = now.strftime('%m-%d %H:%M:%S')
        return timestamp + ' ' + msg
