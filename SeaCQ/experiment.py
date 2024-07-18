import random

def gen_dataset(w_num:int, fid_num:int):
    '''
    生成数据集，数据集的形式为文件。
    首先生成w_num个倒排索引，每个关键字对应的fid数为fid_num。
    然后将倒排索引转换为文件的形式。
    input:
        w_num - 关键字数
        fid_num - 每个关键字对应的文件数
    output:
        dataset - 数据集。Dict类型。key为文件id，字符串类型。value为文件中的关键字集合，集合中元素为字符串类型。
    '''

    # 数据集
    dataset=dict()

    for w in range(1,w_num+1):
        # 生成fid_num个随机的文件id，且取值范围为[1,10*fid_num]
        fid_list=[random.randint(1, 1+10*fid_num) for _ in range(fid_num)]

        # 将这些(w, fid)加入数据集
        for fid in fid_list:
            # 若该文件还不存在，增加k-v pair
            if str(fid) not in dataset:
                dataset[str(fid)]=set()
            # 将w加入fid对应的集合中
            dataset[str(fid)].add(str(w))
    
    return dataset

