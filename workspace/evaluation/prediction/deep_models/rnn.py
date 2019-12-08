# modules
from pandas import DataFrame
import numpy as np

#params
from ....params import general_params
# settings
from ....util.settings  import pandas_settings, gpu_settings
# preprocessing
from ....util.functions.preprocessing.importing import load_dataset
from ....util.functions.preprocessing.split_dataset import split_xytt, to_categorical
from ....util.functions.preprocessing.apply_features import apply_features
# postprocessing
from ....util.functions.postprocessing.evaluate_model import eval_preds
# reporting
from ....util.functions.reporting import print_slice_stats, print_df_ratio
# model config
from ....util.functions.model_config.model_config import fit_model, compile_model

# models
from .rnn_model import rnn_model
from .rnn_params import rnn_params

# set up the full dataframe to loop through and make predictions
asset_history_df = load_dataset(general_params)
feature_df       = apply_features(asset_history_df.copy())

print_df_ratio(feature_df)
general_params['feature_ct'] = feature_df.shape[-1] - 1

# set loop duration, train_size
test_section_duration = general_params['test_size'] * general_params['total_sections']
shift = 0 # optional variable (positive integers only) to shift dataset to the left

# get the array loc values for the loop and trim the df
start_loc = (-1 * min([feature_df.shape[0], general_params['train_size'] + test_section_duration + general_params['future'] + general_params['timestep_ct']])) - shift
end_loc   = None # move df to the left (backwards in time)
if shift != 0: end_loc = -shift

feature_df = feature_df.iloc[start_loc: end_loc].reset_index(drop = True)

# build the model
model = rnn_model()

# compile the model
model = compile_model(model)

print(model.summary())
if general_params['reuse_init_model_weights']: init_model_weights = model.get_weights()

for section_ct in range(1000):
    if general_params['reuse_init_model_weights']: model.reset_states(); model.set_weights(init_model_weights)
    train_x, test_x, train_y, test_y = split_xytt(feature_df, section_ct)
    print_slice_stats(train_y)

    # fit the model
    fit_model(model, train_x, train_y)

    # make predictions
    preds_y = model.predict(test_x)

    # evaluate model accuracy
    eval_preds(preds_y, test_y)