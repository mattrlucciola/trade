def apply_features(_df_):
    from ....params.general_params import general_params
    from ....params.feature_params import feature_params
    fb_trgt = _df_.pop('fb_trgt')
    dt      = _df_.pop('dt')

    _df_['pc_h'] =  _df_['high'].pct_change()
    _df_['hl']   = (_df_['high'] - _df_['low']) / _df_['low']
    for col in ['high', 'vol_quote', 'hl', 'pc_h']:
        if 'pc'   in feature_params["basic_fxns"] and ('vol' not in col) and ('pc' not in col) and (_df_[col].min() != 0):
            for time_ in feature_params["window_list"]: _df_[f"{col}__pc_{time_}"] = _df_[col].pct_change(time_)
        if 'mean' in feature_params["basic_fxns"]:
            for time_ in feature_params["window_list"]: _df_[f"{col}__mean_{time_}"] = _df_[col].rolling(time_).mean()
        if 'med'  in feature_params["basic_fxns"]:
            for time_ in feature_params["window_list"]: _df_[f"{col}__med_{time_}"] = _df_[col].rolling(time_).median()
        if 'mad'  in feature_params["basic_fxns"]:
            for time_ in feature_params["window_list"]: _df_[f"{col}__mad_{time_}"] = ((_df_[col].rolling(time_).median() - _df_[col]).abs())#.median()
        if 'skew' in feature_params["basic_fxns"]:
            for time_ in [i for i in feature_params["window_list"] if i > 10]: _df_[f"{col}__skew_{time_}"] = _df_[col].rolling(time_).skew()
        if 'kurt' in feature_params["basic_fxns"]:
            for time_ in [i for i in feature_params["window_list"] if i > 10]: _df_[f"{col}__kurt_{time_}"] = _df_[col].rolling(time_).kurt()
        if 'mm'   in feature_params["basic_fxns"] and ('pc_h' not in col) and (_df_[col].min() != 0):
            for time_ in feature_params["window_list"]: _df_[f"{col}__mm_{time_}"] = (_df_[col].rolling(time_).max() - _df_[col].rolling(time_).min()) / _df_[col].rolling(time_).min()

    _df_['fb_trgt'] = fb_trgt
    _df_ = _df_.iloc[max(feature_params["window_list"]) * 3 - 1: -general_params['future']]
    return _df_