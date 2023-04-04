#include <op.h>
#include <gtest/gtest.h>
using namespace std;

TEST(OPTest, trade_serial) {
  Map<Set<str>> selected;
  selected["a"] = {"one", "two", "three", "five", "eight"};
  auto info = TradingInfo("ITFollow",
                          "001",
                          30,
                          303244,
                          selected);
  Map<Vec<float>> o;
  o["a"] = {1, 2, 3};
  Map<Vec<float>> c;
  c["b"] = {4, 5, 6};
  Map<Vec<float>> ma20;
  ma20["c"] = {7, 8, 9};
  auto prices = PriceData({"1", "2", "3"}, {"4", "5", "6"}, o, c, ma20);

  const Map<int> sid2tid;
  Map<Map<str>> dic_records;
  Map<Vec<str>> last_date_signal;
  auto trader = Trader(info, prices, sid2tid, dic_records, last_date_signal);
  trader.trade_serial();
}
