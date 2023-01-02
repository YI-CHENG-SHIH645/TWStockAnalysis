import datetime
from collections import defaultdict
from strategies.cpp_acc.core import receive_dict
import numpy as np
import pandas as pd

if __name__ == '__main__':
    # dic = defaultdict(list, {"CPU": [12, 14, 16], "GPU": [14, 16, 18], "RAM": [16, 18, 20]})
    dic = {"CPU": 1, "GPU": 2, "RAM": "3"}
    dic = receive_dict(dic)
    print(dic)
