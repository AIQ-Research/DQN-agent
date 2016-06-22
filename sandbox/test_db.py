from fx_trader import FxTrader
from fx_session import EASession
from fx_broker import FxBroker2orders

my_broker = FxBroker2orders('/Users/vicident/Development/hdata/', 'EUR_USD', EASession(), 100000, 10000, 0.3, 0.1)