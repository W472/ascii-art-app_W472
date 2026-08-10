from flask import Flask, request, jsonify
from PIL import Image
import io
import os

app = Flask(__name__)

# 字符集：从深到浅（密度从高到低）
ASCII_CHARS = "@%#*+=-:. "

def resize_image(image, new_width=100):
    """
    按比例缩放图片，保持宽高比，宽度固定为 new_width，
    高度根据字符的宽高比调整（通常字符高度约是宽度的2倍，所以高度缩小为一半）。
    """
    width, height = image.size
    aspect_ratio = height / width
    # 字符在终端中通常高是宽的2倍，因此高度换算时乘以0.5
    new_height = int(aspect_ratio * new_width * 0.5)
    resized_image = image.resize((new_width, new_height))
    return resized_image

def grayify(image):
    """将图片转为灰度图"""
    return image.convert("L")

def pixels_to_ascii(image):
    """将灰度图的每个像素映射到字符"""
    pixels = image.getdata()
    # 灰度值 0-255，映射到字符集索引 (0-9)，共10个字符
    characters = "".join([ASCII_CHARS[pixel // 26] for pixel in pixels])
    return characters

def image_to_ascii(image_path, new_width=100):
    """完整的图片转字符画流程"""
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"无法打开图片: {e}")
        return None

    # 1. 缩放
    image = resize_image(image, new_width)
    # 2. 灰度化
    image = grayify(image)
    # 3. 像素映射为字符
    ascii_str = pixels_to_ascii(image)
    
    # 按图片宽度拼接字符串，形成多行文本
    img_width = image.width
    ascii_str_len = len(ascii_str)
    ascii_img = "\n".join(
        ascii_str[i:(i + img_width)] for i in range(0, ascii_str_len, img_width)
    )
    return ascii_img

@app.route('/')
def index():
    return "图片转字符画后端已运行！请访问前端页面。"

@app.route('/upload', methods=['POST'])
def upload():
    """接收上传的图片，返回字符画 JSON"""
    if 'image' not in request.files:
        return jsonify({"error": "没有图片文件"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "文件名为空"}), 400
    
    # 保存临时文件
    temp_path = "temp_upload.jpg"
    file.save(temp_path)
    
    # 生成字符画
    ascii_art = image_to_ascii(temp_path, new_width=100)
    
    # 删除临时文件
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    if ascii_art is None:
        return jsonify({"error": "图片处理失败"}), 500
    
    # 终端显示艺术字（关键！）
    print("\n" + "="*60)
    print("🎨 生成的字符画：")
    print(ascii_art)
    print("="*60 + "\n")
    
    return jsonify({"ascii": ascii_art})

if __name__ == '__main__':
    # 启动 Flask 应用，监听 5000 端口
    app.run(debug=True, host='0.0.0.0', port=5000)