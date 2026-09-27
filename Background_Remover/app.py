import io
import logging
import os
import threading

from flask import Flask, jsonify, render_template, request, send_file
from PIL import Image, ImageOps, UnidentifiedImageError
from pillow_heif import register_heif_opener

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024

MAX_IMAGE_PIXELS = 40_000_000
SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP", "BMP", "TIFF", "GIF", "HEIF", "AVIF"}
session_lock = threading.Lock()
rembg_session = None
register_heif_opener()


def prepare_image(image_data):
    try:
        with Image.open(io.BytesIO(image_data)) as source:
            if source.format not in SUPPORTED_FORMATS:
                raise ValueError("Choose a JPG, PNG, WebP, HEIC, TIFF, GIF, or BMP image.")
            if source.width * source.height > MAX_IMAGE_PIXELS:
                raise ValueError("This image is too large to process. Try one under 40 megapixels.")
            image = ImageOps.exif_transpose(source).convert("RGBA")
    except (UnidentifiedImageError, OSError) as error:
        raise ValueError("That file could not be read as an image.") from error

    normalized = io.BytesIO()
    image.save(normalized, format="PNG")
    return normalized.getvalue()


def get_rembg_session():
    global rembg_session
    if rembg_session is None:
        with session_lock:
            if rembg_session is None:
                from rembg import new_session

                rembg_session = new_session("u2net")
    return rembg_session


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/remove-background")
def remove_background():
    uploaded_file = request.files.get("image")
    if uploaded_file is None or not uploaded_file.filename:
        return jsonify(error="Choose an image to get started."), 400

    try:
        image_data = prepare_image(uploaded_file.read())
    except ValueError as error:
        return jsonify(error=str(error)), 400

    try:
        from rembg import remove

        result = remove(image_data, session=get_rembg_session())
    except Exception:
        app.logger.exception("Background removal failed")
        return jsonify(error="The image could not be processed. Check your connection on the first run and try again."), 500

    return send_file(
        io.BytesIO(result),
        mimetype="image/png",
        as_attachment=True,
        download_name="background-removed.png",
    )


@app.errorhandler(413)
def file_too_large(_error):
    return jsonify(error="That file is over the 12 MB upload limit."), 413


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)