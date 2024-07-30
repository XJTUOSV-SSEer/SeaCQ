from typing import Dict,Set,Tuple,Any, Optional, List
from web3 import Web3
import hmac

class binSearchTree:
    '''
    二叉搜索树的结点以及相关操作
    '''

    # 结点中的文件id
    id: int
    # 左子结点在数组中的下标。若不存在，则为None
    lchild: int
    # 左子结点的hash digest，使用keccak256计算得到，32字节。若不存在左子结点，则lhash为全0
    lhash: bytes
    # 右子结点在数组中的下标。若不存在，则为None
    rchild: int
    # 右子结点的hash digest，使用keccak256计算得到，32字节。若不存在左子结点，则lhash为全0
    rhash: bytes
    # 从根结点到当前结点的路径。一个字符串。根结点为'*'，lchild为0，rchild为1
    path: str

    
    def __init__(self):
        self.id=None
        self.lchild = None
        self.rchild = None
        self.lhash=bytes(32)
        self.rhash=bytes(32)
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
            rchild, rhash = binSearchTree.construct_tree(tree, e_list, mid+1, rb, root.path, '1')
            root.rchild = rchild
            root.rhash = rhash

            # 计算根哈希，root_hash=H(id || lhash || rhash)
            root_hash = bytes( Web3.keccak( str(id).encode('utf-8') + lhash + rhash) )

            # 将root加入tree数组
            tree.append(root)

            return len(tree)-1, root_hash
    


    @staticmethod
    def construct_from_path(tree:List['binSearchTree'], CMAP: Dict[bytes, bytes], tau_w:bytes, 
                            k_w:bytes, current_path:str):
        '''
        根据结点的路径来重建二叉搜索树
        input:
            tree - 储存建立的树结点
            CMAP - 储存 k->v 的映射。k,v都是32字节bytes。
                   k=f(tau_w, path), v=f(k_w, path) xor id
            tau_w - bytes
            k_w - bytes
            current_path - 当前结点的路径。树根的路径为'*'
        output:
            node - 当前结点在tree数组中的下标
            node_hash - 当前结点的哈希
        '''

        ################## 计算路径，并判断这个路径是否存在于CMAP ########################
        # 计算k=f(tau_w, path)
        k=hmac.new(key=tau_w, msg=current_path.encode('utf-8'), digestmod='sha256').digest()
        if k not in CMAP:
            return None, bytes(32)
        
        # 取出v，并得到id
        v=CMAP[k]
        tmp=hmac.new(key=k_w, msg=current_path.encode('utf-8'), digestmod='sha256').digest()
        id = int( bytes(a ^ b for a, b in zip(v, tmp)).decode('utf-8').lstrip('0') )

        # 构造结点
        node = binSearchTree()
        node.id = id
        node.path = current_path


        ################### 计算左、右子结点 ###########################
        lchild, lhash = binSearchTree.construct_from_path(tree, CMAP, tau_w, k_w, current_path+'0')
        rchild, rhash = binSearchTree.construct_from_path(tree, CMAP, tau_w, k_w, current_path+'1')

        node.lchild=lchild
        node.lhash=lhash
        node.rchild=rchild
        node.rhash=rhash

        # 将node加入tree数组
        tree.append(node)
        # 计算根哈希，root_hash=H(id || lhash || rhash)
        node_hash = bytes( Web3.keccak( str(id).encode('utf-8') + lhash + rhash) )

        return len(tree)-1, node_hash
    
    

    @staticmethod
    def update_tree(tree:List['binSearchTree'], id:int):
        '''
        将一个id插入二叉树。注意，被修改的叶结点暂时不计算lhash和rhash
        '''
        # 找到插入位置pre
        pre=0
        ptr = len(tree)-1
        while ptr is not None:
            pre=ptr
            if id < tree[ptr].id:
                ptr = tree[ptr].lchild
            elif id > tree[ptr].id:
                ptr = tree[ptr].rchild

        # 插入节点
        new_node=binSearchTree()
        new_node.id=id
        if id < tree[pre].id:
            new_node.path=tree[pre].path+'0'
            tree[pre].lchild = len(tree)
        else:
            new_node.path=tree[pre].path+'1'
            tree[pre].rchild = len(tree)
        
        tree.append(new_node)
        

    @staticmethod
    def gen_proof(tree:List['binSearchTree'], upd_ids:List[int], proof:List['binSearchTree'], 
                    ptr:int):
        '''
        生成证明。
        定义更新路径：upd_ids中的结点到root的路径成为更新路径
        对每个结点递归的处理，判断左，右子结点是否在更新路径上。若任一子结点在更新路径上，则该结点也在
        更新路径上，proof中加入该结点，且设置对应的lhash/rhash为None，以待后续验证。若该结点不在更新
        路径上，则do nothing
        input:
            tree - 这里的tree包含刚被更新的结点和更新前已在tree中的结点。更新时没有修改相关节点的
                   lhash和rhash
            upd_ids - 被更新的id的列表
            proof - merkle证明。本质上是一棵子树，对应upd_ids中结点的merkle proof，即所有被更新结点的路径，
                    但返回的子树中不包括upd_ids中的结点。
            ptr - 当前结点在tree数组中的下标
        output:
            is_on_path - 若当前node在更新路径上，则为true；否则为false
            ptr_new - 若当前node处生成了一个结点加入proof，则返回proof中的下标
        '''

        #################### 递归边界，判断当前结点是否为新更新的 ####################
        #################### 使用剪枝，一找到upd_ids内的结点就返回 ##################
        if ptr is None:
            return False, None
        
        node = tree[ptr]
        # 判断该结点的id是否为更新的
        if node.id in upd_ids:
            return True, None
        

        #################### 判断左右子结点是否在更新路径上 #########################
        lchild_is_on_path, ptr_new_l = binSearchTree.gen_proof(tree, upd_ids, proof, node.lchild)
        rchild_is_on_path, ptr_new_r = binSearchTree.gen_proof(tree, upd_ids, proof, node.rchild)
        # 某个子结点在更新路径上，则为当前结点复制一个结点，后续作为子树的结点加入proof
        if lchild_is_on_path or rchild_is_on_path:
            new_node = binSearchTree()
            new_node.id = node.id
            # 若左子结点在路径上
            if lchild_is_on_path:
                # 若左子结点在upd_list中
                if ptr_new_l is None:
                    new_node.lchild = None
                else:
                    new_node.lchild = ptr_new_l
            # 若左子结点不在路径上，则新结点的lhash子段复制原来的，lchild字段设置为None
            else:
                new_node.lhash = node.lhash

            # 若右子结点在路径上
            if rchild_is_on_path:
                # 若右子结点在upd_list中
                if ptr_new_r is None:
                    new_node.rchild = None
                else:
                    new_node.rchild = ptr_new_r
            # 若右子结点不在路径上，则新结点的rhash子段复制原来的，rchild字段设置为None
            else:
                new_node.rhash = node.rhash

            # 将new_node加入proof
            proof.append(new_node)

            # 返回
            return True, len(proof)-1
        
        # 结点不在更新路径上
        else:
            return False, None

            







                
    
    @staticmethod
    def update_hash(tree:List['binSearchTree'], ptr:int):
        '''
        更新树中结点的哈希
        input:
            tree - 
            ptr - 当前结点在tree数组中的下标
        output:
            当前结点的哈希
        '''

        ############################## 递归边界 ###############################
        if ptr is None:
            return bytes(32)

        node = tree[ptr]
        lhash = binSearchTree.update_hash(tree, node.lchild)
        rhash = binSearchTree.update_hash(tree, node.rchild)

        # 计算哈希，hash=H(id || lhash || rhash)
        hash = bytes( Web3.keccak( str(node.id).encode('utf-8') + lhash + rhash) )

        return hash
    


    @staticmethod
    def find_min_id(tree:List['binSearchTree'], ptr:int):
        '''
        找到树中最小的id，并返回对应结点在数组中的下标
        input:
            tree - 
            ptr - 当前结点在数组中的下标
        output:
            ptr - 最小结点在数组中的下标
        '''

        # 递归边界
        if tree[ptr].lchild is None:
            return ptr
        
        ptr = tree[ptr].lchild
        return binSearchTree.find_min_id(tree, ptr)
    



    @staticmethod
    def merkle_prove(tree:List['binSearchTree'], proof:List['binSearchTree'], node_set:Set[int], ptr:int, 
                     index_map:Dict[int, int]):
        '''
        给定一组结点，为其作merkle prove，并计算原树结点与merkle子树结点间的index映射关系
        input:
            tree - 
            proof - merkle子树
            node_set - 要prove的结点在tree中的index集合
            ptr - 当前结点在tree中的index
            index_map - 映射表，将同一结点在tree中的index映射到在proof中的index
        output:
            is_on_path - 若当前node在更新路径上，则为true；否则为false
            ptr_new - 若当前node处生成了一个结点加入proof，则返回proof中的下标
        '''

        # 每个结点三种情况：
        # (1) 左/右结点在更新路径上，则该结点也在更新路径上，将该结点作为内部结点加入merkle proof
        # (2) 不符合(1)，但是在node_set中，则该结点在更新路径上，将该结点作为叶结点加入merkle proof
        # (3) 不符合(1),(2)，则该结点不在更新路径上，直接返回

        # 递归边界，判断ptr是否为None
        if ptr is None:
            return False, None

        
        # 递归的获取左，右子结点的证明
        lchild_is_on_path, ptr_new_l = binSearchTree.merkle_prove(tree, proof, node_set, tree[ptr].lchild, index_map)
        rchild_is_on_path, ptr_new_r = binSearchTree.merkle_prove(tree, proof, node_set, tree[ptr].rchild, index_map)

        # 判断结点属于哪种情况
        # 情况(1)
        if lchild_is_on_path or rchild_is_on_path:
            # 创建新结点
            new_node=binSearchTree()
            new_node.id = tree[ptr].id
            new_node.path = tree[ptr].path
            # 判断左子结点
            if lchild_is_on_path:
                new_node.lchild = ptr_new_l
            else:
                new_node.lhash = tree[ptr].lhash
            # 判断右子结点
            if rchild_is_on_path:
                new_node.rchild = ptr_new_r
            else:
                new_node.rhash = tree[ptr].rhash
            
            # 将结点加入proof
            proof.append(new_node)

            # 更新映射关系
            index_map[ptr] = len(proof)-1

            return True, len(proof)-1
        
        # 情况(2)
        elif ptr in node_set:
            # 创建新结点
            new_node=binSearchTree()
            new_node.id = tree[ptr].id
            new_node.path = tree[ptr].path
            new_node.lhash = tree[ptr].lhash
            new_node.rhash = tree[ptr].rhash

            # 将结点加入proof
            proof.append(new_node)

            # 更新映射关系
            index_map[ptr] = len(proof)-1

            return True, len(proof)-1
        
        # 情况(3)
        else:
            return False, None
    

    @staticmethod
    def is_neighbor(tree:List['binSearchTree'], lb:int, ub:int):
        '''
        判断所给lb和ub是否在树中中序遍历相邻，即中序遍历序列中两个元素相邻
        input:
            lb - 结点在tree中的下标
            ub - 
        output:
            flag - 若相邻，返回true
        '''

        # 首先判断lb是否存在右子结点。若存在，在右子结点对应的子树中搜索

        # 若恶意服务器没有在proof中包含右子结点，而是给出了rhash，则存在欺骗行为
        # 因为若lb包括右子结点，则ub必定在右子结点对应的子树中，必定有一部分在proof中
        if (tree[lb].rhash != bytes(32)) and (tree[lb].rchild is None):
            return False
        
        if tree[lb].rchild is not None:
            # 找到右子结点对应子树的min id
            ptr = binSearchTree.find_min_id(tree, tree[lb].rchild)
            # 判断是否与ub相等
            if ptr!=ub:
                return False
            
        else:
            # 根据路径推断ub。对lb的路径，找到最后一个0，并将这个0以及之后的字串截取掉，即可得到ub的路径
            # 例如，假设lb=00001001，则ub=000010
            lb_path = tree[lb].path
            if lb_path.rfind('0') == -1:
                return False

            ub_path = lb_path[0:lb_path.rfind('0')]
            # 找到ub_path对应结点在tree中的下标ptr
            ptr = len(tree)-1
            i = 1       # 标识当前搜索到ub_path的第几位
            while i< len(ub_path):
                if ub_path[i] == '0':
                    ptr = tree[ptr].lchild
                elif ub_path[i] == '1':
                    ptr = tree[ptr].rchild
                
                i += 1
            
            # 若ub_path对应结点不等于ub，返回false
            if ptr != ub:
                return False
        
        return True


    @staticmethod
    def cal_hash_root(merkle_proof: List['binSearchTree'], ptr:int):
        '''
        给定merkle proof（一棵子树），重新计算hash_root
        input:
            merkle_proof - merkle证明，本质是一棵子树
            ptr - 当前结点在merkle_proof数组中的下标
        output:
            hash_root - 以ptr为根结点的子树的根哈希
        '''

        # 递归时，结点可以分为几类：
        # (1)在原树中是内部结点，但在merkle proof中是叶结点。child==None, hash!=0
        # (2)child不为None
        # (3)child==None, hash==0

        # 计算得到的当前结点的lhash, rhash
        lhash=None
        rhash=None

        # 求lhash
        # 情况(1)(3)合并，直接使用当前节点中储存的child hash
        if merkle_proof[ptr].lchild is None:
            lhash = merkle_proof[ptr].lhash
        else:
            # 在lchild不为none的情况下，若lhash不为0，则说明该结点是被篡改的
            if merkle_proof[ptr].lhash != bytes(32):
                print("merkle proof node is tampered")
            # 递归的调用，计算左子树的root hash
            lhash = binSearchTree.cal_hash_root(merkle_proof, merkle_proof[ptr].lchild)
        
        # 求rhash
        # 情况(1)(3)合并，直接使用当前节点中储存的child hash
        if merkle_proof[ptr].rchild is None:
            rhash = merkle_proof[ptr].rhash
        else:
            # 在lchild不为none的情况下，若lhash不为0，则说明该结点是被篡改的
            if merkle_proof[ptr].rhash != bytes(32):
                print("merkle proof node is tampered")
            # 递归的调用，计算左子树的root hash
            rhash = binSearchTree.cal_hash_root(merkle_proof, merkle_proof[ptr].rchild)
        
        
        # 计算root_hash = H(id||lhash||rhash)
        root_hash = bytes( Web3.keccak( str(merkle_proof[ptr].id).encode('utf-8') + lhash + rhash) )
        return root_hash