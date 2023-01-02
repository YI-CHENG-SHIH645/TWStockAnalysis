#include <iostream>
#include <vector>
#include <tuple>
#include <pybind11/pybind11.h>
#include <pybind11/chrono.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#define datetime std::chrono::system_clock::time_point

namespace py = pybind11;

void show_datetime(datetime t) {
  std::time_t time_tt = std::chrono::system_clock::to_time_t(t);
  std::cout << std::ctime(&time_tt) << std::endl;
}

bool sell_logic(int hd, int hd_th, float adj_c, float adj_c_ma20) {
  return (hd >= hd_th) || (adj_c < adj_c_ma20);
}

std::tuple<float, float, float> get_pnl(float open_price, float sell_price) {
  float tax = 0.003f * sell_price;
  float fee = 0.001425f * 0.6f * (sell_price + open_price);
  float pnl = (sell_price - open_price - tax - fee) / open_price;
  tax = std::round(tax*1000 * 100) / 100;
  fee = std::round(fee*1000 * 100) / 100;
  pnl = std::round(pnl*100 * 100) / 100;

  return std::make_tuple(pnl, tax, fee);
}

void trade(py::dict &dic_records,
           int tid,
           std::string &sid,
           float open_price,
           int holding_days,
           int holding_days_th,
           py::dict &last_date_signal,
           datetime today,
           int &available_tid,
           py::array_t<float> &o,
           py::array_t<float> &c,
           py::array_t<float> &ma20,
           std::vector<datetime> &dates,
           py::dict &selected,
           std::string &strategy_name,
           std::string &trader_code) {
  auto ptr_o = static_cast<float *>(o.request().ptr);
  auto ptr_c = static_cast<float *>(c.request().ptr);
  auto ptr_ma20 = static_cast<float *>(ma20.request().ptr);
  auto last_date_sell_list = py::cast<py::list>(last_date_signal["sell"]);

  for (size_t idx = 0; idx < o.size(); ++idx) {
    if (!std::isnan(open_price)) {
      holding_days += (idx != o.size() - 1);
      // try to sell
      if (sell_logic(holding_days, holding_days_th, ptr_c[idx], ptr_ma20[idx])) {
        if (idx == o.size() - 1) {
          last_date_sell_list.append(sid);
          break;
        }

        float sell_price = ptr_o[idx + 1];
        auto triplet = get_pnl(open_price, sell_price);
        datetime sell_date = dates[idx + 1];

        dic_records[std::to_string(tid).c_str()]["close_date"] = sell_date;
        dic_records[std::to_string(tid).c_str()]["close_price"] = sell_price;
        dic_records[std::to_string(tid).c_str()]["holding_days"] = holding_days;
        dic_records[std::to_string(tid).c_str()]["pnl"] = std::get<0>(triplet);
        dic_records[std::to_string(tid).c_str()]["tax"] = std::get<1>(triplet);
        dic_records[std::to_string(tid).c_str()]["fee"] = std::get<2>(triplet);

        open_price = std::nanf("");
        holding_days = 0;

        tid = available_tid;
        dic_records[std::to_string(tid).c_str()]["sid"] = sid;
        dic_records[std::to_string(tid).c_str()]["strategy_name"] = strategy_name;
        dic_records[std::to_string(tid).c_str()]["trader_code"] = trader_code;
        dic_records[std::to_string(tid).c_str()]["holding_days"] = holding_days;
        dic_records[std::to_string(tid).c_str()]["last_check"] = today;
        dic_records[std::to_string(tid).c_str()]["open_price"] = open_price;
        available_tid += 1;
      }
    } else {
      // try to buy
      if (selected.attr("get")(dates[idx], py::list()).contains(sid)) {
        if (idx < o.size() - 1) {
          datetime buy_date = dates[idx + 1];
          float buy_price = ptr_o[idx + 1];
          dic_records[std::to_string(tid).c_str()]["open_date"] = buy_date;
          dic_records[std::to_string(tid).c_str()]["open_price"] = buy_price;
          dic_records[std::to_string(tid).c_str()]["long_short"] = "long";
          dic_records[std::to_string(tid).c_str()]["shares"] = 1;
          open_price = buy_price;
          holding_days = 1;
        }
      }
    }
  }
  if(!std::isnan(open_price)) {
    auto triplet = get_pnl(open_price, ptr_c[c.size()-1]);
    dic_records[std::to_string(tid).c_str()]["holding_days"] = holding_days;
    dic_records[std::to_string(tid).c_str()]["pnl"] = std::get<0>(triplet);
  }
}


