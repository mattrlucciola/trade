import numpy as np
def to_categorical(y, class_ct = None, dtype = 'float32'):
    y = np.array(y, dtype = 'int') 
    if (y.shape[-1] == 1) and (len(y.shape) > 1): y.shape = tuple(y.shape[: -1])
    y = y.ravel()
    if class_ct == None: class_ct = np.max(y) + 1
    n = y.shape[0]
    cat_np = np.zeros((n, class_ct), dtype = dtype)
    cat_np[np.arange(n), y] = 1
    cat_np = np.reshape(cat_np, (n, class_ct))
    return cat_np

def split_points_train_test(general_params):

    train_split_i = -1 * (general_params['train_size'] + general_params['test_size'] + general_params['future'])
    train_split_f = train_split_i + general_params['train_size']
    test_split_i  = train_split_f + general_params['future']
    test_split_f  = test_split_i  + general_params['test_size']
    if test_split_f == 0: test_split_f = None

    sptt = {
        "train_split_i": train_split_i,
        "train_split_f": train_split_f,
        "test_split_i": test_split_i,
        "test_split_f": test_split_f,
    }
    return sptt

def split_points_xy():
    return

def split_tt_y(_y_df_, sptt):
    train_y = to_categorical(_y_df_.iloc[sptt['train_split_i']: sptt['train_split_f']].values, 2)
    test_y  = to_categorical(_y_df_.iloc[sptt['test_split_i' ]: sptt['test_split_f' ]].values, 2)
    return train_y, test_y

def split_tt_x(_x_df_, sptt, general_params):
    from sklearn.preprocessing import MinMaxScaler
    train_x_dict = {}
    test_x_dict  = {}

    for feature in _x_df_.columns:
        # generate and set scaler from train set, and apply to both train & test for each feature

        # get single-column df
        x_feature_df = _x_df_[[feature]].copy()

        # scale the single-column df
        scaler = MinMaxScaler()
        scaler.fit(x_feature_df.iloc[: sptt['train_split_f']])
        x_feature_df[[feature]] = scaler.transform(x_feature_df)

        # create new column with scaled data
        x_feature_df['{0}_z'.format(feature)] = x_feature_df[[feature]]

        # build new columns for each trailing timestep
        for i in range(general_params['timestep_ct'] - 1): x_feature_df['{0}-{1}'.format(feature, i + 1)] = x_feature_df['{0}_z'.format(feature)].shift(i + 1)

        # delete orig column
        del x_feature_df[feature]

        # convert to 3d np array
        x_np_a = x_feature_df.values
        x_np_a = x_np_a.reshape(x_np_a.shape[0], x_np_a.shape[1], 1)

        # turn into train and test
        train_x = x_np_a[sptt['train_split_i']: sptt['train_split_f']]
        test_x  = x_np_a[sptt['test_split_i' ]: sptt['test_split_f' ]]

        # add each np array to the dictionary with corresponding key
        train_x_dict[feature] = train_x
        test_x_dict[feature]  = test_x
    train_x = np.concatenate([train_x_dict[kv] for kv in train_x_dict], axis = -1)
    test_x  = np.concatenate([test_x_dict[kv]  for kv in test_x_dict] , axis = -1)
    return train_x, test_x

def split_xy(_xytt_df_):
    # split dataframe into x and y first (i.e. (10000, 3) -> (10000, 2) & (10000, 1)), because we need to make timestepped test sets (split train and test after)
    _x_df_ = _xytt_df_[[stat for stat in _xytt_df_.columns if 'fb_' not in stat]]
    _y_df_ = _xytt_df_[[stat for stat in _xytt_df_.columns if 'fb_' in stat]]
    print(_xytt_df_.index.min(), _xytt_df_.index.max(), _xytt_df_.shape)
    return _x_df_, _y_df_

def create_sample_xytt(_xytt_df_, start_point, general_params):
    # set slice points
    slice_i = start_point * general_params['test_size']
    slice_f = slice_i + general_params['train_size'] + general_params['test_size'] + general_params['future'] + general_params['timestep_ct']
    
    # create df slice
    xytt_s_df = _xytt_df_.iloc[slice_i: slice_f]
    return xytt_s_df

def split_xytt(xytt_df, start_point = 0):
    from ....params.general_params import general_params

    # create the sample df
    xytt_sample_df = create_sample_xytt(xytt_df, start_point, general_params)

    # split df into x and y
    x_df, y_df = split_xy(xytt_sample_df)

    # create split points (change train_split_i in the loop to accomodate for varying step sizes)
    sptt = split_points_train_test(general_params)

    # split y into train and test
    train_y, test_y = split_tt_y(y_df, sptt)

    # split x into train and test
    train_x, test_x = split_tt_x(x_df, sptt, general_params)

    return train_x, test_x, train_y, test_y