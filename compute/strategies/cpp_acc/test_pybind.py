from dataclasses import dataclass
from typing import List, Dict, Set
import numpy as np


@dataclass
class DataCollection:
    int_list: List[int]
    str_list: List[str]
    int2str: Dict[int, str]
    str2dict: Dict[str, Set[int]]
    str2arr: Dict[str, np.ndarray]


if __name__ == '__main__':
    int_list = [1, 2, 3, 4, 5]
    str_list = ["apple", "banana", "car", "dina", "watermelon"]
    int2str = {
        6: "hotel",
        7: "steak",
        8: "moon"
    }
    str2dict = {
        "Japan": {22, 122},
        "Korea": {33, 124},
        "Taiwan": {23, 120},
        "Singapore": {1, 103}
    }
    str2arr = {
        "1101": np.array([30, 40, 50]),
        "2330": np.array([300, 400, 500]),
        "9958": np.array([125, 114, 178]),
    }
    data_obj = DataCollection(int_list, str_list, int2str, str2dict, str2arr)
