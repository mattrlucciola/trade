import numpy as np
from sklearn.utils import class_weight

from ....params.general_params import general_params
from ....evaluation.prediction.deep_models.rnn_params import rnn_params

def fit_model(model, train_x, train_y):

    # establish class weights, if needed
    if general_params['use_class_weights']: cw = class_weight.compute_class_weight('balanced', np.unique(train_y[: , 0: 1]), train_y[: , 1]); cw = {0: cw[0], 1: cw[1]}
    else                                  : cw = None

    model.fit(
        x            = train_x,
        y            = [train_y],
        epochs       = general_params['epoch_ct'],
        batch_size   = int(train_x.shape[0] / 10),
        class_weight = cw,
        verbose      = 2
    )
    return

def compile_model(model):
    model.compile(
        loss      = rnn_params['loss'],
        optimizer = rnn_params['optimizer'],
        metrics   = ['acc']
    )
    return model