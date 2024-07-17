pragma solidity >=0.4.22 <0.6.0;
pragma experimental ABIEncoderV2;

contract ADS {
    // 定义存储动态字节数组的 mapping
    mapping(bytes16 => bytes) public dict;

    // 设置一个k-v pair到dict。k为字符串，v为动态数组
    function setADS(bytes16 _key, bytes memory _value) public {
        dict[_key] = _value;
    }

    // 批量设置k-v pair
    // _k_list储存若干k，_v_list储存若干value，且元素的顺序与_k_list一致。
    // batch_size为当前批次的元素数量
    function batch_setADS(bytes16[] memory _k_list,bytes[] memory _v_list,uint batch_size) public{
        for(uint i=0;i<batch_size;i++){
            bytes16 _key=_k_list[i];
            bytes memory _value=_v_list[i];
            dict[_key]=_value;
        }
    }


    // 获取dict的值。k为字符串
    function getADS(bytes16 _key) public view returns (bytes memory) {
        return dict[_key];
    }
}