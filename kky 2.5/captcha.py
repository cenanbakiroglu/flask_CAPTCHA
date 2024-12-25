from flask import Flask, session, request, render_template, make_response
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random

app = Flask(__name__)
app.secret_key = "gizli_anahtar"  # Oturum için gizli anahtar

@app.route("/captcha")
def captcha():
    # Resim boyutu
    width, height = 150, 50
    # Resim oluşturma (koyu gri arka plan)
    image = Image.new("RGB", (width, height), (30, 30, 30))  # Koyu gri arka plan
    draw = ImageDraw.Draw(image)

    # Çizgiler ekleme (parlak çizgiler, sarı veya açık mavi)
    for _ in range(20):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=(128,128,128), width=2)  # Açık mavi çizgiler

   # Karakter havuzu (rakamlar ve harfler)
    chars=("Q","W","E","R","T","Y","U","I","O","P","Ğ","Ü","A","S","D","F","G","H","J","K","L","Ş","İ","Z","X","C","V","B","N","M","Ö","Ç",
           "q","w","e","r","t","y","u","ı","o","p","ğ","ü","a","s","d","f","g","h","j","k","l","ş","i","z","x","c","v","b","n","m","ö","ç",
           "0","1","2","3","4","5","6","7","8","9")
    # CAPTCHA metni oluşturma
    captcha_text=""
    for i in range(6):
        captcha_text+=chars[random.randint(0,len(chars)-1)]
    font = ImageFont.truetype("arial.ttf", 24)

    # CAPTCHA metnini çizme (parlak yazı rengi: beyaz)
    for i, char in enumerate(captcha_text):
        x = 20 + i * 20
        y = random.randint(5, 15)
        draw.text((x, y), char, fill=(255, 255, 255), font=font)  # Beyaz yazı rengi

    # Sayıları oturuma kaydetme
    session["captcha"] = captcha_text

    # Resmi tarayıcıya gönderme
    buffer = BytesIO()
    image.save(buffer, "PNG")
    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers["Content-Type"] = "image/png"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/verify", methods=["POST"])
def verify():
    user_input = request.form.get("captcha")
    if user_input == session.get("captcha"):
        return "Doğru CAPTCHA!"
    else:
        return "Hatalı CAPTCHA!"


if __name__ == "__main__":
    app.run(debug=True)
