from keras.optimizers import Nadam

rnn_params = {
    'optimizer': Nadam(lr = 0.002, beta_1 = 0.899, beta_2 = 0.99, epsilon = None, schedule_decay = 0.004),
    'loss'     : 'mean_squared_error',

    'stat_list'  : ['high'
                    ,'low'
                    ,'vol_quote'
                    #,'btc_price'
                    ],
}