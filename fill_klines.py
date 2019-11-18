import requests, json
from operator import itemgetter
from datetime import datetime
from pandas   import DataFrame
from time     import time, sleep, gmtime

from mongo_settings import mongo_coll_cursor
import network_fxns
from pandas_settings import set_options_pd
set_options_pd(precision = 9)

print('fill_klines', __name__)
#from update_activity import check_activity

def make_kline_df(s_d, interval):
    sec_per_min  = 60
    msec_per_sec = 1000

    limit_min    = 1000
    limit_ms     = limit_min * sec_per_min * msec_per_sec

    dt_now  = (int(datetime.utcnow().timestamp()) * 1000) - (int(datetime.utcnow().timestamp()) % 60 * 1000)
    columns = ['dt', 'open', 'high', 'low', 'close', 'vol_base', 'close_dt', 'vol_quote', 'trades', 'taker_base', 'taker_quote', 'ignore']
    kline_list = []
    loop_ct = 0
    latest_kline_time = 0
    while True:
        if latest_kline_time == 0: dt_f = dt_now - (limit_ms * loop_ct)
        else                     : dt_f = latest_kline_time
        PARAMS = {'symbol': s_d['symbol'].upper(), 'interval': interval, 'endTime': dt_f, 'limit': 2000}
        
        try                                            : api_response = requests.get('https://api.binance.com/api/v1/klines', params = PARAMS).json()
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError, json.decoder.JSONDecodeError) as e: print('no internec connection', '\n', e, '\n'); return []

        if len(api_response) == 0: break
        for line in api_response: kline_list.append(line)
        
        if latest_kline_time == int(api_response[0][0]): break
        else:latest_kline_time = int(api_response[0][0])
        
        loop_ct = loop_ct + 1
        print('\rloop #{0}  interval: {1}   kline ct = {2}   actual list len = {3}\r'.format(loop_ct, interval, loop_ct * limit_min, len(kline_list)), end = '')

    kline_list = sorted(kline_list, key = itemgetter(0))
    s_df  = DataFrame(kline_list, columns = columns).astype(float)
    s_df  = s_df.drop_duplicates('dt', keep = 'first').sort_values(by = 'dt')
    s_df.drop(['ignore', 'taker_base', 'close_dt', 'vol_base'], axis = 1, inplace = True)

    '''# show the lengths of the df groups
    group__df = s_df.copy()
    group__df.reset_index(inplace = True)
    group__df['time_consistency_check'] = (group__df['dt'] - group__df['dt'].shift(1)).abs() != 60000
    group__df['check'] = group__df['time_consistency_check'].cumsum()
    separated_df = group__df.groupby(['check'])
    df_list = [coin__df_section[1] for coin__df_section in separated_df]
    for i in df_list: print(i.shape)'''

    return s_df

def save_klines_to_db(s_d, k_df, interval):

    # df to dict list
    k_dl = k_df.to_dict('records')
    collection_name = '{0}_{1}'.format(s_d['symbol'], interval)
    cursor = mongo_coll_cursor(collection_name)

    cursor.insert_many(k_dl, ordered = False)
    new_list = list(cursor.find({}))
    print(DataFrame(new_list).shape)

def get_latest_kline(_c_):
    ts = time()
    clist = list(_c_.find({}, {'_id':0, 'dt':1}))
    print('load col {0:.4f}s'.format(time() - ts))
    ts2 = time()
    latest_dt = DataFrame(clist)['dt'].max()
    print('make df {0:.4f}s'.format(time() - ts2))

    latest_kline = list(_c_.find({'dt': int(latest_dt)}, {'_id': 0}))[0]
    return latest_kline

def update_klines_to_db(s_d, s_df, interval):
    # turn dictionary to list
    s_l = s_df.to_dict('records')

    # get cursor
    collection_name = '{0}_{1}'.format(s_d['symbol'], interval)
    cursor = mongo_coll_cursor(collection_name)

    # update every value based on datetime
    for i in s_l:
        cursor.update_one({'dt': i['dt']}, {'$set': i}, upsert = True)
        


    return

