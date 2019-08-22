import tensorflow as tf
import cv2
import os
import imutils
import numpy as np
from scipy import misc
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from server_app.tools import * 
from server_app.model import PSPNet101, PSPNet50

# Input and output files
cwd = os.getcwd()
print("[helper]: "+cwd)
input_directory = cwd+"/server_app/input"
output_directory = cwd+"/server_app/output"

# Indoor model
ADE20k_param = {'crop_size': [473, 473],
                'num_classes': 150,
                'model': PSPNet50,
                'weights_path': cwd+'/model/pspnet50-ade20k'}
# Outdoor model
cityscapes_param = {'crop_size': [720, 720],
                    'num_classes': 19,
                    'model': PSPNet101,
                    'weights_path': cwd+'/model/pspnet101-cityscapes/model.ckpt-0'}

IMAGE_MEAN = np.array((103.939, 116.779, 123.68), dtype=np.float32)

def execute(item, video_name):
    # Create image path
    image_path = input_directory+'/'+video_name+"/"+item
    print("[execute] image_path: "+image_path)
    if not item.startswith('.') and os.path.isfile(image_path):
        # NOTE: If you want to inference on indoor data, change this value to `ADE20k_param`
        param = cityscapes_param
        img_np, filename = load_img(image_path)
        img_shape = tf.shape(img_np)
        h, w = (tf.maximum(param['crop_size'][0], img_shape[0]), tf.maximum(param['crop_size'][1], img_shape[1]))
        img = preprocess(img_np, h, w)
        # Create network.
        PSPNet = param['model']
        net = PSPNet({'data': img}, is_training=False, num_classes=param['num_classes'])
        raw_output = net.layers['conv6']
        # Predictions.
        raw_output_up = tf.image.resize_bilinear(raw_output, size=[h, w], align_corners=True)
        raw_output_up = tf.image.crop_to_bounding_box(raw_output_up, 0, 0, img_shape[0], img_shape[1])
        raw_output_up = tf.argmax(raw_output_up, dimension=3)
        pred = decode_labels(raw_output_up, img_shape, param['num_classes'])
        # Init tf Session
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        sess = tf.Session(config=config)
        init = tf.global_variables_initializer()
        sess.run(init)
        ckpt_path = param['weights_path']
        loader = tf.train.Saver(var_list=tf.global_variables())
        loader.restore(sess, ckpt_path)
        print("Restored model parameters from {}".format(ckpt_path))
        # Run and get result image
        preds = sess.run(pred)
        # Write output image
        cv2.imwrite(output_directory+'/'+video_name+'/'+item, preds[0])
        print("image save to: "+output_directory+ "/"+video_name+"/"+item)
        # Restore for the next file
        tf.reset_default_graph()
        # printing the final thing 
    else:
        print("the file: "+image_path+ " is not file or it start with a dot (.)")
    print("Everything is done !")
#running the main fxn
# execute()

def create_pixel_dict(processed_image_path, raw_image_path):
    '''
    @param image_path: path of the image to analyize
    return doct with percentages of object detected
    '''
    print("image_path: "+processed_image_path)
    img = cv2.imread(processed_image_path, cv2.IMREAD_UNCHANGED)
    dimensions = img.shape
    height = img.shape[0]
    width = img.shape[1]
    total_pixels = height*width
    print("total pixels in image: "+str(total_pixels))
    # creating local_pixel_dict
    local_pixel_dict = {}
    for h in range(height):
        for w in range(width):
            pixel = img[h, w]
            color_str = str(pixel[0])+","+str(pixel[1])+","+str(pixel[2])
            # search for color str
            if color_str in color_dict.keys():
                print("found a "+color_dict[color_str])
                material = color_dict[color_str]
                # if object is not in keys add the object and give it a value of zero 
                if material not in local_pixel_dict.keys():
                    local_pixel_dict[material] = 0
                # otherwise if object is present in local dict, increment it's value
                else:
                    local_pixel_dict[material] = local_pixel_dict[material]+1
    print(local_pixel_dict)
    # convert local_pixel_dict to percent_dict
    for mat in local_pixel_dict:
        local_pixel_dict[mat] = (local_pixel_dict[mat]/total_pixels)*100
    return local_pixel_dict