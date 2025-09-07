import qrcode
import hashlib
from io import BytesIO


def generate_qrcode(partner, user_fullname, points, save_path=None):
    text = f"{partner}{user_fullname}{points}"
    hexdigest = hashlib.md5(text.encode("utf-8")).hexdigest()

    img = qrcode.make(hexdigest)

    if save_path:
        img.save(save_path)
        return save_path
    else:
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

print(generate_qrcode('papajons', 'badimcan', "5000", save_path="reward_qr.png"))