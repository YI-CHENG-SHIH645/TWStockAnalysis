from strategies.cpp_acc.core import check_int_key_int_value
import numpy as np

if __name__ == '__main__':
    # dic_list = {
    #     "1101": ["1101", "1102", "1103"],
    #     "0050": ["0050", "0052", "0054"],
    #     "2330": ["2330", "2333", "2336"],
    # }
    # check_dict_op(dic_list, "qqq", "ppp")
    # print(dic_list)

    # check_list_to_set(['1102', '1103', '1104'])

    dic = {
        1: 2,
        3: 4,
        5: 6
    }
    check_int_key_int_value(dic)
    print(dic)
