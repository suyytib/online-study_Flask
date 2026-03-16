# from torchvision.transforms import transforms
import base64
from io import BytesIO
import math
import os
import cv2
from flask import Blueprint, jsonify, request
# from skimage import io
from flask import render_template
from PIL import Image,ImageFilter
import numpy as np
from functool import captcha__is_login
from model import Comment
from skimage.feature import local_binary_pattern,haar_like_feature_coord,draw_haar_like_feature
# import tensorflow as tf

class Hog_descriptor():
    def __init__(self, img, cell_size=16, bin_size=8):
        self.img = img
        self.img = np.sqrt(img / np.max(img))
        self.img = img * 255
        self.cell_size = cell_size
        self.bin_size = bin_size
        self.angle_unit = 360 // self.bin_size
        assert type(self.bin_size) == int, "bin_size should be integer,"
        assert type(self.cell_size) == int, "cell_size should be integer,"
        assert type(self.angle_unit) == int, "bin_size should be divisible by 360"

    def extract(self):
        height, width = self.img.shape
        gradient_magnitude, gradient_angle = self.global_gradient()
        gradient_magnitude = abs(gradient_magnitude)
        cell_gradient_vector = np.zeros((height // self.cell_size, width // self.cell_size, self.bin_size))
        for i in range(cell_gradient_vector.shape[0]):
            for j in range(cell_gradient_vector.shape[1]):
                cell_magnitude = gradient_magnitude[i * self.cell_size:(i + 1) * self.cell_size,
                                 j * self.cell_size:(j + 1) * self.cell_size]
                cell_angle = gradient_angle[i * self.cell_size:(i + 1) * self.cell_size,
                             j * self.cell_size:(j + 1) * self.cell_size]
                cell_gradient_vector[i][j] = self.cell_gradient(cell_magnitude, cell_angle)

        hog_image = self.render_gradient(np.zeros([height, width]), cell_gradient_vector)
        hog_vector = []
        for i in range(cell_gradient_vector.shape[0] - 1):
            for j in range(cell_gradient_vector.shape[1] - 1):
                block_vector = []
                block_vector.extend(cell_gradient_vector[i][j])
                block_vector.extend(cell_gradient_vector[i][j + 1])
                block_vector.extend(cell_gradient_vector[i + 1][j])
                block_vector.extend(cell_gradient_vector[i + 1][j + 1])
                mag = lambda vector: math.sqrt(sum(i ** 2 for i in vector))
                magnitude = mag(block_vector)
                if magnitude != 0:
                    normalize = lambda block_vector, magnitude: [element / magnitude for element in block_vector]
                    block_vector = normalize(block_vector, magnitude)
                hog_vector.append(block_vector)
        return hog_vector, hog_image

    def global_gradient(self):
        gradient_values_x = cv2.Sobel(self.img, cv2.CV_64F, 1, 0, ksize=5)
        gradient_values_y = cv2.Sobel(self.img, cv2.CV_64F, 0, 1, ksize=5)
        gradient_magnitude = cv2.addWeighted(gradient_values_x, 0.5, gradient_values_y, 0.5, 0)
        gradient_angle = cv2.phase(gradient_values_x, gradient_values_y, angleInDegrees=True)
        return gradient_magnitude, gradient_angle

    def cell_gradient(self, cell_magnitude, cell_angle):
        orientation_centers = [0] * self.bin_size
        for i in range(cell_magnitude.shape[0]):
            for j in range(cell_magnitude.shape[1]):
                gradient_strength = cell_magnitude[i][j]
                gradient_angle = cell_angle[i][j]
                min_angle, max_angle, mod = self.get_closest_bins(gradient_angle)
                orientation_centers[min_angle] += (gradient_strength * (1 - (mod / self.angle_unit)))
                orientation_centers[max_angle] += (gradient_strength * (mod / self.angle_unit))
        return orientation_centers

    def get_closest_bins(self, gradient_angle):
        idx = int(gradient_angle / self.angle_unit)
        mod = gradient_angle % self.angle_unit
        return idx, (idx + 1) % self.bin_size, mod

    def render_gradient(self, image, cell_gradient):
        cell_width = self.cell_size / 2
        max_mag = np.array(cell_gradient).max()
        for x in range(cell_gradient.shape[0]):
            for y in range(cell_gradient.shape[1]):
                cell_grad = cell_gradient[x][y]
                cell_grad /= max_mag
                angle = 0
                angle_gap = self.angle_unit
                for magnitude in cell_grad:
                    angle_radian = math.radians(angle)
                    x1 = int(x * self.cell_size + magnitude * cell_width * math.cos(angle_radian))
                    y1 = int(y * self.cell_size + magnitude * cell_width * math.sin(angle_radian))
                    x2 = int(x * self.cell_size - magnitude * cell_width * math.cos(angle_radian))
                    y2 = int(y * self.cell_size - magnitude * cell_width * math.sin(angle_radian))
                    cv2.line(image, (y1, x1), (y2, x2), int(255 * math.sqrt(magnitude)))
                    angle += angle_gap
        return image

bp=Blueprint("imageprocessing",__name__,url_prefix="/imageprocessing")
@bp.route('/',methods=["GET","POST"])
@captcha__is_login
def imageprocessing_root():
    if request.method == "GET":
        comment = Comment.query.filter(Comment.tieba_id == 0)
        return render_template(f'imageprocessing.html', comment=comment)

@bp.route('/A1/',methods=["POST"])
@captcha__is_login
def A1():   #高斯模糊
    try:
        img=request.form.get('data')
        head,context=img.split(",")
        img_data = base64.b64decode(context)
        image = Image.open(BytesIO(img_data))
        X= image.filter(ImageFilter.GaussianBlur(radius=10))
        X.save('static/images/{}'.format("A1.png"))
        with open('static/images/{}'.format("A1.png"),'rb') as f:
            image_base64 = base64.b64encode(f.read())
        os.remove('static/images/{}'.format("A1.png")) 
        image_base64=str(image_base64,'utf-8')
        return jsonify({"code":200, "message": "success!", "datas": image_base64})
    except:
        return jsonify({"code":404, "message": "fail!", "datas": None})
    
@bp.route('/A2/',methods=["POST"])
@captcha__is_login
def A2():   #图像锐化
    try:
        img=request.form.get('data')
        head,context=img.split(",")
        img_data = base64.b64decode(context)
        image = Image.open(BytesIO(img_data))
        X= image.filter(ImageFilter.SHARPEN)
        X.save('static/images/{}'.format("A2.png"))
        with open('static/images/{}'.format("A2.png"),'rb') as f:
            image_base64 = base64.b64encode(f.read())
        os.remove('static/images/{}'.format("A2.png")) 
        image_base64=str(image_base64,'utf-8')
        return jsonify({"code":200, "message": "success!", "datas": image_base64})
    except:
        return jsonify({"code":404, "message": "fail!", "datas": None})
    
@bp.route('/A3/',methods=["POST"])
@captcha__is_login
def A3():   #图像平滑
    try:
        img=request.form.get('data')
        head,context=img.split(",")
        img_data = base64.b64decode(context)
        image = Image.open(BytesIO(img_data))
        X= image.filter(ImageFilter.SMOOTH)
        X.save('static/images/{}'.format("A3.png"))
        with open('static/images/{}'.format("A3.png"),'rb') as f:
            image_base64 = base64.b64encode(f.read())
        os.remove('static/images/{}'.format("A3.png")) 
        image_base64=str(image_base64,'utf-8')
        return jsonify({"code":200, "message": "success!", "datas": image_base64})
    except:
        return jsonify({"code":404, "message": "fail!", "datas": None})
    
@bp.route('/A4/',methods=["POST"])
@captcha__is_login
def A4():   #图像配准
    try:
        img=request.form.get('data')
        img1=request.form.get('data1')
        head,context=img.split(",")
        head1,context1=img1.split(",")
        img_data = base64.b64decode(context)
        img1_data = base64.b64decode(context1)
        image = Image.open(BytesIO(img_data))
        image2 = Image.open(BytesIO(img1_data))
        img1 = cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2GRAY)
        img2 = cv2.cvtColor(np.asarray(image2), cv2.COLOR_BGR2GRAY)
        height, width = img2.shape
        orb = cv2.ORB_create(5000)
        kp1, des1 = orb.detectAndCompute(img1,None)
        kp2, des2 = orb.detectAndCompute(img2,None)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1,des2)
        matches = sorted(matches, key = lambda x:x.distance)
        matches = matches[:int(len(matches)*0.9)]
        no_of_matches = len(matches)
        p1 = np.zeros((no_of_matches, 2))
        p2 = np.zeros((no_of_matches, 2))
        for i in range(len(matches)):
            p1[i, :] = kp1[matches[i].queryIdx].pt
            p2[i, :] = kp2[matches[i].trainIdx].pt
        homography, mask = cv2.findHomography(p1, p2, cv2.RANSAC)
        transformed_img = cv2.warpPerspective(img1,homography, (width, height))
        cv2.imwrite('static/images/{}'.format("A4.png"), transformed_img)
        with open('static/images/{}'.format("A4.png"),'rb') as f:
            image_base64 = base64.b64encode(f.read())
        os.remove('static/images/{}'.format("A4.png")) 
        image_base64=str(image_base64,'utf-8')
        return jsonify({"code":200, "message": "success!", "datas": image_base64})
    except Exception as e:
        print(e)
        return jsonify({"code":404, "message": "fail!", "datas": None})
    
