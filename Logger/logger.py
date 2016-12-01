class Logout(object):
    TAG = {
        'OK_BLUE': '\033[94m' + '[-] ',
        'OK_GREEN': '\033[92m' + '[-] ',
        'WARNING': '\033[93m' + '[*] ',
        'ERROR': '\033[91m' + '[#] ',
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
    def log_running(msg):
        return msg

    @staticmethod
    @Logout('OK_GREEN')
    def log_output(msg):
        return [m for m in msg]

    @staticmethod
    @Logout('ERROR')
    def log_error(msg):
        return msg

    @staticmethod
    @Logout('WARNING')
    def log_warning(msg):
        return msg