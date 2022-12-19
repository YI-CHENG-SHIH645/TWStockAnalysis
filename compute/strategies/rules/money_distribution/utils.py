import pandas as pd
import matplotlib.pyplot as plt
import zigzag
import operator
from data.database.interface import execute_sql, res_to_df


def get_history_record(strategy_name: str):
    return res_to_df(*execute_sql('get_history_record', (strategy_name, )))


def plot_return(daily_ret, name):
    pivots = zigzag.peak_valley_pivots(daily_ret.values, 0.03, -0.03)
    daily_ret = daily_ret[pivots != 0]
    daily_ret.index = pd.to_datetime(daily_ret.index)
    plt.figure(figsize=(2, 1.5))
    (daily_ret - 1).clip(lower=0).plot.area(color='#FFBA12')

    plt.axis('off')
    plt.savefig("strategies/{}.png".format(name),
                format='png', transparent=True, dpi=300, pad_inches=0, bbox_inches='tight')


def cal_summary(strategy_name: str,
                portfolio_value: dict,
                init_balance: float,
                holding: dict,
                money: float,
                args):
    profit = list(portfolio_value.values())

    max_profit = list(max(portfolio_value.items(), key=operator.itemgetter(1)))
    max_profit[1] = round((max_profit[1] - init_balance) / init_balance * 100, 2)
    max_profit = {"date": max_profit[0], "profit": max_profit[1]}

    min_profit = list(min(portfolio_value.items(), key=operator.itemgetter(1)))
    min_profit[1] = round((min_profit[1] - init_balance) / init_balance * 100, 2)
    min_profit = {"date": min_profit[0], "profit": min_profit[1]}

    years = len(portfolio_value) / 252

    def cal_profit(day):
        return round((profit[-1] - profit[-day - 1]) / profit[-day - 1] * 100, 2)

    summary = {
        "strategy_name": strategy_name,
        "annual_return": round(((cal_profit(-1) / 100 + 1) ** (1 / years) - 1) * 100, 2),
        "season": cal_profit(63),
        "month": cal_profit(21),
        "week": cal_profit(5),
        "day": cal_profit(1),
        "total": {"profit": cal_profit(-1), "year": round(years, 2)},
        "max": max_profit,
        "min": min_profit,
        "holding": len(holding),
        "money": round(money, 2),
        "daily_return": {k: round(v / init_balance, 2) for k, v in portfolio_value.items()}
    }

    ret_series = pd.Series(summary['daily_return'])
    summary.update({"mdd": -round(((ret_series.cummax() - ret_series) / ret_series.cummax()).max() * 100, 2)})
    if not args.profiling_name:
        plot_return(ret_series, strategy_name)

    return summary
