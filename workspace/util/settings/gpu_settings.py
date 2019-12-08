from os import environ
from keras.backend.tensorflow_backend import set_session
import tensorflow as tf

# check if gpu available
def check_gpu_availability():
    from tensorflow.python.client import device_lib
    return device_lib.list_local_devices()

def config_gpu(gpu_number = -1, memory_split = 0.49):
    check_gpu_availability()

    environ["CUDA_VISIBLE_DEVICES"] = f"{gpu_number}"
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    config.gpu_options.per_process_gpu_memory_fraction = memory_split
    set_session(tf.Session(config = config))

config_gpu()