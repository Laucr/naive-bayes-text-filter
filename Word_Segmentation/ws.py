import codecs
import jieba
import os
from Logger.logger import Logger as Log


class WordSegmentation:
    def __init__(self, set_dict):
        self.set_dict = set_dict
        self.stop_wd_list = self.get_stop_wd_list()

    def wd_seg(self):
        def _file_seg_(filename):
            _f = codecs.open(filename, 'r', 'utf-8')
            txt = _f.read()
            seg_list = [_wd for _wd in jieba.cut(txt)]
            # words account before delete stopwords
            _stopwd = len(seg_list)
            for sw in self.stop_wd_list:
                while sw.strip() in seg_list:
                    seg_list.remove(sw.strip())
            # words account before after stopwords
            stopwd_ = len(seg_list)
            _f.close()
            return seg_list, _stopwd, stopwd_
        # use get_sets_of_root_path_tree so
        for iter_filename in self.set_dict['files']:
            log_dir = '\\'.join(iter_filename.split('.')[0].split('\\')[:-3]) + '-seg\\' + \
                      '\\'.join(iter_filename.split('.')[0].split('\\')[-3:-1])

            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            log_name = iter_filename.split('.')[0].split('\\')[-1] + '.log'
            wd_list, _wds, wds_ = _file_seg_(iter_filename)
            Log.log_running("Processed " + self.set_dict['category'] + ' - ' + iter_filename + ',' +
                            ' words account reduced from ' + str(_wds) + ' to ' + str(wds_))
            f = codecs.open(log_dir + '\\' + log_name, 'w', 'utf-8')
            for wd in wd_list:
                if wd != u' ' and wd != u'\n':
                    f.write(wd)
                    f.write(' ')
            f.close()

    # get stop words list
    @staticmethod
    def get_stop_wd_list():
        with codecs.open('stopwd.txt', 'r', 'utf-8') as f:
            text = f.readlines()
            stop_wd_list = [word for word in text]
        Log.log_running('Stopwords total : ' + str(len(stop_wd_list)) + '\n')
        return stop_wd_list
