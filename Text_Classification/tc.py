# text filtering module based on naive bayes
# -*- coding:utf-8 -*-
import os
import copy
import collections
from Logger.logger import Logger as Log
import codecs
import json


class TextFilter(object):
    def __init__(self):
        self._tr_set_dir = ''
        self._te_set_dir = ''
        self._tr_wd_list = {}
        self._ful_wd_list = {}
        self._tr_set_files = {}
        self._te_set_files = {}
        self._prior_prob = {}
        self.rpt = {}
        self._total_files_num = 0

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
        print set_files

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

    def _set_attr(self, _attr, _attr_name):
        if _attr_name is 'train':
            total = 0
            for _sub_attr in _attr:
                total += len(_attr[_sub_attr])
            self._tr_set_files = _attr
            self._total_files_num = total
            Log.log_running('Retrieved train set files.')
        elif _attr_name is 'test':
            self._te_set_files = _attr
            Log.log_running('Retrieved test set files.')
        elif _attr_name is 'prob':
            self._prior_prob = _attr
            Log.log_running('Solved prior probability.')
        elif _attr_name is 'tr_wd_list':
            self._tr_wd_list = _attr
            Log.log_running('Retrieved train word lists.')
        elif _attr_name is 'rpt':
            self.rpt = _attr
            Log.log_running('Text-sort succeed.')

    # for one file input
    @staticmethod
    def get_wd_list(filename):
        tmp = {}
        with open(filename) as f:
            text = f.read()
            for word in text.strip():
                if word not in tmp:
                    tmp[word] = 0
                tmp[word] += 1
        return tmp

    def _bayes_train(self, set_dir):
        sort_wd_freq = {}
        for iter_basename in set_dir:
            for iter_file in set_dir[iter_basename]:
                tmp = TextFilter.get_wd_list(iter_file)
                for wd in tmp:
                    if wd in self._ful_wd_list:
                        self._ful_wd_list[wd] += tmp[wd]
                    else:
                        self._ful_wd_list[wd] = tmp[wd]
            words_freq = collections.OrderedDict(sorted((copy.deepcopy(tmp).items()), key=lambda t: -t[-1]))
            sort_wd_freq.setdefault(iter_basename, words_freq)
        return sort_wd_freq

    # get prior probability
    def _get_prior_prob(self):
        _pri_prob = {}
        [_pri_prob.setdefault(sort_, len(self._tr_set_files[sort_]) * 1.0 / self._total_files_num)
         for sort_ in self._tr_set_files]
        return _pri_prob

    # bayes text filter
    @staticmethod
    def bayes_filter(pri_prob, tr_wd_list, total_wd_list, te_set_files):
        sort_num = {}
        rpt = {}
        for iter_basename in te_set_files:
            for iter_file in te_set_files[iter_basename]:
                wd_list = TextFilter.get_wd_list(iter_file)
                _count = []
                num = 0
                for iter_sort in tr_wd_list:
                    sort_num.setdefault(num, iter_sort)
                    num += 1
                    wd_count = len(tr_wd_list[iter_sort])
                    _count_10 = 0
                    for wd in wd_list.keys():
                        if wd in tr_wd_list[iter_sort]:
                            nij = tr_wd_list[iter_sort][wd]
                            for iter_ in range(wd_list[wd]):
                                _p = pri_prob[iter_sort] * (nij + 1) * 1.0 / (wd_count + len(total_wd_list))
                                while _p < 1:
                                    _p *= 10
                                    _count_10 += 1
                    _count.append(_count_10)
                print sort_num[_count.index(max(_count))].decode('gb2312')
                Log.log_output(iter_file.decode('gb2312'))
                rpt.setdefault(iter_file.decode('gb2312'), sort_num[_count.index(max(_count))].decode('gb2312'))
                Log.log_output(_count)
        return rpt

    def executor(self):
        # self._load_config()
        self._set_attr(self.get_sets_of_secondary_path_tree(self._tr_set_dir), 'train')
        self._set_attr(self.get_sets_of_secondary_path_tree(self._te_set_dir), 'test')
        self._set_attr(self._bayes_train(self._tr_set_files), 'tr_wd_list')
        self._set_attr(self._get_prior_prob(), 'prob')
        self._set_attr(self.bayes_filter(self._prior_prob, self._tr_wd_list, self._ful_wd_list, self._te_set_files),
                       'rpt')


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
            self._wd_list_total_ = self.load_cache(self._cache_path_total_)
            # like [{'category': 'Edu', 'cache_path': 'D:\corpus\Edu-seg\Edu.json'}, {...}]
            for _iter_cache_file in range(len(self._cache_path_category_)):
                self._wd_list_category_.append({
                    'category': self._cache_path_category_[_iter_cache_file]['category'],
                    'words': self.load_cache(self._cache_path_category_[_iter_cache_file]['cache_path'])
                })
        else:
            wd_list_total = {}
            for _iter_basename in self._train_set_dict_:
                words_freq = {}
                for _iter_filename in self._train_set_dict_[_iter_basename]:
                    tmp = TextClassification.get_wd_list(_iter_filename)
                    for wd in tmp:
                        if wd in wd_list_total:
                            wd_list_total[wd] += tmp[wd]
                        else:
                            wd_list_total[wd] = tmp[wd]
                    words_freq = dict(sorted((copy.deepcopy(tmp).items()), key=lambda t: -t[-1]))
                self.create_cache(words_freq, self._train_set_dir_ + '\\' + _iter_basename + '.json')
            self._wd_list_total_ = wd_list_total
            self.create_cache(self._wd_list_total_, os.path.abspath(self._train_set_dir_ + '\\..') +
                              '\\wdlist-total.json')

    def _get_prior_possibility_(self):
        prior_possibility = [{
                                 'category': _iter_basename,
                                 'prior_possibility': len(self._train_set_dict_[_iter_basename]) * 1.0 /
                                                      self._train_set_total_files_num_
                             } for _iter_basename in self._train_set_dict_]
        return prior_possibility

    def text_classification(self):
        prior_pos = self._get_prior_possibility_()

        def p_possibility(p_pos_list):
            p_pos = 1
            _count = 0
            for _p_ in p_pos_list:
                while _p_ < 1:
                    _p_ *= 10
                    _count += 1
                p_pos *= _p_
            return p_pos, _count

        def classification(p_possibility_list, category):
            pos = 0
            __p = p_possibility_list[0]['p_possibility'][0]
            _log = p_possibility_list[0]['p_possibility'][1]
            for _iter_ in range(1, len(p_possibility_list)):
                if p_possibility_list[_iter_]['p_possibility'][1] < _log:
                    __p = p_possibility_list[_iter_]['p_possibility'][0]
                    _log = p_possibility_list[_iter_]['p_possibility'][1]
                    pos = _iter_
                elif p_possibility_list[_iter_]['p_possibility'][1] == _log:
                    if p_possibility_list[_iter_]['p_possibility'][0] < __p:
                        __p = p_possibility_list[_iter_]['p_possibility'][0]
                        _log = p_possibility_list[_iter_]['p_possibility'][1]
                        pos = _iter_
            return p_possibility_list[pos]['p_possibility'][0], \
                   category == p_possibility_list[pos]['p_possibility'][0]

        for _iter_basename in self._test_set_dict_:
            test_num = len(self._test_set_dict_[_iter_basename])
            if_right = 0
            for _iter_file in self._test_set_dict_[_iter_basename]:
                wd_list = self.get_wd_list(_iter_file)
                category_pos = []
                for _iter_category in range(len(self._wd_list_category_)):
                    wd_account = len(self._wd_list_category_[_iter_category]['words'])
                    _p_category = []
                    for wd in wd_list.keys():
                        if wd in self._wd_list_category_[_iter_category]['words']:
                            nij = self._wd_list_category_[_iter_category]['words'][wd]
                            for _iter_ in range(wd_list[wd]):
                                _p = prior_pos[_iter_category]['prior_possibility'] * (nij + 1) * 1.0 / \
                                    (wd_account + self._train_set_total_files_num_)
                                _p_category.append(_p)
                    category_pos.append({
                        'category': self._wd_list_category_[_iter_category]['category'],
                        'p_possibility': p_possibility(_p_category)
                    })
                if classification(category_pos, _iter_basename)[1]:
                    if_right += 1
            print if_right * 1.0 / test_num
