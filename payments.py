import qrcode
import uuid
import os

def generate_qr(amount):
    os.makedirs("files", exist_ok=True)
    bill_id = uuid.uuid4().hex
    pay_url = f"https://qr.nspk.ru/TEST123456789?amount={amount}"

    img = qrcode.make(pay_url)
    path = f"files/qr_{bill_id}.png"
    img.save(path)
    return path