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
    生成用于测试搜索性能的数据集。w1只包含前w1_f_num个文件，w2~w10只匹配前100个文件，其余文件不包含w1~w10
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

    # w1_f_num+1~100文件，必须包含w2~w10, 且不包含w1
    tmp = ['w'+str(s) for s in range(2,11)]
    for i in range(w1_f_num+1, 101):
        index[str(i)] = set(tmp)
        # 再生成 w_num-9 个不同的关键字
        w_list = ['w'+str(s) for s in random.sample(range(11, 1+5*w_num), w_num-9)]
        index[str(i)].update(w_list)
    
    # 其余文件，不能包含w1~w10
    for i in range(101, f_num+1):
        w_list = ['w'+str(s) for s in random.sample(range(11, 1+5*w_num), w_num)]
        index[str(i)] = set(w_list)

    # 计算得到倒排索引
    for f, w_set in index.items():
        for w in w_set:
            if w not in inverted_index:
                inverted_index[w] = set()
            inverted_index[w].add(int(f))
    
    # 将数据持久化存储
    with open(filename1, 'wb') as f1:
        pickle.dump(index, f1)
    with open(filename2, 'wb') as f2:
        pickle.dump(inverted_index, f2)
        
        




if __name__ == '__main__':
    # # 100K文件，每个文件中200个关键字。w1只存在于前20个文件中,w2~w10只存在于前100个文件中
    # gen_dataset2(100000, 200, './100K_file_50_w_20.dat', './inv_100K_file_50_w_20.dat', 20)
    # # 100K文件，每个文件中200个关键字。w1只存在于前40个文件中,w2~w10只存在于前100个文件中
    # gen_dataset2(100000, 200, './100K_file_50_w_40.dat', './inv_100K_file_50_w_40.dat', 40)
    # # 100K文件，每个文件中200个关键字。w1只存在于前60个文件中,w2~w10只存在于前100个文件中
    # gen_dataset2(100000, 200, './100K_file_50_w_60.dat', './inv_100K_file_50_w_60.dat', 60)
    # # 100K文件，每个文件中200个关键字。w1只存在于前80个文件中,w2~w10只存在于前100个文件中
    # gen_dataset2(100000, 200, './100K_file_50_w_80.dat', './inv_100K_file_50_w_80.dat', 80)
    # # 100K文件，每个文件中200个关键字。w1只存在于前100个文件中,w2~w10只存在于前100个文件中
    # gen_dataset2(100000, 200, './100K_file_50_w_100.dat', './inv_100K_file_50_w_100.dat', 100)


    # # 100K文件，每个文件中50个关键字
    # gen_dataset1(100000, 50, './100K_file_50_w.dat', './inv_100K_file_50_w.dat')
    # # 100K文件，每个文件中50个关键字
    # gen_dataset1(100000, 100, './100K_file_100_w.dat', './inv_100K_file_100_w.dat')
    # # 100K文件，每个文件中150个关键字
    # gen_dataset1(100000, 150, './100K_file_150_w.dat', './inv_100K_file_150_w.dat')
    # # 100K文件，每个文件中200个关键字
    # gen_dataset1(100000, 200, './100K_file_200_w.dat', './inv_100K_file_200_w.dat')
    # 100K文件，每个文件中250个关键字
    gen_dataset1(100000, 250, './100K_file_250_w.dat', './inv_100K_file_250_w.dat')

    # 20K文件，每个文件中200关键字
    gen_dataset1(20000, 200, './20K_file_200_w.dat', './inv_20K_file_200_w.dat')
    # 40K文件，每个文件中200关键字
    gen_dataset1(40000, 200, './40K_file_200_w.dat', './inv_40K_file_200_w.dat')
    # 60K文件，每个文件中200关键字
    gen_dataset1(60000, 200, './60K_file_200_w.dat', './inv_60K_file_200_w.dat')
    # 80K文件，每个文件中200关键字
    gen_dataset1(80000, 200, './80K_file_200_w.dat', './inv_80K_file_200_w.dat')
