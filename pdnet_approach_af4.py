import os.path as op
import time

from keras.backend.tensorflow_backend import set_session
from keras.callbacks import TensorBoard, ModelCheckpoint, ReduceLROnPlateau
from keras.models import load_model
from keras.utils.vis_utils import model_to_dot
from keras_tqdm import TQDMCallback
import tensorflow as tf

from data import MaskedUntouched2DSequence
from evaluate import psnr, ssim
from pdnet_crop import pdnet_crop





tf.logging.set_verbosity(tf.logging.INFO)






# paths
train_path = '/media/Zaccharie/UHRes/singlecoil_train/singlecoil_train/'
val_path = '/media/Zaccharie/UHRes/singlecoil_val/'
test_path = '/media/Zaccharie/UHRes/singlecoil_test/'





n_samples_train = 34742
n_samples_val = 7135

n_volumes_train = 973
n_volumes_val = 199





# generators
AF = 4
# MaskShifted2DSequence, MaskShiftedSingleImage2DSequence, MaskedUntouched2DSequence
train_gen = MaskedUntouched2DSequence(train_path, af=AF, inner_slices=8)
val_gen = MaskedUntouched2DSequence(val_path, af=AF)





run_params = {
#     'n_primal': 5,
#     'n_dual': 5,
#     'n_iter': 7,
#     'n_filters': 32,
    'n_primal': 2,
    'n_dual': 2,
    'n_iter': 2,
    'n_filters': 16,
}

n_epochs = 10
run_id = f'pdnet_af{AF}_{int(time.time())}'
chkpt_path = f'checkpoints/{run_id}' + '-{epoch:02d}.hdf5'





chkpt_cback = ModelCheckpoint(chkpt_path, period=2, save_weights_only=True)
log_dir = op.join('logs', run_id)
tboard_cback = TensorBoard(
    log_dir=log_dir,
    histogram_freq=0,
    write_graph=True,
    write_images=False,
)
lr_on_plat_cback = ReduceLROnPlateau(monitor='val_loss', min_lr=5*1e-5, mode='auto', patience=3)
tqdm_cb = TQDMCallback(metric_format="{name}: {value:e}")






model = pdnet_crop(lr=1e-3, **run_params)
print(model.summary(line_length=150))





model.fit_generator(
    train_gen,
    steps_per_epoch=n_volumes_train,
    epochs=n_epochs,
    validation_data=val_gen,
    validation_steps=n_volumes_val,
    verbose=0,
    callbacks=[tqdm_cb, tboard_cback, chkpt_cback, lr_on_plat_cback],
    max_queue_size=100,
    use_multiprocessing=True,
    workers=35,
)