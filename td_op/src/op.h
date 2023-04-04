//
// Created by 施奕成 on 2023/3/10.
//

#pragma once
#include <cassert>
#include <cmath>
#include <map>
#include <omp.h>
#include <set>
#include <string>
#include <tuple>
#include <vector>

typedef std::string str;
template <typename T> using Set = std::set<T>;
template <typename T> using Vec = std::vector<T>;
template <typename T> using Map = std::map<std::string, T>;

struct TradingInfo {

public:
  friend class Trader;
  TradingInfo(const str &strategy_name, const str &trader_code,
              int holding_days_th, int available_tid,
              const Map<Set<str>> &selected)
      : strategy_name(strategy_name), trader_code(trader_code),
        holding_days_th(holding_days_th), available_tid(available_tid),
        selected(selected) {}

private:
  const str &strategy_name;
  const str &trader_code;
  int holding_days_th;
  int available_tid;
  const Map<Set<str>> &selected;
};

struct PriceData {

public:
  friend class Trader;
  PriceData(const Vec<str> &sids, const Vec<str> &dates,
            const Map<Vec<float>> &o, const Map<Vec<float>> &c,
            const Map<Vec<float>> &ma20)
      : sids(sids), dates(dates), o(o), c(c), ma20(ma20) {}

private:
  const Vec<str> &sids;
  const Vec<str> &dates;
  const Map<Vec<float>> &o;
  const Map<Vec<float>> &c;
  const Map<Vec<float>> &ma20;
};

class Trader {

public:
  Trader(TradingInfo &trading_info, const PriceData &price_data,
         const Map<int> &sid2tid, Map<Map<str>> &dic_records,
         Map<Vec<str>> &last_date_signal)
      : trading_info(trading_info), price_data(price_data), sid2tid(sid2tid),
        dic_records(dic_records), last_date_signal(last_date_signal) {}

  Map<Map<str>> trade_serial();

private:
  Map<str> new_record(const str &);
  bool sell_logic(const str &, size_t, int);
  static std::tuple<float, float, float> get_pnl(float, float);
  TradingInfo &trading_info;
  const PriceData &price_data;
  const Map<int> &sid2tid;
  Map<Map<str>> &dic_records;
  Map<Vec<str>> &last_date_signal;
};
