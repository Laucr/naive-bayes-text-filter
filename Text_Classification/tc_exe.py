from Text_Classification.tc import TextClassification

tr_s_p = 'D:\\Projs\\corpus-seg\\train'
te_s_p = 'D:\\Projs\\corpus-seg\\test'
cache_path = [
    [
        {'category': 'Education', 'cache_path': 'D:\\Projs\\corpus-seg\\train\\Education.json'},
        {'category': 'Entertainment', 'cache_path': 'D:\\Projs\\corpus-seg\\train\\Entertainment.json'},
        {'category': 'Finance', 'cache_path': 'D:\\Projs\\corpus-seg\\train\\Finance.json'},
        {'category': 'Food', 'cache_path': 'D:\\Projs\\corpus-seg\\train\\Food.json'},
        {'category': 'Gongyi', 'cache_path': 'D:\\Projs\\corpus-seg\\train\\Gongyi.json'},
        {'category': 'Health', 'cache_path': 'D:\\Projs\\corpus-seg\\train\\Health.json'},
        {'category': 'Military', 'cache_path': 'D:\\Projs\\corpus-seg\\train\\Military.json'},
        {'category': 'Technology', 'cache_path': 'D:\\Projs\\corpus-seg\\train\\Technology.json'},
        {'category': 'Tourism', 'cache_path': 'D:\\Projs\\corpus-seg\\train\\Tourism.json'},
        {'category': 'Women', 'cache_path': 'D:\\Projs\\corpus-seg\\train\\Women.json'},
    ],
    'D:\\Projs\\corpus-seg\\wdlist-total.json'
]

tc = TextClassification(tr_s_p, te_s_p, cache_path)
tc.tc_thd_starter()

