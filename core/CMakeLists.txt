cmake_minimum_required(VERSION 3.18)
project(core)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ../../compute/strategies/cpp_acc)

if(APPLE)
    LINK_DIRECTORIES("/opt/homebrew/opt/libomp/lib")
    include_directories("/opt/homebrew/opt/libomp/include")
else()
    find_package(OpenMP REQUIRED)
endif()


add_subdirectory(extern/pybind11)
#add_subdirectory(extern/pybind11/tests)
include_directories(extern/pybind11/include)

pybind11_add_module(core main.cpp)
if (NOT APPLE)
    target_link_libraries(core PUBLIC OpenMP::OpenMP_CXX)
endif ()
