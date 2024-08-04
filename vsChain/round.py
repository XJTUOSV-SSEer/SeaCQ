from typing import Dict,Set,Tuple,Any, List, Optional

class round:
    '''
    储存JOIN QUERY中每一轮次的信息
    '''

    # 该轮次的搜索目标id
    target_id:int
    # 目标id来源自哪颗树
    target_w: bytes

    # 储存每颗树对于target的lower bound和upper bound
    # 键为tau_w，值为lb,ub结点在树中的下标
    bound: Dict[bytes,Tuple[int, Optional[int]]]


    def __init__(self, target_id:int, target_w:bytes) -> None:
        self.target_id=target_id
        self.bound=dict()
        self.target_w = target_w