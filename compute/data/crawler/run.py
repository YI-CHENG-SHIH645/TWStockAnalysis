from data.crawler.crawler_framework import crawler

target = ["價量資訊",
          "法人買賣",
          "外資持股比",
          "本益比殖利率股價淨值比",
          "資產負債表",
          "綜合損益表",
          "除權息結果",
          "大盤指數"
          ]

if __name__ == '__main__':
    for tgt in target:
        crawler(tgt)
