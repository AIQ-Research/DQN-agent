__author__ = 'vicident'


class SLTPOrder:
    def __init__(self, open_price, lot, sl, tp):
        self.open_price = open_price
        self.lot = lot
        self.sl = sl
        self.tp = tp

    def _equity(self, spot_price):
        raise NotImplemented

    def _check_sl(self, spot_price):
        raise NotImplemented

    def _check_tp(self, spot_price):
        raise NotImplemented

    def close(self, spot_price):
        return self._equity(spot_price)

    def step(self, spot_price):
        reward = 0
        equity = self._equity(spot_price)
        closed = False
        if self._check_sl(spot_price) or self._check_tp(spot_price):
            reward = equity
            closed = True

        return equity, reward, closed


class BuyOrder(SLTPOrder):
    def __init__(self, open_price, lot, sl, tp, slippage=0.005):
        SLTPOrder.__init__(self, open_price, lot, sl, tp)
        self.slippage = slippage

    def equity(self, spot_price):
        return (spot_price - self.open_price - self.slippage) * self.lot

    def check_sl(self, spot_price):
        return self.open_price - spot_price - self.slippage >= self.sl

    def check_tp(self, spot_price):
        return spot_price - self.open_price - self.slippage >= self.tp


class SellOrder(SLTPOrder):
    def __init__(self, open_price, lot, sl, tp, slippage=0.005):
        SLTPOrder.__init__(self, open_price, lot, sl, tp)
        self.slippage = slippage

    def equity(self, spot_price):
        return (self.open_price - spot_price - self.slippage) * self.lot

    def check_sl(self, spot_price):
        return spot_price - self.open_price - self.slippage >= self.sl

    def check_tp(self, spot_price):
        return self.open_price - spot_price - self.slippage >= self.tp
