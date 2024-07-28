from typing import Dict,Set,Tuple,Any, List, Optional

class round:
    '''
    储存JOIN QUERY中每一轮次的信息
    '''

    # 该轮次的搜索目标id
    target:int

    # 储存每颗树对于target的lower bound和upper bound
    # 键为tau_w，值为lb,ub结点在树中的下标
    bound: Dict[bytes,Tuple[int, Optional[int]]]


    def __init__(self, target:int) -> None:
        self.target=target
        self.bound=dict()