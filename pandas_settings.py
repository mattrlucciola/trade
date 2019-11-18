def set_options_pd(precision = 9):
    from pandas import set_option, options
    set_option('precision'        , precision)
    set_option('expand_frame_repr', False)
    set_option('display.max_rows' , None)

set_options_pd()