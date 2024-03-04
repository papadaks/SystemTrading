"""
Trailing Stoploss
Author: TraderPy

Youtube: https://www.youtube.com/channel/UC9xYCyyR_G3LIuJ_LlTiEVQ/featured

Website: https://traderpy.com/

Disclaimer
Trading the financial markets imposes a risk of financial loss. TraderPy is not responsible for any financial losses
that viewers suffer. Content is educational only and does not serve as financial advice. Information or material is
provided ‘as is’ without any warranty.

Past trading results do not indicate future performance. Strategies that worked in the past may not reflect the same
results in the future.
"""

# import libraries
import MetaTrader5 as mt5
import time
import sys

# connect Python to MetaTrader5
mt5.initialize()

# CONFIGS
TICKET = 165856631
MAX_DIST_SL = 0.0006  # Max distance between current price and SL, otherwise SL will update
TRAIL_AMOUNT = 0.0003  # Amount by how much SL updates
DEFAULT_SL = 0.0003  # If position has no SL, set a default SL


# function to trail SL
def trail_sl():
    # get position based on ticket_id
    position = mt5.positions_get(ticket=TICKET)

    # check if position exists
    if position:
        position = position[0]
    else:
        print('Position does not exist')
        sys.exit()

    # get position data
    order_type = position.type
    price_current = position.price_current
    price_open = position.price_open
    sl = position.sl

    dist_from_sl = abs(round(price_current - sl, 6))

    if dist_from_sl > MAX_DIST_SL:
        # calculating new sl
        if sl != 0.0:
            if order_type == 0:  # 0 stands for BUY
                new_sl = sl + TRAIL_AMOUNT

            elif order_type == 1:  # 1 stands for SELL
                new_sl = sl - TRAIL_AMOUNT

        else:
            # setting default SL if the is no SL on the symbol
            new_sl = price_open - DEFAULT_SL if order_type == 0 else price_open + DEFAULT_SL

        request = {
            'action': mt5.TRADE_ACTION_SLTP,
            'position': position.ticket,
            'sl': new_sl,
        }

        result = mt5.order_send(request)
        print(result)
        return result


if __name__ == '__main__':
    print('Starting Trailing Stoploss..')
    print(f'Position: {str(TICKET)}')

    # strategy loop
    while True:
        result = trail_sl()
        # wait 1 second
        time.sleep(1)



