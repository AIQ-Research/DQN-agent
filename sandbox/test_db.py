from fx_trader import FxTrader
from fx_session import EASession

my_env = FxTrader("/Users/vicident/Development/hdata/fxpairs2014.db",
                  "EUR_USD",
                  EASession(),  # European + American sessions
                  1440,         # 24 hours of window frame
                  0.0004,       # pips of brokerage fees + slippage
                  100000        # contract in base currency
                  )

for i in xrange(2880):
    frame, cp, cv, sess = my_env.get_frame()
    if sess:
        my_env.print_time_pointer()
