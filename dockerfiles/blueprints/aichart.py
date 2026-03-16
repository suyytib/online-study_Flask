import random
from flask import Blueprint, request
from flask import render_template
from model import  Questions
from functool import captcha__is_login
from zhipuai import ZhipuAI
def chat_with_gpt(messages): 
        client = ZhipuAI(api_key="46996b5ed6c2eb4b45687a952b3ce40c.lt2N2lEN4dBPCSbD") # 请填写您自己的APIKey
        response = client.chat.completions.create(
            model="glm-4-0520",
            messages=messages,
            top_p= 0.7,
            temperature= 0.9,
            max_tokens=4095,
            stream=True,
        )
        res=""
        for trunk in response:
            res+=trunk.choices[0].delta.content
        return res

bp=Blueprint("aichart",__name__,url_prefix="/aichart")
@bp.route('/')
@captcha__is_login
def aichart():
    return render_template("aichart.html")

@bp.route('/chart/',methods=["POST"]) 
@captcha__is_login
def chart():
    answer = request.form.get("answer")
    messages =[]
    user_input = answer
    messages.append({"role": "user", "content": user_input})
    response = chat_with_gpt(messages)
    print(response)
    return {
        'success': True,
        'message': response,
    }