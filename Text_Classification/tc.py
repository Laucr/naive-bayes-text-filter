# text classification module based on naive bayes
# -*- coding:utf-8 -*-
import os
import copy
from Logger.logger import Logger as Log
from collections import OrderedDict
import codecs
import json
import math
import threading


class TextClassification:
    def __init__(self, train_set_path, test_set_path, cache_path):
        self._train_set_dir_ = train_set_path
        self._test_set_dir_ = test_set_path
        self._train_set_dict_ = self.get_sets_of_secondary_path_tree(train_set_path)
        self._test_set_dict_ = self.get_sets_of_secondary_path_tree(test_set_path)
        self._train_set_total_files_num_ = 0
        for _iter_basename in self._train_set_dict_:
            self._train_set_total_files_num_ += len(self._train_set_dict_[_iter_basename])
        # like [{'category': 'Edu', 'cache_path': 'D:\corpus\Edu-seg\Edu.json'}, {...}]
        self._cache_path_category_ = cache_path[0]
        # like 'D:\corpus\twdlist.json'
        self._cache_path_total_ = cache_path[1]
        self._bayes_train_()

    @staticmethod
    # returns like:
    # set_files {
    # 'sort1': ['D:\\sort1\\1.txt', 'D:\\sort1\\2.txt', 'D:\\sort1\\3.txt'],
    # 'sort2': ['D:\\sort2\\1.txt', 'D:\\sort2\\2.txt', 'D:\\sort2\\3.txt'],
    # }
    def get_sets_of_secondary_path_tree(_file_dir):
        all_file = [[], []]
        gen = os.walk(_file_dir)
        for root, dirs, files in gen:
            all_file[0].append([root])
            all_file[1].append(files)
        set_files = {}
        for iter_i in range(1, len(all_file[0])):
            set_files.setdefault(
                    os.path.basename(all_file[0][iter_i][0]),
                    [os.path.join(all_file[0][iter_i][0], all_file[1][iter_i][iter_j]) for iter_j in
                     range(len(all_file[1][iter_i]))]
            )
        return set_files

    @staticmethod
    # returns like:
    # set_files {
    # 'category': 'train',
    # 'files': ['D:\\train\\1.txt', 'D:\\train\\2.txt', 'D:\\train\\3.txt']
    # }
    def get_sets_of_root_path_tree(_file_dir):
        all_file = [[], []]
        gen = os.walk(_file_dir)
        for root, dirs, files in gen:
            all_file[0].append([root])
            all_file[1].append(files)
        set_files = {
            'category': os.path.basename(all_file[0][0][0]),
            'files':
                [os.path.join(all_file[0][0][0], all_file[1][0][_iter]) for _iter in range(len(all_file[1][0]))]
        }
        return set_files

    @staticmethod
    def get_wd_list(filename):
        tmp = {}
        with codecs.open(filename, 'r', 'utf-8') as f:
            txt = f.read()
            # no error for using .split() because the txt is consist of words and ' '
            for word in txt.split():
                if word not in tmp:
                    tmp[word] = 0
                tmp[word] += 1
        # freq
        return tmp

    @staticmethod
    def load_cache(cache_path):
        with open(cache_path, 'r') as cache:
            return json.load(cache)

    @staticmethod
    def create_cache(cache, cache_path):
        with open(cache_path, 'w') as cache_file:
            json.dump(cache, cache_file)

    def _bayes_train_(self):
        self._wd_list_category_ = []
        if os.path.exists(self._cache_path_total_):
            Log.log_blue_running('Corpus cache loaded.')
            self._wd_list_total_ = self.load_cache(self._cache_path_total_)
            for _iter_cache_file in range(len(self._cache_path_category_)):
                self._wd_list_category_.append({
                    'category': self._cache_path_category_[_iter_cache_file]['category'],
                    'words': self.load_cache(self._cache_path_category_[_iter_cache_file]['cache_path'])
                })
        else:
            Log.log_blue_running('Naive Bayes train module.')
            wd_list_total = {}
            for _iter_basename in self._train_set_dict_:

                characteristic_wd_category = {}

                for _iter_filename in self._train_set_dict_[_iter_basename]:
                    tmp = TextClassification.get_wd_list(_iter_filename)
                    for wd in tmp:
                        if wd in wd_list_total:
                            wd_list_total[wd] += tmp[wd]
                        else:
                            wd_list_total[wd] = tmp[wd]
                    words_freq = OrderedDict((sorted((copy.deepcopy(tmp).items()), key=lambda t: -t[-1]))).items()

                    if len(words_freq) > 25:
                        characteristic_wd_file = dict((x, y) for x, y in words_freq[:25])
                    else:
                        characteristic_wd_file = dict((x, y) for x, y in words_freq)

                    for wd in characteristic_wd_file:
                        if wd in characteristic_wd_category:
                            characteristic_wd_category[wd] += characteristic_wd_file[wd]
                        else:
                            characteristic_wd_category[wd] = characteristic_wd_file[wd]

                self.create_cache(characteristic_wd_category, self._train_set_dir_ + '\\' + _iter_basename + '.json')
                Log.log_blue_running('Category: ' + _iter_basename + ' cache created.')

            self._wd_list_total_ = wd_list_total
            self.create_cache(self._wd_list_total_, os.path.abspath(self._train_set_dir_ + '\\..') +
                              '\\wdlist-total.json')
            Log.log_blue_running('Corpus word-lists cache created.')

    def _get_prior_possibility_(self):
        prior_possibility = [{
                                 'category': self._wd_list_category_[_iter_]['category'],
                                 'prior_possibility': len(self._wd_list_category_[_iter_]['words']) * 1.0 /
                                                      len(self._wd_list_total_)
                             } for _iter_ in range(len(self._wd_list_category_))]
        return prior_possibility

    class TcThread(threading.Thread):

        def __init__(self, thread_name, thread_lock, tc_cls, test_category):
            threading.Thread.__init__(self)
            self.setName(thread_name)
            self.tc_cls = tc_cls
            self.test_category = test_category
            self.thread_lock = thread_lock

        def run(self):
            # self.thread_lock.acquire()
            Log.log_green_running('Thread for ' + self.getName() + ' is running.')
            self.tc_cls.text_classification_polynomial(self.test_category)
            Log.log_green_running('Thread for ' + self.getName() + ' finished.')
            # self.thread_lock.release()

    def text_classification_polynomial(self, test_category):
        prior_pos = self._get_prior_possibility_()

        def p_possibility(p_pos_list):
            log_p_pos = map(math.log, p_pos_list)
            log_p = reduce(lambda x, y: x + y, log_p_pos)
            return log_p

        def classification(p_possibility_list, category):
            p = max([p_possibility_list[_iter_] for _iter_ in range(len(p_possibility_list))]).values()[0]
            return p, p == category

        test_num = len(self._test_set_dict_[test_category])
        if_right = 0
        for _iter_file in self._test_set_dict_[test_category]:
            wd_list = self.get_wd_list(_iter_file)
            category_pos = []
            for _iter_category in range(len(self._wd_list_category_)):
                wd_account = reduce(lambda x, y: x + y, self._wd_list_category_[_iter_category]['words'].values())
                _p_category = []
                denominator = wd_account + len(self._wd_list_total_)
                for wd in wd_list.keys():
                    if wd in self._wd_list_category_[_iter_category]['words']:
                        nij = self._wd_list_category_[_iter_category]['words'][wd]
                    else:
                        nij = 0
                    # every single word count for once
                    for _iter_account_ in range(wd_list[wd]):
                        _p = (nij + 1) * 1.0 / denominator
                        _p_category.append(_p)
                category_pos.append({
                    p_possibility(_p_category) + math.log(prior_pos[_iter_category]['prior_possibility']):
                        self._wd_list_category_[_iter_category]['category']
                })
            if classification(category_pos, test_category)[1]:
                if_right += 1
        Log.log_blue_running('Category: ' + test_category +
                             ' total ' + str(test_num) + ', correct: ' + str(if_right) +
                             ' Accuracy: ' + str((if_right * 1.0 / test_num) * 100) + '%')

    def tc_thd_starter(self):
        thread_lock = threading.Lock()
        threads = [self.TcThread(_iter_basename_, thread_lock, self, _iter_basename_)
                   for _iter_basename_ in self._test_set_dict_]
        [threads[_iter_].start() for _iter_ in range(len(threads))]
