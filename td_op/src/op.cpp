//
// Created by 施奕成 on 2023/3/10.
//
#include "op.h"
#include <omp.h>

Map<Map<str>> Trader::trade_serial() {

  for (auto ptr_sid = price_data.sids.begin(); ptr_sid < price_data.sids.end();
       ++ptr_sid) {
    int tid;
    Map<str> record;
    if (auto search = sid2tid.find(*ptr_sid); search == sid2tid.end()) {
      record = new_record(*ptr_sid);
      tid = __sync_fetch_and_add(&trading_info.available_tid, 1);
      dic_records.insert({std::to_string(tid), record}); // critical section
    } else {
      tid = sid2tid.find(*ptr_sid)->second;
      dic_records.find(std::to_string(tid))->second.find("last_check")->second =
          "today";
      record = dic_records.find(std::to_string(sid2tid.find(*ptr_sid)->second))
                   ->second;
    }

    float open_price = std::stof(record.find("open_price")->second);
    int holding_days = std::stoi(record.find("holding_days")->second);
    assert(dic_records.find(std::to_string(tid)) == dic_records.end());

    for (size_t idx = 0; idx < price_data.o.size(); ++idx) {
      if (!std::isnan(open_price)) {
        holding_days += (idx != price_data.o.size() - 1);
        if (sell_logic(*ptr_sid, idx, holding_days)) {
          if (idx == price_data.o.size() - 1) {
            last_date_signal["sell"].push_back(*ptr_sid);
            break;
          }

          auto sell_date = price_data.dates[idx + 1];
          auto sell_price = price_data.o.at(*ptr_sid)[idx + 1];
          auto triplet = get_pnl(open_price, sell_price);
          auto dr = dic_records.find(std::to_string(tid));
          dr->second.find("close_date")->second = sell_date;
          dr->second.find("close_price")->second = std::to_string(sell_price);
          dr->second.find("holding_days")->second =
              std::to_string(holding_days);
          dr->second.find("pnl")->second = std::to_string(std::get<0>(triplet));
          dr->second.find("tax")->second = std::to_string(std::get<1>(triplet));
          dr->second.find("fee")->second = std::to_string(std::get<2>(triplet));

          open_price = std::stof("NAN");
          holding_days = 0;
          record = new_record(*ptr_sid);
          tid = __sync_fetch_and_add(&trading_info.available_tid, 1);
          dic_records.insert({std::to_string(tid), record}); // critical section
        } else {
          if (auto s = trading_info.selected.find(price_data.dates[idx]);
              s != trading_info.selected.end() && s->second.count(*ptr_sid)) {
            if (idx < price_data.o.size() - 1) {
              auto buy_date = price_data.dates[idx + 1];
              float buy_price = price_data.o.at(*ptr_sid)[idx + 1];
              assert(!std::isnan(buy_price));

              auto dr = dic_records.find(std::to_string(tid));
              dr->second.find("open_date")->second = buy_date;
              dr->second.find("open_price")->second = std::to_string(buy_price);
              dr->second.find("long_short")->second = "long";
              dr->second.find("shares")->second = "1";

              open_price = buy_price;
              holding_days = 1;
            }
          }
        }
      }
    }

    if (!std::isnan(open_price)) {
      auto triplet = get_pnl(
          open_price, price_data.c.at(*ptr_sid)[price_data.c.size() - 1]);
      auto dr = dic_records.find(std::to_string(tid));
      dr->second.find("holding_days")->second = std::to_string(holding_days);
      dr->second.find("pnl")->second = std::to_string(std::get<0>(triplet));
    }
    // ends on one stock
  }

  return dic_records;
}

Map<str> Trader::new_record(const str &sid) {
  return {{"sid", sid},
          {"strategy_name", trading_info.strategy_name},
          {"trader_code", trading_info.trader_code},
          {"holding_days", "0"},
          {"last_check", "today"},
          {"open_price", "NAN"},
          {"open_date", "NAN"},
          {"close_price", "NAN"},
          {"close_date", "NAN"},
          {"holding_days", "NAN"},
          {"pnl", "NAN"},
          {"tax", "NAN"},
          {"fee", "NAN"},
          {"long_short", "NAN"},
          {"shares", "NAN"}};
}

bool Trader::sell_logic(const str &sid, size_t idx, int holding_days) {
  return (holding_days >= trading_info.holding_days_th) ||
         (price_data.c.at(sid)[idx] < price_data.ma20.at(sid)[idx]);
}

std::tuple<float, float, float> Trader::get_pnl(float, float) { return {}; }
