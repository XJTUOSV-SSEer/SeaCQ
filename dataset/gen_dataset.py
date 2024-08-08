from cmath import pi
import random
from typing import Dict,Set
import pickle



def gen_dataset1(f_num:int, w_num:int, filename1:str, filename2:str):
    '''
    生成f_num个文件，每个文件中有 w_num个关键字。文件id为正整数。
    input:
        f_num - 
        w_num -
        filename1 - 将数据集以 fid-w_set 字典的形式写入文件，且fid为字符串形式。用于SEACQ
        filename2 - 将数据集以 w-fid_set 字典的形式写入文件，且fid为int类型。用于vschain
    '''

    # 索引
    index:Dict[str, Set[str]] = dict()
    # 倒排索引
    inverted_index:Dict[str, Set[int]] = dict()

    # 生成数据
    for i in range(1, f_num+1):
        # 生成 w_num 个不同的关键字
        w_list = ['w'+str(s) for s in random.sample(range(1, 1+5*w_num), w_num)]
        w_set = set(w_list)
        index[str(i)] = w_set

        for w in w_set:
            if w not in inverted_index:
                inverted_index[w] = set()
            inverted_index[w].add(i)
    
    print(1)
    
    # 将数据持久化存储
    with open(filename1, 'wb') as f1:
        pickle.dump(index, f1)
    with open(filename2, 'wb') as f2:
        pickle.dump(inverted_index, f2)




def gen_dataset2(f_num:int, w_num:int, filename1:str, filename2:str, w1_f_num):
    '''
    生成用于测试搜索性能的数据集。w1只包含前w1_f_num个文件，w2~w10只匹配前1000个文件，其余文件不包含w1~w10
    input:
        f_num - 
        w_num -
        filename1 - 将数据集以 fid-w_set 字典的形式写入文件，且fid为字符串形式。用于SEACQ
        filename2 - 将数据集以 w-fid_set 字典的形式写入文件，且fid为int类型。用于vschain
        w1_f_num - 表示包含w1的文件的个数
    '''
    # 索引
    index:Dict[str, Set[str]] = dict()
    # 倒排索引
    inverted_index:Dict[str, Set[int]] = dict()

    # 生成数据
    tmp = ['w'+str(s) for s in range(1,11)]
    # 前w1_f_num个文件, 必须包含w1~w10
    for i in range(1, w1_f_num+1):
        index[str(i)] = set(tmp)
        # 再生成 w_num-10 个不同的关键字
        w_list = ['w'+str(s) for s in random.sample(range(11, 1+5*w_num), w_num-10)]
        index[str(i)].update(w_list)

    # w1_f_num+1~1000文件，必须包含w2~w10, 且不包含w1
    tmp = ['w'+str(s) for s in range(2,11)]
    for i in range(w1_f_num+1, 1001):
        index[str(i)] = set(tmp)
        # 再生成 w_num-9 个不同的关键字
        w_list = ['w'+str(s) for s in random.sample(range(11, 1+5*w_num), w_num-9)]
        index[str(i)].update(w_list)
    
    # 其余文件，不能包含w1~w10
    for i in range(1001, f_num+1):
        w_list = ['w'+str(s) for s in random.sample(range(11, 1+5*w_num), w_num)]
        index[str(i)] = set(w_list)

    # 计算得到倒排索引
    for f, w_set in index.items():
        for w in w_set:
            if w not in inverted_index:
                inverted_index[w] = set()
            inverted_index[w].add(int(f))
    
    print(len(inverted_index['w1']))
    print(len(inverted_index['w2']))
    print(len(inverted_index['w10']))
    
    # 将数据持久化存储
    with open(filename1, 'wb') as f1:
        pickle.dump(index, f1)
    with open(filename2, 'wb') as f2:
        pickle.dump(inverted_index, f2)
        
        


def gen_upd_dataset(f_num:int, w_num:int, dataset_name:str, filename1:str, filename2:str):
    '''
    生成add的数据,要求w-id不能已存在于数据库. 以fid-w_set的形式持久化存储在filename1，以w-fid的形式结构化储存在
    filename2
    input:
        f_num - 对前f_num个文件更新
        w_num - 每个文件add w_num个新关键字
        dataset_name - 原数据集的文件名
        filename1 - 要写入的文件名
    '''
    # 获取原数据集
    with open (dataset_name, 'rb') as f: #打开文件
        dataset = pickle.load(f)

    upd_dataset:Dict[str, Set[str]] = dict()
    
    for i in range(1, f_num+1):
        id = str(i)
        w_set:Set[str] = dataset[id]
        new_w_set = set()
        # 加入w_num个新关键字
        for j in range(w_num):
            # 生成关键字
            new_w = None
            while True:
                new_w = 'w'+str(random.randint(1, 1000))
                if new_w not in w_set and new_w not in new_w_set:
                    break
            new_w_set.add(new_w)

        upd_dataset[id] = new_w_set
    
    print(len(upd_dataset['1']))
    print(upd_dataset['1'])
    print(len(upd_dataset['1000']))
    
    with open(filename1, 'wb') as f1:
        pickle.dump(upd_dataset, f1)
    
    # 倒排索引
    inverted_index:Dict[str, Set[int]] = dict()
    # 计算得到倒排索引
    for f, w_set in upd_dataset.items():
        for w in w_set:
            if w not in inverted_index:
                inverted_index[w] = set()
            inverted_index[w].add(int(f))
    with open(filename2, 'wb') as f2:
        pickle.dump(inverted_index, f2)




