def namestr(obj, namespace = globals()): return [name for name in namespace if namespace[name] is obj][0]
def print_df_ratio(df): print(namestr(df) + ':', '{0}/{1} = {2:.4f}'.format(df['fb_trgt'].sum(), df.shape[0], df['fb_trgt'].sum() / df.shape[0]))

def print_slice_stats(train_y):
    slice_sum = train_y.sum(axis = 0)
    print(f"{slice_sum[1]:.0f}/{slice_sum.sum():.0f} = {slice_sum[1] / slice_sum.sum():.4f}")

#print(tfpn_df[['tp', 'tn', 'fp', 'fn', 'prec', 'recall']])