# from torchvision.transforms import transforms
import base64
import os
from flask import Blueprint, request, send_file, session
from flask import render_template
import numpy as np
import tensorflow as tf
from tensorflow import keras
import skimage.io as io  
from functool import captcha__is_login
from model import Comment, User
from PIL import Image,ImageFilter
from table_config import db
# import tensorflow as tf
bp=Blueprint("deeplearning",__name__,url_prefix="/deeplearning")
@bp.route('/A1')
@captcha__is_login
def A1():
    comment = Comment.query.filter(Comment.tieba_id == 1)
    return render_template(f'/deeplearning/A1.html', comment=comment)

@bp.route('/A2',methods=["GET","POST"])
@captcha__is_login
def A2():
    if request.method == "GET":
        comment = Comment.query.filter(Comment.tieba_id == 2)
        return render_template(f'/deeplearning/A2.html', comment=comment)
    """ img=request.files.get('pic')
    try:
        img.save('static/images/{}'.format("A2.jpg"))
        image=Image.open('static/images/{}'.format("A2.jpg"))
        X= image.filter(ImageFilter.GaussianBlur(radius=10))
        X.save('static/images/{}'.format("A2.jpg"))
        with open('static/images/{}'.format("A2.jpg"),'rb') as f:
            image_base64 = base64.b64encode(f.read())
        os.remove('static/images/{}'.format("A2.jpg")) 
        image_base64=str(image_base64,'utf-8')
        return render_template('/deeplearning/A2.html',picture=image_base64)
    except:
        return render_template('/deeplearning/A2.html',pic_error="请上传图片") """
    
@bp.route('/A3',methods=["GET","POST"])
@captcha__is_login
def A3():
    if request.method == "GET":
        comment = Comment.query.filter(Comment.tieba_id == 3)
        return render_template(f'/deeplearning/A3.html', comment=comment)
    img=request.files.get('pic')
    try:
        img.save('static/images/{}'.format("A3.jpg")) 
        img_src = io.imread('static/images/{}'.format("A3.jpg")) 
        os.remove('static/images/{}'.format("A3.jpg")) 
        img_src=img_src[:,:,1]
        X=tf.reshape(img_src,(1,28,28))
        model = keras.models.load_model('modea.h5')
        y_pred=np.argmax(model.predict(X),axis=1)
        # predict using the loaded model
        context = {'y_pred': str(y_pred[0])}
        return render_template('/deeplearning/A3.html',**context)
    except Exception as e:
        print(e)
        return render_template('/deeplearning/A3.html',pic_error="请上传图片")


@bp.route('/A4')
@captcha__is_login
def A4():
    comment = Comment.query.filter(Comment.tieba_id == 4)
    return render_template(f'/deeplearning/A4.html', comment=comment)

@bp.route('/A5')
@captcha__is_login
def A5():
    comment = Comment.query.filter(Comment.tieba_id == 5)
    return render_template(f'/deeplearning/A5.html', comment=comment)