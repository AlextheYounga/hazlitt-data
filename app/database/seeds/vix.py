from app.lab.vix.vix import Vix
from app.lab.news.newsfeed import NewsFeed

vix = Vix(saveResults=True)
nf = NewsFeed()
stocks = nf.mentionedStocks()

for stock in stocks:
    print(stock.ticker)
    vix.equation(stock.ticker)
