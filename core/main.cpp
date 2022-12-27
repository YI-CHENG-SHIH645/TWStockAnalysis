#include <iostream>
#include <pybind11/pybind11.h>

void print_hi() {
  std::cout << "HI\n";
}

PYBIND11_MODULE(core, m) {
  m.def("print_hi", &print_hi);
}
