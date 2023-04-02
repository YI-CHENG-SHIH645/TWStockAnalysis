file(GLOB CPPS *.cpp)
file(GLOB HEADERS *.h)

add_library(trading_op ${CPPS} ${HEADERS})
target_link_libraries(trading_op ${third_party})
