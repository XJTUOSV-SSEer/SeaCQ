import random
from typing import Dict,Set,Tuple,Any, List, Optional

def gen_data(w_num:int, id_num:int) -> Dict[str,Set[int]]:
    '''
    生成倒排索引
    input:
        w_num - w的个数
        id_num - 每个w对应id的个数
    output:
        dataset - 倒排索引
    '''
    dataset=dict()

    for i in range(1, w_num+1):
        w='w'+str(i)
        # 生成id_num个id
        id_list = random.sample(range(1, 3*id_num+1), id_num)
        id_set = set(id_list)

        dataset[w]=id_set
    
    return dataset