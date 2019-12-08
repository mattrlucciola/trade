def load_dataset():
    # this makes a dataset with a datetime index (UTC) and removes all values before the most recent time-gap
    # tldr: finds the latest "complete" and "consistent" dataset
    from pandas import read_csv, concat, to_datetime
    from os import getcwd

    from ....params.general_params import general_params

    coin_file    = '{0}/model_coins/year/{1}.csv'.format(getcwd(), general_params['coin_pair'])
    pre_coin__df = read_csv(coin_file).astype(float).set_index(['dt'], drop = True)

    # add the price of bitcoin (in USDT) to the current dataset, if its in the stat_list
    if 'btc_price' in [feature for feature in general_params['stat_list']]: 
        btc_price_file = '{0}/model_coins/year/BTCUSDT.csv'.format(getcwd())
        btc_price_df   = read_csv(btc_price_file).astype(float).set_index(['dt'], drop = True)
        pre_coin__df   = pre_coin__df[[feature for feature in general_params['stat_list'] if 'btc_price' != feature]]
        btc_price_df['btc_price'] = btc_price_df['high']
        pre_coin__df = concat([pre_coin__df, btc_price_df['btc_price']], axis = 1)
    else: pre_coin__df = pre_coin__df[[feature for feature in general_params['stat_list']]]

    # time consistency check
    pre_coin__df.reset_index(inplace = True)
    pre_coin__df['time_consistency_check'] = (pre_coin__df['dt'] - pre_coin__df['dt'].shift(1)).abs() != 60000
    pre_coin__df['check'] = pre_coin__df['time_consistency_check'].cumsum()
    separated_df = pre_coin__df.groupby(['check'])
    df_list = [coin__df_section[1] for coin__df_section in separated_df]
    
    # pull the most recent coin_df
    coin_df = df_list[-2]
    coin_df.drop(['time_consistency_check', 'check'], axis = 1, inplace = True)

    # convert index to datetime
    if 1 == 0:
        coin_df['dt'] = to_datetime(coin_df['dt'] / 1000, unit = 's')
        coin_df.set_index(['dt'], drop = True, inplace = True)

    # create y values
    coin_df['f__max'] = coin_df['high'].rolling(general_params['future']).max().shift(-general_params['future'])
    coin_df['f__min'] = coin_df['high'].rolling(general_params['future']).min().shift(-general_params['future'])

    # calc boolean y-values: 'fb' = future boolean
    coin_df['fb_trgt'] = (coin_df['f__max'] >= (coin_df['high'] * (1 + max(general_params['pct_list'])))) & (coin_df['f__min'] >= (coin_df['high'] * (1 + min(general_params['pct_list']))))

    # delete future value columns (f__max, f__min, etc...) from dataset
    coin_df.drop([drop for drop in coin_df.columns if ('__' in drop)], axis = 1, inplace = True)
    return coin_df