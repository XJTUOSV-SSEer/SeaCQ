pragma solidity >=0.4.22 <0.6.0;
pragma experimental ABIEncoderV2;

contract Merkle{
    // BMAP，储存每棵树tau_w -> root_hash 的映射
    mapping(bytes32 => bytes32) public BMAP;

    // UMAP，储存tau_w_upd -> H_w_upd的映射，即每批更新id的摘要
    mapping(bytes32 => bytes32) public UMAP;

    // 二叉树结点
    struct Node{
        // 文件id，正整数
        uint id;
        // 左子结点在tree数组中的下标
        // 若为-1，标识不存在左/右子结点
        int lchild;
        int rchild;
        // 左/右子结点的哈希
        bytes32 lhash;
        bytes32 rhash;
    }

    // 批量设置BMAP
    // _k_list储存若干k，_v_list储存若干value，且元素的顺序与_k_list一致。
    // batch_size为当前批次的元素数量
    function batch_setBMAP(bytes32[] memory _k_list, bytes32[] memory _v_list, uint batch_size) public {
        for(uint i=0; i<batch_size; i++){
            bytes32 tau_w = _k_list[i];
            bytes32 root_hash = _v_list[i];
            BMAP[tau_w] = root_hash;
        }
    }

    // 设置UMAP
    function set_UMAP(bytes32 k, bytes32 v) public{
        UMAP[k] = v;
    }

    // 读取root_hash
    function get_BMAP(bytes32 tau_w) public view returns (bytes32){
        return BMAP[tau_w];
    }


    // 验证并更新tau_w对应的树，并重新计算root_hash
    // size - merkle proof数组长度。size-1为树根的下标
    // upd_id_list - 被更新的id
    // upd_id_size - upd_id_list长度
    function update_tree(bytes32 tau_w, bytes32 tau_w_upd,uint[] memory id_list, int[] memory lchild_list, int[] memory rchild_list,
                         bytes32[] memory lhash_list, bytes32[] memory rhash_list, uint size, 
                         uint[] memory upd_id_list, uint upd_id_size) public{
        // 将输入转换为Node数组。动态地定义数组。
        Node[] memory tree = new Node[](size+upd_id_size);
        for(uint i=0; i<size; i++){
            // 创建一个Node
            Node memory n;
            n.id = id_list[i];
            n.lchild = lchild_list[i];
            n.rchild = rchild_list[i];
            n.lhash = lhash_list[i];
            n.rhash = rhash_list[i];

            // 将node加入tree。注意，memory数组不能用push
            tree[i]=n;
        }

        // 对tree计算hash root，并与本地保存的hash root对比
        bytes32 h = cal_root_hash(tree, size-1);
        require(h==BMAP[tau_w]);


        // 判断id_list对应的multi-set hash是否等于UMAP中储存的
        require(multiset_hash(upd_id_list, upd_id_size) == UMAP[tau_w_upd]);


        // 根据id_list更新hash_root
        // 首先将id_list中的id插入二叉树
        for(uint i=0; i<upd_id_size; i++){
            insert_node(tree, size-1, upd_id_list[i], size + i);
        }
        // 重新计算二叉树的根哈希，并更新BMAP
        BMAP[tau_w] = cal_root_hash(tree, size-1);
    }


    // 对给定的merkle proof tree，计算根哈希
    function cal_root_hash(Node[] memory tree, uint ptr) private returns (bytes32) {
        // 递归时，结点可以分为几类：
        // (1)在原树中是内部结点，但在merkle proof中没有child。child==-1, hash!=0
        // (2)child不为None
        // (3)child==-1, hash==0

        // 计算得到的child hash
        bytes32 lhash;
        bytes32 rhash;

        if(tree[ptr].lchild == -1){
            lhash = tree[ptr].lhash;
        }
        else{
            lhash = cal_root_hash(tree, uint(tree[ptr].lchild));
        }

        if(tree[ptr].rchild == -1){
            rhash = tree[ptr].rhash;
        }
        else{
            rhash = cal_root_hash(tree, uint(tree[ptr].rchild));
        }

        // 计算当前结点的哈希
        // 首先将id与lhash, rhash拼接
        bytes memory b = abi.encodePacked(num_to_bytes(tree[ptr].id), lhash, rhash);
        return keccak256(b);
    }




    // 将uint类型数据转换为对应的字符串字面量，然后转换为bytes
    function num_to_bytes(uint v) private pure returns (bytes memory){
        if(v==0){
            return "0";
        }

        // 判断数值有几位
        uint tmp=v;
        uint len=0;
        while(tmp!=0){
            len++;
            tmp = tmp / 10;
        }

        // 储存bytes数据
        bytes memory buf = new bytes(len);
        uint idx = len-1;
        tmp=v;

        while(tmp!=0){
            buf[idx] = bytes1(uint8(tmp%10 +48));
            idx--;
            tmp = tmp/10;
        }

        return buf;
    }


    // 将id加入tree
    // idx - 新结点被插入数组后的下标
    function insert_node(Node[] memory tree, uint root_idx, uint id, uint idx) public pure {
        // 从根结点开始搜索，将id插入
        int ptr = int(root_idx);
        // 搜索的前一个结点在数组中的下标
        uint pre;

        while(ptr != -1){
            pre = uint(ptr);
            // 判断往左还是往右搜索
            if(tree[uint(ptr)].id > id){
                // 更新ptr
                ptr = tree[uint(ptr)].lchild;
            }
            else{
                ptr = tree[uint(ptr)].rchild;
            }
        }

        // 创建并插入结点
        Node memory n;
        n.id = id;
        n.lchild = -1;
        n.rchild = -1;
        tree[idx] = n;
        
        // 更新tree[pre]
        if(id < tree[pre].id){
            tree[pre].lchild = int(idx);
        }
        else if(id > tree[pre].id){
            tree[pre].rchild = int(idx);
        }
    }



    // 对给定的upd_id_list，计算multi-set hash
    function multiset_hash(uint[] memory upd_id_list, uint upd_id_size) public pure returns (bytes32){
        // 结果
        bytes32 r;
        // 遍历upd_id_list中所有id
        for(uint i=0; i<upd_id_size; i++){
            // 计算H(id)
            bytes32 h_id = keccak256(num_to_bytes(upd_id_list[i]));
            // 异或
            r = r^h_id;
        }

        return r;
    }


}