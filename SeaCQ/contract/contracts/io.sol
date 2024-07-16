pragma solidity >=0.4.22 <0.6.0;

contract ADS {
    // 定义存储动态字节数组的 mapping
    mapping(bytes16 => bytes) public dict;


    // 将bytes1[]字节数组转换为bytes动态数组
    function convert1(bytes1[] memory byteArray) private pure returns (bytes memory) {
        // 创建一个新的动态字节数组，长度与 bytes1[] 相同
        bytes memory result = new bytes(byteArray.length);

        // 将 bytes1[] 的每个元素复制到新的 bytes 动态数组中
        for (uint i = 0; i < byteArray.length; i++) {
            result[i] = byteArray[i];
        }

        return result;
    }

    // 将bytes动态数组转换为bytes1[]字节数组
    function convert2(bytes memory byteArray) private pure returns (bytes1[] memory) {
        // 创建一个新的 bytes1[] 数组，长度与 bytes 数组相同
        bytes1[] memory result = new bytes1[](byteArray.length);

        // 将 bytes 数组的每个元素复制到新的 bytes1[] 数组中
        for (uint i = 0; i < byteArray.length; i++) {
            result[i] = byteArray[i];
        }

        return result;
    }

    function test(int a) public{
        
    }




    // 设置动态字节数组的值
    function setADS(bytes16 _key, bytes1[] memory _value) public {
        dict[_key] = convert1(_value);
    }



    // 获取动态字节数组的值
    function getADS(bytes16 _key) public view returns (bytes1[] memory) {
        return convert2(dict[_key]);
    }
}