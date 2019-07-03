import requests, json
from datetime import datetime
from pandas   import DataFrame
from time     import time, sleep

from utility_get_mongo_db_trade import login_mongo
import utility_check_port_trade
from pandas_settings import set_options_pd
set_options_pd(9)

def get_trade_params():
    cursor = login_mongo('trade')['trade_params']
    trade_params = list(cursor.find({"status": 'active'}, {'_id': 0, 'dt_record': 0, 'status': 0}))
    if len(trade_params) > 1: print('help'); print(trade_params); print(type(trade_params), len(trade_params)); exit()
    else: return trade_params[0]

def get_all_symbols():
    try: api_response_prices = requests.get('https://api.binance.com/api/v1/exchangeInfo').json()
    except (requests.exceptions.ConnectionError, requests.exceptions.SSLError): print('get_coin_list request failed, attempt {0}'.format(0)); exit()
    return api_response_prices['symbols']

def get_quote_symbol_info(sym_list):
    quote_asset_list = DataFrame(sym_list)['quoteAsset'].unique()
    quote_usdt_list = ['{}USDT'.format(quote_asset) for quote_asset in quote_asset_list if 'USDT' not in quote_asset]
    try: api_response = requests.get('https://api.binance.com/api/v3/ticker/price').json()
    except (requests.exceptions.ConnectionError, requests.exceptions.SSLError, requests.exceptions.ChunkedEncodingError, json.decoder.JSONDecodeError) as e: print('no internec connection', '\n', e, '\n'); return []
    price_df = DataFrame(api_response)
    list_of_quote_info = price_df[price_df['symbol'].isin(quote_usdt_list)].to_dict('records')
    quote_info_dict = {}
    for quote_info in list_of_quote_info:
        quote_info_dict[quote_info['symbol']] = {'price': quote_info['price']}

    return quote_info_dict

def pull_klines_to_list(p, lst):
    try: api_response = requests.get('https://api.binance.com/api/v1/klines', params = p).json()
    except (requests.exceptions.ConnectionError, requests.exceptions.SSLError, requests.exceptions.ChunkedEncodingError, json.decoder.JSONDecodeError) as e: print('no internec connection', '\n', e, '\n'); return []
    for line in api_response: lst.append(line)
    return lst

def kline_list_to_df(k_lst, clms):
    try                   : k_df = DataFrame(k_lst, columns = clms).astype(float)
    except ValueError as e: print('this is a weird valueerror\n', k_df,'\n', e); exit()
    k_df = k_df.drop_duplicates('dt', keep = 'first').sort_values(by = 'dt')

    return k_df

def mark_activity(s_d, activity_bool):
    # enter into database col that its active 
    cursor = login_mongo('trade')['all_symbols_status']
    s_d['activity_status'] = int(activity_bool)
    s_d['dt_status'] = int(time())
    cursor.update_one({'symbol': s_d['symbol']}, {'$set': s_d}, upsert = True)

def check_activity(t_p, s_d, clms):
    list_to_df = []
    activity_window = 60
    dt_now = (int(datetime.utcnow().timestamp()) * 1000) - (int(datetime.utcnow().timestamp()) % 60 * 1000)
    PARAMS = {'symbol': s_d['symbol'].upper(), 'interval': '1m', 'endTime': dt_now, 'limit': activity_window}
    m_l = pull_klines_to_list(PARAMS, list_to_df)
    s_df = kline_list_to_df(m_l, clms)
    s_df['vol_USDT'  ] = s_df['vol_quote'  ] * s_d['quotePriceUSDT']
    s_df['taker_USDT'] = s_df['taker_quote'] * s_d['quotePriceUSDT']
    
    trades_avg = s_df['trades'    ].mean()
    vol_avg    = s_df['vol_USDT'  ].mean()
    taker_avg  = s_df['taker_USDT'].mean()

    trade_bool    = trades_avg >= t_p['min_trades'  ]
    volume_bool   = vol_avg    >= t_p['min_vol_usdt']
    activity_bool = trade_bool & volume_bool

    print('{:9}: trades: {:6.0f}      vol_usdt: {:11.4f}      taker_usdt: {:8.4f}'.format(s_d['symbol'], trades_avg, vol_avg, taker_avg), trade_bool, volume_bool)
    mark_activity(s_d, activity_bool)

    if   trade_bool  == False: print('low trade avg: {0:.3f} < {1} (thresh)'.format(trades_avg, t_p['min_trades'  ])); return activity_bool
    elif volume_bool == False: print('low vol avg  : {0:.3f} < {1} (thresh)'.format(vol_avg   , t_p['min_vol_usdt'])); return activity_bool
    else: return activity_bool

def run_update_activity():
    runtime = time()
    while True:
        programtime = time()

        # get parameters
        trade_params = get_trade_params()

        # get list of all symbols
        list_of_symbols = get_all_symbols()
        if len(list_of_symbols) == 0: msg = 'api response is empty'; exit()
        else:
            
            # get quote pair prices
            quote_info_dict = get_quote_symbol_info(list_of_symbols)

            # go thru each pair and check if they fit the liquidity requirements
            count = 0
            am_list = []

            for symbol_dict in list_of_symbols:
                banned_symbols = []
                if symbol_dict['symbol'] in banned_symbols: continue
                elif symbol_dict['status'].upper() == 'BREAK': continue

                looptime = time()
                count += 1
                
                # get the est usd value for volume
                convert_symbol = '{0}USDT'.format(symbol_dict['quoteAsset'])
                if symbol_dict['quoteAsset'] == "USDT": symbol_dict['quotePriceUSDT'] = 1
                else: symbol_dict['quotePriceUSDT'] = float(quote_info_dict[convert_symbol]['price'])

                # check and mark activity
                columns = ['dt', 'open', 'high', 'low', 'close', 'vol_base', 'close_dt', 'vol_quote', 'trades', 'taker_base', 'taker_quote', 'ignore']
                check_activity(trade_params, symbol_dict, columns) == False
            
        # print stats
        
        
        cursor = login_mongo('trade')['all_symbols_status']
        l = list(cursor.find({}, {'_id': 0, 'dt_status':0}))
        df = DataFrame(l)
        active_sum = int(df['activity_status'].sum())
        active_total = int(df.shape[0])
        print('update_activity.py - dt: {0} ||      {1}/{2} active symbols     loop time: {3:.4f} s'.format(datetime.now(), active_sum, active_total, time() - programtime))
        sleep(30 * 60)

# start
if __name__ == "__main__":
    run_update_activity()