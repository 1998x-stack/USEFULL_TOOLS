"""QR code generation and reading."""

import os
from typing import Optional


def generate_qr(data: str, output: str, size: int = 300) -> str:
    try:
        import qrcode
    except ImportError:
        raise ImportError("qrcode is required: pip install devkit-tools[web]")
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size))
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    img.save(output)
    return output


def read_qr(image_path: str) -> Optional[str]:
    try:
        from PIL import Image
        from pyzbar.pyzbar import decode
    except ImportError:
        raise ImportError("pyzbar and Pillow required: pip install devkit-tools[web]")
    img = Image.open(image_path)
    decoded = decode(img)
    if decoded:
        return decoded[0].data.decode("utf-8")
    return None
