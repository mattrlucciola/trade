def set_options_pd(pd_precision, float_precision):
    from pandas import set_option, options
    set_option('expand_frame_repr', False)
    set_option('display.max_rows' , None)
    if pd_precision   : set_option('precision'        , pd_precision)
    if float_precision: set_option('display.float_format', lambda x: '{:.{}f}'.format(x, float_precision))
    # set_option('display.float_format', lambda x: '%.8f'.format(float_precision) % x)

set_options_pd()