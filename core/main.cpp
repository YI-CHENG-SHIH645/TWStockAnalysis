#include <iostream>
#include <unordered_set>
#include <set>
#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/chrono.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#define datetime std::chrono::system_clock::time_point

namespace py = pybind11;


int trade(py::dict &dic_records,
          int tid,
          int available_tid,
          py::str &sid,
          float open_price,
          int holding_days,
          py::dict &last_date_signal,
          datetime today,
          py::array_t<float> o,
          py::array_t<float> c,
          py::array_t<std::chrono::system_clock::time_point> dates) {
  auto ptr_o = static_cast<float *>(o.request().ptr);
  auto ptr_c = static_cast<float *>(c.request().ptr);
  auto ptr_dates = static_cast<datetime *>(dates.request().ptr);

  auto last_date_sell_list = py::cast<py::list>(last_date_signal["sell"]);
  for (size_t idx = 0; idx < o.size(); idx++) {
    if(!std::isnan(open_price)) {
      holding_days += (idx != o.size()-1);
      // try to sell
      if(idx == o.size()-1) {
        last_date_sell_list.append(sid);
        break;
      }
      float sell_price = ptr_o[idx+1];
      float tax = 3e-3f * sell_price;
      float fee = 1.425e-3f * 0.6f * (sell_price + open_price);
      float pnl = (sell_price - open_price - tax - fee) / open_price * 100;

      datetime sell_date = ptr_dates[idx+1];


    } else {
      // try to buy
    }
  }

  return available_tid;
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

void show_datetime(std::chrono::system_clock::time_point t) {
  std::time_t time_tt = std::chrono::system_clock::to_time_t(t);
  std::cout << std::ctime(&time_tt) << std::endl;
}

void show_dic_list(py::dict &d) {
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

PYBIND11_MODULE(core, m) {
  m.def("add_two_array", &add_two_array);
  m.def("show_datetime", &show_datetime);
  m.def("show_dic_list", &show_dic_list);
}
