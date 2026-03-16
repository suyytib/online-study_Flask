import time
# from torchvision.transforms import transforms
from flask import Blueprint, g, request
# from skimage import io
from flask import render_template
from functool import captcha__is_login
from table_config import db

from model import Comment, User,Tiebas
# import tensorflow as tf
bp=Blueprint("tieba",__name__,url_prefix="/tieba")
@bp.route('/')
@captcha__is_login
def tieba_root():
    tieba = Tiebas.query.filter().all()
    return render_template('/tieba.html', tieba=tieba)

@bp.route('/writeBlog', methods=['POST'])
@captcha__is_login
def writeblog():
    title = request.form.get("title")
    text = request.form.get("text")
    btnradios = request.form.get("btnradios")
    user=User.query.get(g.user_id)
    username=user.username
    create_time = time.strftime("%Y-%m-%d %H:%M:%S")
    blog = Tiebas(title=title, text=text, create_time=create_time, user=username ,types=btnradios)
    db.session.add(blog)
    db.session.commit()
    return {
        'success': True,
        'message': '添加成功！',
    }
    
@bp.route('/comment/',methods=['POST']) 
@captcha__is_login
def comment():
    text = request.values.get('text')
    tiebaId = request.values.get('tiebaId')
    user=User.query.get(g.user_id)
    username=user.username
    # 获取当前系统时间
    create_time = time.strftime("%Y-%m-%d %H:%M:%S")
    comment = Comment(text=text, create_time=create_time, tieba_id=tiebaId, user=username)
    db.session.add(comment)
    db.session.commit()
    return {
        'success': True,
        'message': '评论成功！',
    }

@bp.route('/viewBlog', methods=['GET'])
@captcha__is_login
def viewblog():
    tiebaid=request.args["tiebaid"]
    blog = Tiebas.query.filter(Tiebas.id==tiebaid).first()
    comment = Comment.query.filter(Comment.tieba_id == (blog.id+10000))
    return render_template('/blog.html', comment=comment,blog=blog)

@bp.route('/typesBlog',methods=['GET'])
@captcha__is_login
def typeblog():
    btnradio = request.args["btnradio"]
    if btnradio== "0":
        tieba = Tiebas.query.filter().all()
    else:
        tieba = Tiebas.query.filter(Tiebas.types==btnradio).all()
    return render_template('/tieba.html',tieba=tieba)