if __name__ == '__main__':
    # 100K文件，每个文件中200个关键字。w1只存在于前200个文件中,w2~w10只存在于前1000个文件中
    # gen_dataset2(100000, 200, './100K_file_200_w_200.dat', './inv_100K_file_200_w_200.dat', 200)
    # 100K文件，每个文件中200个关键字。w1只存在于前400个文件中,w2~w10只存在于前1000个文件中
    # gen_dataset2(100000, 200, './100K_file_200_w_400.dat', './inv_100K_file_200_w_400.dat', 400)
    # 100K文件，每个文件中200个关键字。w1只存在于前600个文件中,w2~w10只存在于前1000个文件中
    # gen_dataset2(100000, 200, './100K_file_200_w_600.dat', './inv_100K_file_200_w_600.dat', 600)
    # 100K文件，每个文件中200个关键字。w1只存在于前800个文件中,w2~w10只存在于前1000个文件中
    # gen_dataset2(100000, 200, './100K_file_200_w_800.dat', './inv_100K_file_200_w_800.dat', 800)
    # 100K文件，每个文件中200个关键字。w1只存在于前1000个文件中,w2~w10只存在于前1000个文件中
    # gen_dataset2(100000, 200, './100K_file_200_w_1000.dat', './inv_100K_file_200_w_1000.dat', 1000)


    # # 100K文件，每个文件中50个关键字
    # gen_dataset1(100000, 50, './100K_file_50_w.dat', './inv_100K_file_50_w.dat')
    # # 100K文件，每个文件中50个关键字
    # gen_dataset1(100000, 100, './100K_file_100_w.dat', './inv_100K_file_100_w.dat')
    # # 100K文件，每个文件中150个关键字
    # gen_dataset1(100000, 150, './100K_file_150_w.dat', './inv_100K_file_150_w.dat')
    # # 100K文件，每个文件中200个关键字
    # gen_dataset1(100000, 200, './100K_file_200_w.dat', './inv_100K_file_200_w.dat')
    # # 100K文件，每个文件中250个关键字
    # gen_dataset1(100000, 250, './100K_file_250_w.dat', './inv_100K_file_250_w.dat')

    # # 20K文件，每个文件中200关键字
    # gen_dataset1(20000, 200, './20K_file_200_w.dat', './inv_20K_file_200_w.dat')
    # # 40K文件，每个文件中200关键字
    # gen_dataset1(40000, 200, './40K_file_200_w.dat', './inv_40K_file_200_w.dat')
    # # 60K文件，每个文件中200关键字
    # gen_dataset1(60000, 200, './60K_file_200_w.dat', './inv_60K_file_200_w.dat')
    # # 80K文件，每个文件中200关键字
    # gen_dataset1(80000, 200, './80K_file_200_w.dat', './inv_80K_file_200_w.dat')

    # 100K 文件, 每个文件中200关键字前提下, add 100K w-id pair, 固定更新文件数为1000
    gen_upd_dataset(1000, 100, './100K_file_200_w.dat', 'upd_100K.dat', 'inv_upd_100K.dat')
    # 100K 文件, 每个文件中200关键字前提下, add 200K w-id pair, 固定更新文件数为1000
    gen_upd_dataset(1000, 200, './100K_file_200_w.dat', 'upd_200K.dat', 'inv_upd_200K.dat')
    # 100K 文件, 每个文件中200关键字前提下, add 300K w-id pair, 固定更新文件数为1000
    gen_upd_dataset(1000, 300, './100K_file_200_w.dat', 'upd_300K.dat', 'inv_upd_300K.dat')
    # 100K 文件, 每个文件中200关键字前提下, add 400K w-id pair, 固定更新文件数为1000
    gen_upd_dataset(1000, 400, './100K_file_200_w.dat', 'upd_400K.dat', 'inv_upd_400K.dat')
    # 100K 文件, 每个文件中200关键字前提下, add 500K w-id pair, 固定更新文件数为1000
    gen_upd_dataset(1000, 500, './100K_file_200_w.dat', 'upd_500K.dat', 'inv_upd_500K.dat')