def fill_kline_gap(s_d, interval, minute_diff, latest_dt):
    sec_per_min  = 60
    msec_per_sec = 1000

    limit_min    = 1000
    limit_ms     = limit_min * sec_per_min * msec_per_sec

    dt_now  = (int(datetime.utcnow().timestamp()) * 1000) - (int(datetime.utcnow().timestamp()) % 60 * 1000)
    columns = ['dt', 'open', 'high', 'low', 'close', 'vol_base', 'close_dt', 'vol_quote', 'trades', 'taker_base', 'taker_quote', 'ignore']
    kline_list = []
    loop_ct = 0
    latest_kline_time = 0
    newest_kline_time = 0
    
    while True:
        dt_i = latest_dt
        if minute_diff > limit_min:
            dt_i = newest_kline_time
            
            limit = 1000
        else: limit = minute_diff
        PARAMS = {'symbol': s_d['symbol'].upper(), 'interval': interval, 'startTime': int(dt_i), 'limit': int(limit)}

        try : api_response = requests.get('https://api.binance.com/api/v1/klines', params = PARAMS).json()
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError, json.decoder.JSONDecodeError) as e: print('no internec connection', '\n', e, '\n'); return []

        if len(api_response) == 0: break
        for line in api_response: kline_list.append(line)
        
        if newest_kline_time == 0: newest_kline_time = int(api_response[-1][0])
        elif newest_kline_time == int(api_response[-1][0]): break
        else:newest_kline_time = int(api_response[-1][0])

        loop_ct = loop_ct + 1
        print('\rloop #{0}  interval: {1}   kline ct = {2}   actual list len = {3}\r'.format(loop_ct, interval, loop_ct * limit_min, len(kline_list)), end = '')
        if minute_diff <= 1000: break

    kline_list = sorted(kline_list, key = itemgetter(0))
    s_df  = DataFrame(kline_list, columns = columns).astype(float)
    s_df  = s_df.drop_duplicates('dt', keep = 'first').sort_values(by = 'dt')
    s_df.drop(['ignore', 'taker_base', 'close_dt', 'vol_base'], axis = 1, inplace = True)

    s_df['dt'] = s_df['dt'].astype(int)
    s_df['trades'] = s_df['trades'].astype(int)

    update_klines_to_db(s_d, s_df, interval)

def get_kline_history(s_d, interval):
    collection_name = '{0}_{1}'.format(s_d['symbol'], interval)
    cursor = mongo_coll_cursor(collection_name)
    coll_ct = int(cursor.count())

    if   coll_ct == 1999: pass
    elif coll_ct > 1:
        print('checking column')
        
        # check if collection is updated to the current minute
        latest_kline = get_latest_kline(cursor)
        latest_dt = latest_kline['dt']
        now_dt = (int(time()) * 1000) - (int(time()) % 60 * 1000)
        minute_diff = (now_dt - latest_dt) / 60000
        if minute_diff > 1:
            print('minute difference is {0}, filling in gap'.format(minute_diff))
            fill_kline_gap(s_d, interval, minute_diff, latest_dt)

    else:
        # fill in the history for the trading pair (at interval)
        kline_df = make_kline_df(s_d, interval)
        kline_df['dt'] = kline_df['dt'].astype(int)
        kline_df['trades'] = kline_df['trades'].astype(int)
        save_klines_to_db(s_d, kline_df, interval)


def run_fill_klines():
    # 1 check for klines
    # 1a get all coin status
    cursor = mongo_coll_cursor('all_symbols_status')
    list_of_active_symbols = list(cursor.find({'activity_status': 1}, {'_id': 0, 'dt_status': 0, 'baseAssetPrecision': 0, 'filters': 0, 'orderTypes':0,'isSpotTradingAllowed':0, 'isMarginTradingAllowed':0, 'icebergAllowed':0,'quotePrecision':0,'baseAsset':0}))
    
    # 1 thru 8
    xxx = 0
    list_of_active_symbols = list_of_active_symbols[: : -1]

    interval_list = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
    for ct_symbol, symbol_dict in enumerate(list_of_active_symbols):

        # make list of klines for each symbol
        
        print('\n\n\n{0:3.0f}/{1:3.0f} {2:8}'.format(ct_symbol, len(list_of_active_symbols), symbol_dict['symbol'].lower()))
        for ct_int, interval in enumerate(interval_list[: : -1]):
            #if 'BTCPAX' not in symbol_dict['symbol'] or '1m' not in interval: continue
            print('\n\n{0}_{1}    {2}/{3}\n'.format(symbol_dict['symbol'], interval, ct_int, len(interval_list)))
            get_kline_history(symbol_dict, interval)


# run script
if __name__ == "__main__":
    while True:
        looptime = time()
        run_fill_klines()
        print('fill_klines.py     dt now: {0}     loop time: {2:.4f} s'.format(datetime.now(), time() - looptime))
        sleep(1)