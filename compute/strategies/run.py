from strategies.core import strategy
from strategies.rules.logic import *
from strategies.rules.money_distribution import EvenDistribution


def main(args):
    summary = {"latest_signal": [], "strategies_summary": [], "trading_record": []}

    for item in [
        # @@@@@@@@@@@@@@@@@@@@@@@@
        # register trading logic
        # @@@@@@@@@@@@@@@@@@@@@@@@
        strategy(ITFollowLogic, args),
        strategy(PEPBLogic, args),
        strategy(NewFactor, args),
    ]:
        summary["latest_signal"].append(item)

    args.c = ITFollowLogic.c
    args.adj_ratio = ITFollowLogic.adj_ratio
    args.adj_c = args.c * args.adj_ratio
    # money distribution logic
    for item in [
        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        # register money distribution logic
        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        EvenDistribution(args, ITFollowLogic.strategy_name, init_balance=1e3).cal(),
        EvenDistribution(args, PEPBLogic.strategy_name, init_balance=1e3).cal(),
        EvenDistribution(args, NewFactor.strategy_name, init_balance=1e3).cal(),
    ]:
        summary["strategies_summary"].append(item[0])
        summary["trading_record"].append(item[1])

    if not args.profiling_name:
        import json
        f = open('strategies/info.json', 'w', encoding='utf-8')
        json.dump(summary, f, indent=4)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiling_name", type=str, default="")
    parser.add_argument("--new_start", action="store_true")
    parser.add_argument("--cpp", action="store_true")
    args_ = parser.parse_args()
    if args_.profiling_name:
        import os
        import cProfile
        os.makedirs("profiling", exist_ok=True)
        cProfile.run("main(args_)", os.path.join("profiling", args_.profiling_name))
    else:
        main(args_)
