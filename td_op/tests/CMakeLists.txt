enable_testing()

add_executable(tests tests.cpp)

target_link_libraries(
  tests
  GTest::gtest_main
  trading_op_static
)

gtest_discover_tests(tests)
