# from torchvision.transforms import transforms
from flask import Blueprint
from ctypes import *
# from skimage import io
from flask import render_template

from functool import captcha__is_login
bp=Blueprint("deplaning",__name__,url_prefix="/deplaning")
@bp.route('/')
@captcha__is_login
def deplaning_root():
    return "这是解刨网页"
@bp.route("/A1")
@captcha__is_login
def A1():
    return render_template("/deplaning/A1.html")

@bp.route("/A2")
@captcha__is_login
def A2():
    return render_template("/deplaning/A2.html")

@bp.route("/A3")
@captcha__is_login
def A3():
    return render_template("/deplaning/A3.html")

@bp.route("/A4")
@captcha__is_login
def A4():
    return render_template("/deplaning/A4.html")

@bp.route("/A5")
@captcha__is_login
def A5():
    return render_template("/deplaning/A5.html")

@bp.route("/A6")
@captcha__is_login
def A6():
    return render_template("/deplaning/A6.html")

@bp.route("/A7")
@captcha__is_login
def A7():
    return render_template("/deplaning/A7.html")

@bp.route("/A8")
@captcha__is_login
def A8():
    return render_template("/deplaning/A8.html")

@bp.route("/A9")
@captcha__is_login
def A9():
    return render_template("/deplaning/A9.html")