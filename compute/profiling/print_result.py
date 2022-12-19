if __name__ == '__main__':
    import argparse
    import pstats
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiling_name", type=str, required=True)
    parser.add_argument("--sortby", type=str, default="cumtime")
    parser.add_argument("--topk", type=int, default=20)
    args = parser.parse_args()
    p = pstats.Stats(args.profiling_name)
    p.sort_stats(args.sortby).print_stats(args.topk)
