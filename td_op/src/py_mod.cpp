//
// Created by 施奕成 on 2023/3/10.
//
#include "op.h"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(trading_op, m) {
  m.doc() = R"pbdoc(
    Trading Operation
    -----------------------
    .. currentmodule:: trading_op
    .. autosummary::
       :toctree: _generate
       TradingInfo
       PriceData
       Trader
  )pbdoc";

  py::class_<TradingInfo>(m, "TradingInfo")
      .def(
          py::init<const str &, const str &, int, int, const Map<Set<str>> &>(),
          py::arg("strategy_name"), py::arg("trader_code"),
          py::arg("holding_days_th"), py::arg("available_tid"),
          py::arg("selected"));

  py::class_<PriceData>(m, "PriceData")
      .def(py::init<const Vec<str> &, const Vec<str> &, const Map<Vec<float>>,
                    const Map<Vec<float>>, const Map<Vec<float>>>(),
           py::arg("sids"), py::arg("dates"), py::arg("o"), py::arg("c"),
           py::arg("ma20"));

  py::class_<Trader>(m, "Trader")
      .def(py::init<TradingInfo &, const PriceData &, const Map<int> &,
                    Map<Map<str>> &, Map<Vec<str>> &>(),
           py::arg("trading_info"), py::arg("price_data"), py::arg("sid2tid"),
           py::arg("dic_records"), py::arg("last_date_signal"))
      .def("trade_serial", &Trader::trade_serial);
}
