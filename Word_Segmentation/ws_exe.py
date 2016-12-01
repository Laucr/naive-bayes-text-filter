import Text_Classification.tc as tf
import os
import wsthread
import threading

category_path = [
    os.path.abspath('../../corpus/train/Education'),
    os.path.abspath('../../corpus/train/Entertainment'),
    os.path.abspath('../../corpus/train/Finance'),
    os.path.abspath('../../corpus/train/Food'),
    os.path.abspath('../../corpus/train/Gongyi'),
    os.path.abspath('../../corpus/train/Health'),
    os.path.abspath('../../corpus/train/Military'),
    os.path.abspath('../../corpus/train/Technology'),
    os.path.abspath('../../corpus/train/Tourism'),
    os.path.abspath('../../corpus/train/Wenshi'),
    os.path.abspath('../../corpus/train/Women'),
    os.path.abspath('../../corpus/test/Education'),
    os.path.abspath('../../corpus/test/Entertainment'),
    os.path.abspath('../../corpus/test/Finance'),
    os.path.abspath('../../corpus/test/Food'),
    os.path.abspath('../../corpus/test/Gongyi'),
    os.path.abspath('../../corpus/test/Health'),
    os.path.abspath('../../corpus/test/Military'),
    os.path.abspath('../../corpus/test/Technology'),
    os.path.abspath('../../corpus/test/Tourism'),
    os.path.abspath('../../corpus/test/Wenshi'),
    os.path.abspath('../../corpus/test/Women'),
]

threads_set_dict = [tf.TextFilter.get_sets_of_root_path_tree(category_path[_iter])
                    for _iter in range(len(category_path))]

thread_lock = threading.Lock()

threads = [wsthread.WsThread(threads_set_dict[_iter]['category'], thread_lock, threads_set_dict[_iter])
           for _iter in range(len(category_path))]

[threads[_iter].start() for _iter in range(len(threads))]