@bp.route('/A5/',methods=["POST"])
@captcha__is_login
def A5():   #图像融合
    try:
        img=request.form.get('data')
        img1=request.form.get('data1')
        head,context=img.split(",")
        head1,context1=img1.split(",")
        img_data = base64.b64decode(context)
        img1_data = base64.b64decode(context1)
        image = Image.open(BytesIO(img_data))
        image = image.resize((400,400)) 
        image2 = Image.open(BytesIO(img1_data))
        image2 = image2.resize((400,400)) 
        image = image.convert('RGBA')
        image2 = image2.convert('RGBA')
        X= Image.blend(image,image2,0.5)
        X.save('static/images/{}'.format("A5.png"))
        with open('static/images/{}'.format("A5.png"),'rb') as f:
            image_base64 = base64.b64encode(f.read())
        os.remove('static/images/{}'.format("A5.png")) 
        image_base64=str(image_base64,'utf-8')
        return jsonify({"code":200, "message": "success!", "datas": image_base64})
    except:
        return jsonify({"code":404, "message": "fail!", "datas": None})
    
@bp.route('/A6/',methods=["POST"])
@captcha__is_login
def A6():   #伪彩色处理
    try:
        img=request.form.get('data')
        head,context=img.split(",")
        img_data = base64.b64decode(context)
        image = Image.open(BytesIO(img_data))
        image.save('static/images/{}'.format("A6.png"))
        im_gray = cv2.imread('static/images/{}'.format("A6.png"), cv2.IMREAD_GRAYSCALE)
        im_color = cv2.applyColorMap(im_gray, cv2.COLORMAP_JET)
        cv2.imwrite('static/images/{}'.format("A6.png"),im_color)
        with open('static/images/{}'.format("A6.png"),'rb') as f:
            image_base64 = base64.b64encode(f.read())
        os.remove('static/images/{}'.format("A6.png")) 
        image_base64=str(image_base64,'utf-8')
        return jsonify({"code":200, "message": "success!", "datas": image_base64})
    except:
        return jsonify({"code":404, "message": "fail!", "datas": None})
    
