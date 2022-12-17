if __name__ == '__main__':
    from strategies.core import strategy
    from strategies.rules.logic import *
    from strategies.rules.money_distribution import EvenDistribution

    summary = {"latest_signal": [], "strategies_summary": [], "trading_record": []}

    for item in [
        # @@@@@@@@@@@@@@@@@@@@@@@@
        # register trading logic
        # @@@@@@@@@@@@@@@@@@@@@@@@
        strategy(ITFollowLogic),
        strategy(PEPBLogic),
        strategy(NewFactor),
    ]:
        summary["latest_signal"].append(item)

    # money distribution logic
    for item in [
        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        # register money distribution logic
        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        EvenDistribution(ITFollowLogic.strategy_name, init_balance=1e3).cal(),
        EvenDistribution(PEPBLogic.strategy_name, init_balance=1e3).cal(),
        EvenDistribution(NewFactor.strategy_name, init_balance=1e3).cal(),
    ]:
        summary["strategies_summary"].append(item[0])
        summary["trading_record"].append(item[1])

    import json
    f = open('strategies/info.json', 'w', encoding='utf-8')
    json.dump(summary, f, indent=4)
