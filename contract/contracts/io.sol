pragma solidity >=0.4.22 <0.6.0;
pragma experimental ABIEncoderV2;

contract ADS {
    // 定义存储ACC_w的 mapping
    mapping(bytes16 => bytes) public dict_w;
    // 定义存储ACC_fid的 mapping
    mapping(bytes16 => bytes) public dict_fid;

    // bytes数组，第一个元素为ADS，第二个元素为P
    bytes[2] public total_ADS;


    // 设置一个k-v pair到dict。k为字符串，v为动态数组
    // typ为要设置的mapping。若typ==1，加入dict_w；若typ==2，加入dict_fid
    function setADS(bytes16 _key, bytes memory _value, uint typ) public {
        if(typ==1){
            dict_w[_key] = _value;
        }
        else if(typ==2){
            dict_fid[_key] = _value;
        }
        
    }

    // 批量设置k-v pair
    // _k_list储存若干k，_v_list储存若干value，且元素的顺序与_k_list一致。
    // batch_size为当前批次的元素数量
    // typ为要设置的mapping。若typ==1，加入dict_w；若typ==2，加入dict_fid
    function batch_setADS(bytes16[] memory _k_list,bytes[] memory _v_list,uint batch_size, uint typ) public{
        for(uint i=0;i<batch_size;i++){
            bytes16 _key=_k_list[i];
            bytes memory _value=_v_list[i];
            if(typ==1){
                dict_w[_key]=_value;
            }
            else if(typ==2){
                dict_fid[_key]=_value;
            }
        }
    }


    // 获取dict的值。k为字符串
    // typ为要设置的mapping。若typ==1，访问dict_w；若typ==2，访问dict_fid
    function getADS(bytes16 _key, uint typ) public view returns (bytes memory) {
        if(typ==1){
            return dict_w[_key];
        }
        else if(typ==2){
            return dict_fid[_key];
        }        
    }



    // 设置ACC_ADS和ACC_P
    function set(bytes memory ads, bytes memory p) public {
        total_ADS[0]=ads;
        total_ADS[1]=p;
    }

    // 返回ACC_ADS和ACC_P
    function get() public view returns (bytes[2] memory){
        return total_ADS;
    }


}