@bp.route('/A7/',methods=["POST"])
@captcha__is_login
def A7():   #自动阈值分割
    try:
        img=request.form.get('data')
        head,context=img.split(",")
        img_data = base64.b64decode(context)
        image = Image.open(BytesIO(img_data))
        image.save('static/images/{}'.format("A6.png"))
        image = cv2.imread('static/images/{}'.format("A6.png"), cv2.IMREAD_GRAYSCALE)
        ratio=0.15
        I_mean = cv2.boxFilter(image, cv2.CV_32FC1, (5, 5))
        out = image - (1.0 - ratio) * I_mean
        out[out >= 0] = 255
        out[out < 0] = 0
        out = out.astype(np.uint8)
        cv2.imwrite('static/images/{}'.format("A7.png"),out)
        with open('static/images/{}'.format("A7.png"),'rb') as f:
            image_base64 = base64.b64encode(f.read())
        os.remove('static/images/{}'.format("A7.png")) 
        image_base64=str(image_base64,'utf-8')
        return jsonify({"code":200, "message": "success!", "datas": image_base64})
    except:
        return jsonify({"code":404, "message": "fail!", "datas": None})
    
@bp.route('/A8/',methods=["POST"])
@captcha__is_login
def A8():   #直方图均衡化
    try:
        img=request.form.get('data')
        head,context=img.split(",")
        img_data = base64.b64decode(context)
        image = Image.open(BytesIO(img_data))
        gray_image = image.convert('L')
        gray_arr = np.array(gray_image)
        hist, bins = np.histogram(gray_arr, 255)
        cdf = np.cumsum(hist)
        cdf = 255 * (cdf/cdf[-1])
        res = np.interp(gray_arr.flatten(), bins[:-1], cdf)
        res = res.reshape(gray_arr.shape)
        image=Image.fromarray(res.astype(np.uint8))
        image.save('static/images/{}'.format("A8.png"))
        with open('static/images/{}'.format("A8.png"),'rb') as f:
            image_base64 = base64.b64encode(f.read())
        os.remove('static/images/{}'.format("A8.png")) 
        image_base64=str(image_base64,'utf-8')
        return jsonify({"code":200, "message": "success!", "datas": image_base64})
    except:
        return jsonify({"code":404, "message": "fail!", "datas": None})
    
