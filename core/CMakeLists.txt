cmake_minimum_required(VERSION 3.18)
project(core)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ../../compute/strategies/cpp_acc)

add_subdirectory(extern/pybind11)
#add_subdirectory(extern/pybind11/tests)
include_directories(extern/pybind11/include)

pybind11_add_module(core main.cpp)
