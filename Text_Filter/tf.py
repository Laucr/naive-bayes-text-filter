# text filtering module based on naive bayes
# -*- coding:utf-8 -*-
import os
import copy
import re
import collections
from Logger.logger import Logger as Log
import jieba.analyse
import codecs


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

    def _load_config(self):
        cfg_path = os.path.abspath('./bayes.cfg')
        if os.path.exists(cfg_path):
            f = open(cfg_path)
            settings = f.readlines()
            train_set_dir = re.match(re.compile(r'train-set-dir = (.+?) #'), settings[0]).group(1)
            test_set_dir = re.match(re.compile(r'test-set-dir = (.+?) #'), settings[1]).group(1)
            self._tr_set_dir = os.path.abspath(train_set_dir)
            self._te_set_dir = os.path.abspath(test_set_dir)
            f.close()
        else:
            self._tr_set_dir = os.path.abspath('./train_set')
            self._te_set_dir = os.path.abspath('./test_set')
        Log.log_running('Retrieved set path.')

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
            for word in text.split():
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

    @staticmethod
    def op_detect(set_files):
        kws = []
        for iter_basename in set_files:
            for iter_filename in set_files[iter_basename]:
                with open(iter_filename) as f:
                    all_text = f.read()
                    kws.append(jieba.analyse.textrank(all_text, topK=10, allowPOS=('ns', 'n')))
        tmp = {}
        for kw in kws:
            for wd in kw:
                if wd not in tmp:
                    tmp[wd] = 0
                tmp[wd] += 1
        op = collections.OrderedDict(sorted((copy.deepcopy(tmp).items()), key=lambda t: -t[-1]))
        if len(op) <= 10:
            return ' '.join([w for w in op])
        else:
            s = ''
            count = 0
            for w in op:
                if count == 10:
                    break
                count += 1
                s += ' '
                s += w
            return s

    def report(self):
        with codecs.open('report.log', 'w', 'utf-8') as f:
            ops = self.op_detect(self.get_sets_of_secondary_path_tree(self._te_set_dir))
            f.write(ops)
            f.write('\n')
            for key in self.rpt:
                f.write(key + ' belongs to ' + self.rpt[key])
                f.write('\n')

    def executor(self):
        self._load_config()
        self._set_attr(self.get_sets_of_secondary_path_tree(self._tr_set_dir), 'train')
        self._set_attr(self.get_sets_of_secondary_path_tree(self._te_set_dir), 'test')
        self._set_attr(self._bayes_train(self._tr_set_files), 'tr_wd_list')
        self._set_attr(self._get_prior_prob(), 'prob')
        self._set_attr(self.bayes_filter(self._prior_prob, self._tr_wd_list, self._ful_wd_list, self._te_set_files),
                       'rpt')
        self.report()