@bp.route('/A9/',methods=["POST"])
@captcha__is_login
def A9():   #图像压缩
    try:
        img=request.form.get('data')
        head,context=img.split(",")
        img_data = base64.b64decode(context)
        image = Image.open(BytesIO(img_data))
        image.save('static/images/{}'.format("A9.png"))
        image = cv2.imread('static/images/{}'.format("A9.png"), cv2.IMREAD_GRAYSCALE)
        params = [cv2.IMWRITE_PNG_COMPRESSION, 3]
        msg = cv2.imencode(".png", image, params)[1]
        msg = (np.array(msg)).tostring()
        os.remove('static/images/{}'.format("A9.png")) 
        msg = base64.b64encode(msg)
        msg=str(msg,'utf-8')
        return jsonify({"code":200, "message": "success!", "datas": msg})
    except Exception as e:
        print(e)
        return jsonify({"code":404, "message": "fail!", "datas": None})
    
@bp.route('/A10/',methods=["POST"])
@captcha__is_login
def A10():   #图像解压
    try:
        img=request.form.get('data')
        img_data = base64.b64decode(img)
        nparr = np.frombuffer(img_data, dtype=np.uint8)
        img_decode = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cv2.imwrite('static/images/{}'.format("A10.png"), img_decode) 
        with open('static/images/{}'.format("A10.png"),'rb') as f:
            image_base64 = base64.b64encode(f.read())
        os.remove('static/images/{}'.format("A10.png")) 
        image_base64=str(image_base64,'utf-8')
        return jsonify({"code":200, "message": "success!", "datas": image_base64})
    except Exception as e:
        print(e)
        return jsonify({"code":404, "message": "fail!", "datas": None})
    
