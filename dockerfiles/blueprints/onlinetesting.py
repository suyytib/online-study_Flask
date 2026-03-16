import random
from flask import Blueprint, request
from flask import render_template
from model import  Questions
from functool import captcha__is_login
bp=Blueprint("onlinetesting",__name__,url_prefix="/onlinetesting")
@bp.route('/')
@captcha__is_login
def onlinetesting():
    return render_template("onlinetesting.html")

@bp.route('/testing/',methods=["POST"]) 
@captcha__is_login
def testing():
    id_questions=str(random.randint(1, 24))
    text=Questions.query.filter_by(id=id_questions)
    test_answer=text[0].answer
    test_user_answer=request.form.get("answers")
    test_question=text[0].question
    return render_template('onlinetesting.html',answers=test_user_answer,questions=test_question,true_answers=test_answer)

