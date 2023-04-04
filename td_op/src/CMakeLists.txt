file(GLOB CPPS *.cpp)
file(GLOB HEADERS *.h)

list(FILTER CPPS EXCLUDE REGEX ".*/main_old.cpp")
list(FILTER CPPS EXCLUDE REGEX ".*/main_old2.cpp")


add_library(trading_op_static STATIC ${CPPS} ${HEADERS})
target_include_directories(trading_op_static INTERFACE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(trading_op_static PUBLIC ${third_party})

# It is just a wrapper of add_library
pybind11_add_module(trading_op MODULE ${CPPS} ${HEADERS})
target_link_libraries(trading_op PRIVATE ${third_party})