@bp.route('/A11/',methods=["POST"])
@captcha__is_login
def A11():   #仿射变换
    try:
        img=request.form.get('data')
        head,context=img.split(",")
        img_data = base64.b64decode(context)
        image = Image.open(BytesIO(img_data))
        image.save('static/images/{}'.format("A11.png"))
        src = cv2.imread('static/images/{}'.format("A11.png"))
        rows, cols = src.shape[: 2]
        post1 = np.float32([[50, 50], [200, 50], [50, 200]])
        post2 = np.float32([[10, 100], [200, 50], [100,250]])
        M = cv2.getAffineTransform(post1, post2)
        result = cv2.warpAffine(src, M, (rows, cols))
        cv2.imwrite('static/images/{}'.format("A11.png"),result) 
        with open('static/images/{}'.format("A11.png"),'rb') as f:
            image_base64 = base64.b64encode(f.read())
        os.remove('static/images/{}'.format("A11.png")) 
        image_base64=str(image_base64,'utf-8')
        return jsonify({"code":200, "message": "success!", "datas": image_base64})
    except Exception as e:
        print(e)
        return jsonify({"code":404, "message": "fail!", "datas": None})
    
@bp.route('/A12/',methods=["POST"])
@captcha__is_login
def A12():   #HOG特征提取
    try:
        img=request.form.get('data')
        head,context=img.split(",")
        img_data = base64.b64decode(context)
        image = Image.open(BytesIO(img_data))
        image.save('static/images/{}'.format("A12.png"))
        img = cv2.imread('static/images/{}'.format("A12.png"),cv2.IMREAD_GRAYSCALE)
        hog = Hog_descriptor(img, cell_size=8, bin_size=8)
        vector, image = hog.extract()
        cv2.imwrite('static/images/{}'.format("A12.png"),image) 
        image=Image.open('static/images/{}'.format("A12.png"))
        X=image.convert('L')
        X.save('static/images/{}'.format("A12.png"))
        with open('static/images/{}'.format("A12.png"),'rb') as f:
            image_base64 = base64.b64encode(f.read())
        os.remove('static/images/{}'.format("A12.png")) 
        image_base64=str(image_base64,'utf-8')
        return jsonify({"code":200, "message": "success!", "datas": image_base64})
    except Exception as e:
        print(e)
        return jsonify({"code":404, "message": "fail!", "datas": None})
    
@bp.route('/A13/',methods=["POST"])
@captcha__is_login
def A13():   #LBP特征提取
    try:
        img=request.form.get('data')
        head,context=img.split(",")
        img_data = base64.b64decode(context)
        image = Image.open(BytesIO(img_data))
        image.save('static/images/{}'.format("A13.png"))
        img = cv2.imread('static/images/{}'.format("A13.png"),cv2.IMREAD_COLOR)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        lbp = local_binary_pattern(img_gray, 8, 1)
        cv2.imwrite('static/images/{}'.format("A13.png"),lbp) 
        image=Image.open('static/images/{}'.format("A13.png"))
        X=image.convert('L')
        X.save('static/images/{}'.format("A13.png"))
        with open('static/images/{}'.format("A13.png"),'rb') as f:
            image_base64 = base64.b64encode(f.read())
        os.remove('static/images/{}'.format("A13.png")) 
        image_base64=str(image_base64,'utf-8')
        return jsonify({"code":200, "message": "success!", "datas": image_base64})
    except Exception as e:
        print(e)
        return jsonify({"code":404, "message": "fail!", "datas": None})
    
@bp.route('/A14/',methods=["POST"])
@captcha__is_login
def A14():   #腐蚀
    try:
        img=request.form.get('data')
        head,context=img.split(",")
        img_data = base64.b64decode(context)
        image = Image.open(BytesIO(img_data))
        image.save('static/images/{}'.format("A14.png"))
        img = cv2.imread('static/images/{}'.format("A14.png"),cv2.IMREAD_COLOR)
        b, g, r = cv2.split(img)
        img2 = cv2.merge([r, g, b])
        rows, cols = img.shape[:2]
        src = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, src = cv2.threshold(src, 102, 255, cv2.THRESH_BINARY)
        kernel = np.ones((10, 10), np.uint8)
        res1 = cv2.erode(src, kernel)
        cv2.imwrite('static/images/{}'.format("A14.png"),res1) 
        with open('static/images/{}'.format("A14.png"),'rb') as f:
            image_base64 = base64.b64encode(f.read())
        os.remove('static/images/{}'.format("A14.png")) 
        image_base64=str(image_base64,'utf-8')
        return jsonify({"code":200, "message": "success!", "datas": image_base64})
    except Exception as e:
        print(e)
        return jsonify({"code":404, "message": "fail!", "datas": None})
    
