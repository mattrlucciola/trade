#identify all markets offered by the platform

#create/update historical market data (for all time intervals):
    #metrics:
        #[book activity if available, price (h/l), volume, taker, trade_ct
        #btc/usd, btc/eur, btc/yen, btc/yuan, btc/korea, btc/gbp]

# import mongo fxn
from mongo_settings import mongo_coll_cursor

# pulls all markets available on the platform (platform is set within params)
def get_all_markets(params):
    if params['platform'] == 'coinbase':
        list_of_markets = []
    return list_of_markets

#update current price & order book activity (async/websocket)
    #incorporate above function (create/update historical market data)

#decide which markets are available
### future updates to this set of functions, make a fxn to evaluate 1 market at 1 interval, allows me to set list of mkts or intvl list priority


def update_db_liq(mkt__liq, params):
    db_coll = mongo_coll_cursor('liquidity_all_markets')
    db_coll.update_one({'_id': mkt__liq['symbol']}, update = {'$set': mkt__liq}, upsert = True)

def add_to_db_archive(mkt__liq__list, params):
    from time import time
    db_coll = mongo_coll_cursor('liquidity_all_markets_archive')
    db_coll.insert_many([{'_id': int(time()), 'markets': mkt__liq__list}])

def eval_markets(list_of_mkts, params):
    from pandas import DataFrame
    list_of_mkts_liq = []
    for interval in params['all_intervals']:
        for mkt_info in list_of_mkts:
            mkt_liq = {'symbol': mkt_info['symbol']}
            # get history lists
            history_volume   = mkt_info['volume_history'  ].iloc[-params['liquidity_minutes']: ]
            history_trade_ct = mkt_info['trade_ct_history'].iloc[-params['liquidity_minutes']: ]

            # check volume history viablility
            mkt_liq['volume_avg']          = float(history_volume.mean())
            mkt_liq['volume_std']          = float(history_volume.std())
            mkt_liq['volume_below_min_ct'] = int(history_volume[history_volume['volume'] < params['liquidity_volume_min_{0}'.format(interval)]].shape[0])
            mkt_liq['vol_avg'] = mkt_liq['volume_avg']          > params['liquidity_volume_avg_threshold']
            mkt_liq['vol_bmc'] = mkt_liq['volume_below_min_ct'] > params['liquidity_volume_bmc_threshold']

            # check trade_ct history viablility
            mkt_liq['trade_ct_avg']             = float(history_trade_ct.mean())
            mkt_liq['trade_ct_std']             = float(history_trade_ct.std())
            mkt_liq['trade_ct_below_min_ct']    = int(history_trade_ct[history_trade_ct['trade_ct'] < params['liquidity_trade_ct_min_{0}'.format(interval)]].shape[0])
            mkt_liq['tc_avg'] = mkt_liq['trade_ct_avg']             > params['liquidity_trade_ct_avg_threshold']
            mkt_liq['tc_bmc'] = mkt_liq['trade_ct_below_min_ct']    > params['liquidity_trade_ct_bmc_threshold']

            list_of_mkts_liq.append(mkt_liq)

            update_db_liq(mkt_liq, params)
        
    add_to_db_archive(list_of_mkts_liq, params)


# main
def main(params):
    list_of_markets = get_all_markets(params)
    eval_markets(list_of_markets, params)

params = {
    'platform': 'coinbase'
}
main(params)