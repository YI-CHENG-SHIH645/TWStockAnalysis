//
// Created by 施奕成 on 2023/3/10.
//

#pragma once
#include <omp.h>
#include <vector>
#include <tuple>
#include <map>

typedef std::vector<std::string>> StrArr;
typedef std::vector<std::set>> StrSet;
typedef std::vector<float> FloatArr;
typedef std::map<std::string, std::string> Record;

bool sell_logic(int, int, float, float);

std::tuple<float, float, float> get_pnl(float, float);

void trade(std::map<int, Record> &dic_records,
           int tid,
           std::string &sid,
           float open_price,
           int holding_days,
           int holding_days_th,
           std::map<std::string, StrArr> &last_date_signal,
           int &available_tid,
           FloatArr &o,
           FloatArr &c,
           FloatArr &ma20,
           StrArr &dates,
           std::map<std::string, StrSet> &selected,
           std::string &strategy_name,
           std::string &trader_code)

