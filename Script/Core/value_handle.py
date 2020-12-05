import random
import bisect
import itertools
from typing import Dict, List


def two_bit_array_to_dict(array: tuple) -> dict:
    """
    将二维数组转换为字典
    Keyword arguments:
    array -- 要转换的二维数组
    """
    return {x: y for x, y in array}


def get_region_list(now_data: Dict[any, int]) -> dict:
    """
    按dict中每个value的值对key进行排序，并计算权重区域列表
    Keyword arguments:
    now_data -- 需要进行计算权重的dict数据
    """
    sort_data = sorted_dict_for_values(now_data)
    return dict(zip(itertools.accumulate(sort_data.values()), sort_data.keys()))


def sorted_dict_for_values(old_dict: Dict[any, int]) -> dict:
    """
    按dict中每个value的值对key进行排序生成新dict
    Keyword arguments:
    old_dict -- 需要进行排序的数据
    """
    return two_bit_array_to_dict(sorted(old_dict.items(), key=lambda x: x[1]))


def get_random_for_weight(data: Dict[any, int]) -> any:
    """
    按权重随机获取dict中的一个key
    Keyword arguments:
    data -- 需要随机获取key的dict数据
    """
    weight_max = sum(data.values())
    weight_region_data = get_region_list(data)
    weight_region_list = [int(i) for i in weight_region_data.keys()]
    now_weight = random.randint(0, weight_max - 1)
    weight_region = get_next_value_for_list(now_weight, weight_region_list)
    return weight_region_data[weight_region]


def get_next_value_for_list(now_int: int, int_list: List[int]) -> int:
    """
    获取列表中第一个比指定值大的数
    Keyword arguments:
    now_int -- 作为获取参考的指定数值
    int_list -- 用于取值的列表
    """
    now_id = bisect.bisect_left(int_list, now_int)
    return int_list[now_id]


def get_old_value_for_list(now_int: int, int_list: List[int]) -> int:
    """
    获取列表中第一个比指定值小的数
    Keyword arguments:
    now_int -- 作为获取参考的指定数值
    int_list -- 用于取值的列表
    Return arguments:
    int -- 查询到的值
    """
    now_id = bisect.bisect_right(int_list, now_int)
    return int_list[now_id - 1]


def list_of_groups(init_list: list, children_list_len: int) -> List[list]:
    """
    将列表分割为指定长度的列表集合
    Keyword arguments:
    init_list -- 原始列表
    children_list_len -- 指定长度
    Return arguments:
    List[list] -- 新列表
    """
    list_of_groups = zip(*(iter(init_list),) * children_list_len)
    end_list = [list(i) for i in list_of_groups]
    count = len(init_list) % children_list_len
    end_list.append(init_list[-count:]) if count != 0 else end_list
    return end_list