void trade_on_sids(std::vector<std::string> &sids,
                   py::dict &o,
                   py::dict &c,
                   py::dict &ma20,
                   std::vector<datetime> &dates,
                   py::dict &selected,
                   int holding_days_th,
                   py::dict &dic_records,
                   py::dict &last_date_signal,
                   py::dict &sid2tid,
                   datetime today,
                   int available_tid,
                   std::string &strategy_name,
                   std::string &trader_code) {
  int tid;
  for(auto sid : sids) {
    py::dict r;
    if(!sid2tid.contains(sid)) {
      r["sid"] = sid;
      r["strategy_name"] = strategy_name;
      r["trader_code"] = trader_code;
      r["holding_days"] = 0;
      r["last_check"] = today;
      r["open_price"] = std::nanf("");
      tid = available_tid;
      dic_records[std::to_string(tid).c_str()] = r;
      available_tid += 1;
    } else {
      tid = py::cast<int>(sid2tid[sid.c_str()]);
      r = dic_records[sid2tid[sid.c_str()]];
    }
    py::array_t<float> o_ = py::cast<py::array_t<float>>(o[sid.c_str()]);
    py::array_t<float> c_ = py::cast<py::array_t<float>>(c[sid.c_str()]);
    py::array_t<float> ma20_ = py::cast<py::array_t<float>>(ma20[sid.c_str()]);

    float open_price = py::cast<float>(r["open_price"]);
    dic_records[std::to_string(tid).c_str()]["last_check"] = today;
    int holding_days = py::cast<int>(r["holding_days"]);
    trade(dic_records, tid, sid,
          open_price, holding_days, holding_days_th,
          last_date_signal, today, available_tid,
          o_, c_, ma20_, dates,
          selected, strategy_name, trader_code);
  }
}


py::array_t<double> add_two_array(py::array_t<double> &a, py::array_t<double> &b, float aux) {
  std::cout << a.size() << std::endl;
  py::buffer_info a_buf = a.request(), b_buf = b.request();
  auto result = py::array_t<double>(a_buf.size);
  py::buffer_info result_buf = result.request();

  auto ptr_a = static_cast<double *>(a_buf.ptr);
  auto ptr_b = static_cast<double *>(b_buf.ptr);
  auto ptr_r = static_cast<double *>(result_buf.ptr);

  for (size_t idx = 0; idx < a_buf.shape[0]; idx++)
    ptr_r[idx] = ptr_b[idx] + ptr_a[idx];
  ptr_a[0] = 4;
  std::cout << std::isnan(aux) << std::endl;
  return result;
}

void check_dic_list(py::dict &d) {
  for(auto p : d) {
    const std::string& date = py::cast<const std::string>(p.first);
    std::cout << "date: " << date << " : ";
    auto sid_list = py::cast<py::list>(p.second);
    sid_list.append("g");
    for (const auto & iter : sid_list) {
      std::cout << iter << " ";
    }
    std::cout << std::endl;
  }
}

void check_dict_op(py::dict &d, py::str &c1, py::str &c2) {
  int a = 3;
  d[std::to_string(a).c_str()] = 3;
  py::dict r;
  r["sid"] = c1;
  r["strategy_name"] = c2;
  d[std::to_string(a).c_str()] = r;
  d[std::to_string(a).c_str()]["b"] = 3;
}

void check_int_key_int_value(py::dict &d) {
  for(auto p : d) {
    std::cout << p.first << " " << p.second << " " << p.first + p.second << " " << std::endl;
  }
  d[std::to_string(3).c_str()] = 5;
}

void check_datetime_key(py::dict &d, std::vector<datetime> dts) {
  std::cout << d.attr("get")(dts[0]) << std::endl;
  std::cout << d.attr("get")(dts[0]).contains(2) << std::endl;
  std::cout << d.attr("get")(dts[0]).contains(3) << std::endl;
  std::cout << d.attr("get")(dts[1]) << std::endl;
  std::cout << d.attr("get")(dts[1]).contains(2) << std::endl;
  std::cout << d.attr("get")(dts[1]).contains(3) << std::endl;
}

PYBIND11_MODULE(core, m) {
  m.def("check_datetime_key", &check_datetime_key);
  m.def("trade_on_sids", &trade_on_sids);
}
