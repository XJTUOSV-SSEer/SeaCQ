from os import path
from typing import Dict,Set,Tuple,Any, Optional, List
from web3 import Web3

class binSearchTree:
    '''
    二叉搜索树的结点以及相关操作
    '''

    # 结点中的文件id
    id: int
    # 左子结点在数组中的下标
    lchild: int
    # 左子结点的hash digest，使用keccak256计算得到，32字节。若不存在左子结点，则lhash为全0
    lhash: bytes
    # 右子结点在数组中的下标
    rchild: int
    # 右子结点的hash digest，使用keccak256计算得到，32字节。若不存在左子结点，则lhash为全0
    rhash: bytes
    # 从根结点到当前结点的路径。一个字符串。根结点为'*'，lchild为0，rchild为1
    path: str

    
    def __init__(self):
        self.id=-1
        self.lchild = -1
        self.rchild = -1
        self.lhash=None
        self.rhash=None
        self.path=''

    
    @staticmethod
    def construct_tree(tree:List['binSearchTree'] , e_list: List[int], lb:int, rb:int, parent_path:str, direct: str):
        '''
        静态方法，将给定的数据构造为一棵二叉搜索树，并返回树根的引用
        input:
            tree - 一个数组，静态的储存树的结点。初始为空
            e_list - 一个列表，储存w对应的所有id。数据增序排列
            lb - left bound。当前要处理的数据的左边界。
            rb - right bound。当前要处理的数据的右边界。
            parent_path - 当前结点到根结点的路径
            direct - 父结点到当前结点的方向。若当前结点为左子结点，则为'0'，否则为'1'。
        output:
            root - 根结点在tree数组中的下标
            root_hash - 根结点的哈希摘要，bytes类型
        '''

        #################### 递归边界 #######################
        # 若lb>rb，返回None
        if lb>rb:
            return None, bytes(32)

        # 递归表达式
        # 找到数据的中间点作为root，并递归求解左右子树
        else:
            # 中间点
            mid = int((lb+rb)/2)
            # 中间点对应的id
            id = e_list[mid]
            # 为中间点构造tree node
            root=binSearchTree()
            root.id=id
            root.path=parent_path+direct

            # 递归求解左子树，得到左子树的根节点与根哈希
            lchild, lhash = binSearchTree.construct_tree(tree, e_list, lb, mid-1, root.path, '0')
            root.lchild=lchild
            root.lhash=lhash

            # 递归求解右子树
            rchild, rhash = binSearchTree.construct_tree(e_list, mid+1, rb, root.path, '1')
            root.rchild = rchild
            root.rhash = rhash

            # 计算根哈希，root_hash=H(id || lhash || rhash)
            root_hash = bytes( Web3.keccak( str(id).encode('utf-8') + lhash + rhash) )

            # 将root加入tree数组
            tree.append(root)

            return len(tree)-1, root_hash
        
    
    
