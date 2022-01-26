import backtrader as bt
import backtrader.feeds as btfeeds
import pandas as pd
import numpy as np


def createRandomDataFeed(n_samples, corr, mu=0, annual_sigma=.15, start_value=1000):
    """

    :param n_samples: number of sample length
    :param corr: autocorrelation coefficent should be between 0 and 1
    :param mu: mean of the distribution
    :param annual_sigma: std dev of distribution
    :return: pd.DF col['close']
    """
    assert 0 < corr < 1, "Auto-correlation must be between 0 and 1"

    # Find out the offset `c` and the std of the white noise `sigma_e`
    # that produce a signal with the desired mean and variance.
    # See https://en.wikipedia.org/wiki/Autoregressive_model
    # under section "Example: An AR(1) process".

    sigma = annual_sigma / np.sqrt(365)

    c = mu * (1 - corr)
    sigma_e = np.sqrt((sigma ** 2) * (1 - corr ** 2))

    # Sample the auto-regressive process.
    signal = [c + np.random.normal(0, sigma_e)]
    for _ in range(1, n_samples):
        signal.append(c + corr * signal[-1] + np.random.normal(0, sigma_e))

    # create the price index
    rets = signal
    price = [start_value]
    for i in np.arange(len(rets)):
        price.append(price[-1] * rets[i] + price[-1])

    # create the data frame
    price = pd.DataFrame(price)
    price.columns = ['close']
    # price['open'] = price['close']
    # price['high'] = price['close']
    # price['low'] = price['close']
    # price['volume'] = 0
    # price['openinterest'] = 0
    start_date = pd.to_datetime('01-01-1990')
    price.index = pd.date_range(start=start_date, end=start_date + pd.DateOffset(days=len(signal)))
    price['datetime'] = price.index
    return price


class myClose(btfeeds.DataBase):
    params = (('datetime', None), ('close', 0))


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000000)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    df = createRandomDataFeed(n_samples=10000,
                              corr=0.0000000001,
                              mu=0,
                              annual_sigma=.15,
                              start_value=1000)

    data = myClose(dataname=df,
                   volume=False, openinterest=False,
                   fromdate=df.index[0],
                   todate=df.index[-1]
                   )

    cerebro.adddata(data)

    # Plot the result
    cerebro.run()
    cerebro.plot()