add_library(trade main.cpp trade.cpp trade.h)
target_link_libraries(trade PUBLIC OpenMP::OpenMP_CXX pybind11::pybind11)
