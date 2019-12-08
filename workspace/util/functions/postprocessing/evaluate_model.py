
from pandas import DataFrame, concat

# global var
tfpn_df_prev = DataFrame()

def update_tfpn_df_prev(tfpn_df, print_df):
    global tfpn_df_prev
    if tfpn_df_prev.shape != DataFrame().shape: tfpn_df_prev[['tp', 'tn', 'fp', 'fn']] += tfpn_df[['tp', 'tn', 'fp', 'fn']]
    else                                      : tfpn_df_prev = tfpn_df[['tp', 'tn', 'fp', 'fn']]
    print_tfpn_prev = tfpn_df_prev.copy()
    print_tfpn_prev['prec']   = print_tfpn_prev['tp'] / (print_tfpn_prev[['tp', 'fp']].sum(axis = 1))
    print_tfpn_prev['recall'] = print_tfpn_prev['tp'] / (print_tfpn_prev[['tp', 'fn']].sum(axis = 1))
    
    if print_df: print(concat([tfpn_df[['tp', 'tn', 'fp', 'fn', 'prec', 'recall']], print_tfpn_prev], axis = 1))

def calc_secondary_stats(tfpn_df, precision = True, recall = True, accuracy = False):
    if precision == True : tfpn_df['prec']     = tfpn_df['tp'] / (tfpn_df[['tp', 'fp']].sum(axis = 1))
    if recall    == True : tfpn_df['recall']   = tfpn_df['tp'] / (tfpn_df[['tp', 'fn']].sum(axis = 1))
    if accuracy  == False: tfpn_df['accuracy'] = (tfpn_df[['tp', 'tn']].sum(axis = 1)) / (tfpn_df[['fp', 'fn']].sum(axis = 1) + tfpn_df[['tp', 'tn']].sum(axis = 1))
    return tfpn_df

def eval_preds(preds_y, test_y, print_df = True):
    # make the preds df
    pred_df = make_pred_df(preds_y, test_y)

    # evaluate and save preds
    tfpn_df_list = []
    for _thresh in [x / 100 for x in list(range(100)) if x % 5 == 0 and (x > 20)]:
        df = pred_df.copy()
        df['preds_y'] = df['preds_y'] > _thresh
        df['tp'] = (df['preds_y'] == 1) & (df['test_y'] == 1)
        df['tn'] = (df['preds_y'] == 0) & (df['test_y'] == 0)
        df['fp'] = (df['preds_y'] == 1) & (df['test_y'] == 0)
        df['fn'] = (df['preds_y'] == 0) & (df['test_y'] == 1)
        tfpn_df_list.append({'thresh': _thresh, 'tp': df['tp'].sum(), 'tn': df['tn'].sum(), 'fp': df['fp'].sum(), 'fn': df['fn'].sum()})
    
    tfpn_df = DataFrame(tfpn_df_list).set_index(['thresh'], drop = True)
    tfpn_df = tfpn_df[['tp', 'tn', 'fp', 'fn']]
    tfpn_df = calc_secondary_stats(tfpn_df)
    update_tfpn_df_prev(tfpn_df, print_df)

def make_pred_df(preds_y, test_y):
    if type(preds_y) == type([0]): preds_y = preds_y[0]
    if len(preds_y.shape) == 2:
        pred_df = DataFrame(preds_y, columns = ['0', '1'])
        pred_df['og_adj1'] = (pred_df['1'] ** 2) * ((pred_df['1'] * (1 + (((pred_df['1'] - pred_df['0']) / pred_df['1'])))) ** (1 / 4))
        pred_df['preds_y'] = pred_df['1'].where(pred_df['1'] > pred_df['0'], other = 0)

        # add adjusted vals
        pred_df['preds_adj1'] = (pred_df['preds_y'] ** 2) * ((pred_df['1'] * (1 + (((pred_df['1'] - pred_df['0']) / pred_df['1'])))) ** (1 / 4))

        # add test set
        pred_df['test_y'] = test_y[: , -1]
    return pred_df