general_params = {
    'coin_pair' : 'ADABTC',
    'quote_coin': 'BTC',

    'train_size' : 10000,
    'motif_size' : 20,
    'timestep_ct': 120,
    'test_size'  : 200,

    'future'    : 45,
    'pct_high'  : 0.004,
    'pct_low'   : 0.008,
    'y_classes' : 2,
    'epoch_ct'  : 30,

    'target_ratio'  : 0.65,
    'step_count'    : 200,
    'total_sections': 2000,
    
    'use_class_weights': False,
    'reuse_init_model_weights': False,
}
general_params['pct_list'] = [general_params['pct_high'], -general_params['pct_low']]