import hmac
import pickle
import json
import random

def get_data_build(dataset_size,pickle_file,json_file):
    '''
    生成指定大小的数据集。共1K个关键字，每个关键字对应dataset_size/1000个文件id，并额外包含一个nonce

    将倒排索引转换为普通字符串的形式并用pickle持久化储存为'./data_4K.txt'，且储存在"./data_4K.json"

    Parameters:
    dataset_size:数据集大小
    pickle_file:pickle文件的名称
    json_file: json文件的名称
    '''

    d={}
    for i in range(0,1001):
        l=[]
        # 先加入一个nonce
        nonce=random.randint(-100000000000,10000000000)
        nonce=str(nonce).zfill(16)
        l.append(nonce)

        # 随机生成多个整数，注意这些整数不能是相同的
        for j in range(int(dataset_size/1000)):
            s=str(random.randint(0,2000)).zfill(16)
            while s in l:
                s=str(random.randint(0,2000)).zfill(16)
            
            l.append(s)
        
        d[str(i)]=l
    
    with open (pickle_file, 'wb') as f: #打开文件
        pickle.dump(d, f)

    json_str = json.dumps(d,indent=4)
    with open(json_file, 'w') as json_file:
        json_file.write(json_str)



def get_data_update(dataset_size,pickle_file,json_file):
    '''
    生成指定大小的数据集。共200个关键字，每个关键字对应dataset_size/200个文件id

    将倒排索引转换为普通字符串的形式并用pickle持久化储存为'./data_4K.txt'，且储存在"./data_4K.json"

    Parameters:
    dataset_size:数据集大小
    pickle_file:pickle文件的名称
    json_file: json文件的名称
    '''

    d={}
    for i in range(0,200):
        # 随机生成整数
        l=[]
        # 先加入一个nonce
        nonce=random.randint(-100000000000,10000000000)
        nonce=str(nonce).zfill(16)
        l.append(nonce)
        for j in range(int(dataset_size/200)):
            s=str(random.randint(0,2000)).zfill(16)
            while s in l:
                s=str(random.randint(0,2000)).zfill(16)
            l.append(s)
        
        d[str(i)]=l
    
    with open (pickle_file, 'wb') as f: #打开文件
        pickle.dump(d, f)

    json_str = json.dumps(d,indent=4)
    with open(json_file, 'w') as json_file:
        json_file.write(json_str)






if __name__=='__main__':
    #  用于测试build的数据
    get_data_build(2000,"./data/data_2K.txt","./data/data_2K.json")


    # 用于测试update的数据
    # get_data_update(400,"./data/data_400.txt","./data/data_400.json")
    # get_data_update(800,"./data/data_800.txt","./data/data_800.json")
    # get_data_update(1200,"./data/data_1200.txt","./data/data_1200.json")
    # get_data_update(1600,"./data/data_1600.txt","./data/data_1600.json")
    # get_data_update(2000,"./data/data_2000.txt","./data/data_2000.json")
    
    # get_data(2000,"./dataset_2K.txt","./dataset_2K.json")

    # transform_data()

    # # 10K数据集
    # with open ("data_10K.txt", 'rb') as f: #打开文件
    #     dict=pickle.load(f)
    
    # json_str = json.dumps(dict,indent=4)
    # with open("./data_10K.json", 'w') as json_file:
    #     json_file.write(json_str)

    
    # print(dict['999'])
    # print(dict['1000'])
    # print(dict)