from keras.layers       import Input, Dense, concatenate, Dropout, Flatten
from keras.models       import Model

from ....params.general_params import general_params

def rnn_model(timestep_ct, feature_ct):
    inputs_cp = Input(shape = (timestep_ct, feature_ct), name = 'inputs')

    x_cp_dense  = Dropout(0.01)(Dense(512)(Flatten()(inputs_cp)))
    x_cp_dense  = Dropout(0.01)(Dense(256)(x_cp_dense))

    final_layer = x_cp_dense
    main_output = Dense(units = 2, activation = 'softmax')(final_layer)

    model = Model(inputs_cp, [main_output])
    return model