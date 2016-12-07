import datetime
now = datetime.datetime.now()
timestamp = now.strftime('%m-%d %H:%M:%S')


class Logout(object):
    TAG = {
        'OK_BLUE': '\033[94m' + '[-] ' + timestamp,
        'OK_GREEN': '\033[92m' + '[-] ' + timestamp,
        'EMPHASIS': '\033[93m' + '[*] ' + timestamp,
        'CAUTION': '\033[91m' + '[#] ' + timestamp,
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
        return msg

    @staticmethod
    @Logout('OK_GREEN')
    def log_output(msg):
        return [m for m in msg]

    @staticmethod
    @Logout('OK_GREEN')
    def log_green_running(msg):
        return msg

    @staticmethod
    @Logout('CAUTION')
    def log_caution(msg):
        return msg

    @staticmethod
    @Logout('EMPHASIS')
    def log_emphasis(msg):
        return msg