@bp.route('/A15/',methods=["POST"])
@captcha__is_login
def A15():   #膨胀
    try:
        img=request.form.get('data')
        head,context=img.split(",")
        img_data = base64.b64decode(context)
        image = Image.open(BytesIO(img_data))
        image.save('static/images/{}'.format("A15.png"))
        img = cv2.imread('static/images/{}'.format("A15.png"),cv2.IMREAD_COLOR)
        b, g, r = cv2.split(img)
        img2 = cv2.merge([r, g, b])
        rows, cols = img.shape[:2]
        src = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, src = cv2.threshold(src, 102, 255, cv2.THRESH_BINARY)
        kernel = np.ones((10, 10), np.uint8)
        dilated = cv2.dilate(src, kernel)
        cv2.imwrite('static/images/{}'.format("A15.png"),dilated) 
        with open('static/images/{}'.format("A15.png"),'rb') as f:
            image_base64 = base64.b64encode(f.read())
        os.remove('static/images/{}'.format("A15.png")) 
        image_base64=str(image_base64,'utf-8')
        return jsonify({"code":200, "message": "success!", "datas": image_base64})
    except Exception as e:
        print(e)
        return jsonify({"code":404, "message": "fail!", "datas": None})
    
@bp.route('/A16/',methods=["POST"])
@captcha__is_login
def A16():   #开运算
    try:
        img=request.form.get('data')
        head,context=img.split(",")
        img_data = base64.b64decode(context)
        image = Image.open(BytesIO(img_data))
        image.save('static/images/{}'.format("A16.png"))
        img = cv2.imread('static/images/{}'.format("A16.png"),cv2.IMREAD_COLOR)
        b, g, r = cv2.split(img)
        img2 = cv2.merge([r, g, b])
        rows, cols = img.shape[:2]
        src = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, src = cv2.threshold(src, 102, 255, cv2.THRESH_BINARY)
        kernel = np.ones((10, 10), np.uint8)
        opened = cv2.morphologyEx(src, cv2.MORPH_OPEN, kernel)
        cv2.imwrite('static/images/{}'.format("A16.png"),opened) 
        with open('static/images/{}'.format("A16.png"),'rb') as f:
            image_base64 = base64.b64encode(f.read())
        os.remove('static/images/{}'.format("A16.png")) 
        image_base64=str(image_base64,'utf-8')
        return jsonify({"code":200, "message": "success!", "datas": image_base64})
    except Exception as e:
        print(e)
        return jsonify({"code":404, "message": "fail!", "datas": None})
    
@bp.route('/A17/',methods=["POST"])
@captcha__is_login
def A17():   #闭运算
    try:
        img=request.form.get('data')
        head,context=img.split(",")
        img_data = base64.b64decode(context)
        image = Image.open(BytesIO(img_data))
        image.save('static/images/{}'.format("A17.png"))
        img = cv2.imread('static/images/{}'.format("A17.png"),cv2.IMREAD_COLOR)
        b, g, r = cv2.split(img)
        img2 = cv2.merge([r, g, b])
        rows, cols = img.shape[:2]
        src = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, src = cv2.threshold(src, 102, 255, cv2.THRESH_BINARY)
        kernel = np.ones((10, 10), np.uint8)
        closed = cv2.morphologyEx(src, cv2.MORPH_CLOSE, kernel)
        cv2.imwrite('static/images/{}'.format("A17.png"),closed) 
        with open('static/images/{}'.format("A17.png"),'rb') as f:
            image_base64 = base64.b64encode(f.read())
        os.remove('static/images/{}'.format("A17.png")) 
        image_base64=str(image_base64,'utf-8')
        return jsonify({"code":200, "message": "success!", "datas": image_base64})
    except Exception as e:
        print(e)
        return jsonify({"code":404, "message": "fail!", "datas": None})