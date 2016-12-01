import ws
import Text_Filter.tf as tf
import os

set_dict = tf.TextFilter.get_sets_of_root_path_tree(os.path.abspath('../ntest/sort1/train'))
w = ws.WordSegmentation(set_dict)
w.wd_seg()