
import backtester as bt
import traceback
import os
import pandas as pd
import numpy as np

import MyAppsSite.settings as settings

prohibited_words = ["exec(", "import ", "eval(", "compile(", "os.", "io."]

def evaluate(text, selected_shares):
    text += """
global trader
trader = MyTrader("User")
    """
    market = bt.Market()
    working_path = os.path.join(settings.MEDIA_ROOT, settings.TEMP_DATA_DIR)
    market.load_history_data(working_path, selected_shares)

    try:
        for word in prohibited_words:
            if text.find(word) != -1:
                raise Exception("Prohibited statement found")

        exec(text)
        try:
            market.set_trader(trader)
        except Exception as e:
            return False, "No MyTrader class"
    except Exception as e:
        return False, traceback.format_exc(limit=0)

    trader.set_market(market)
    market.run_full_test()
    return True,  trader.get_performance()




