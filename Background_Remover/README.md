# Clearcut Background Remover

A local Flask app that removes image backgrounds and returns transparent PNGs.

## Run

From this folder, install the dependencies and start the app:

```sh
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. On the first removal, `rembg` downloads its segmentation model; an internet connection is needed for that initial setup. The model is then reused while the app is running.

The app accepts JPG, PNG, WebP, HEIC/HEIF, TIFF, GIF, and BMP images up to 12 MB and 40 megapixels. Uploaded and processed images are held in memory and are not written to disk.