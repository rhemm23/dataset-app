from flask import abort, send_file
from __main__ import app
from PIL import Image, ImageDraw
from db import DB
import io

import numpy as np

db = DB()

# Converts a PIL image to a response
def serve_pil_image(image):
  image_io = io.BytesIO()
  image.save(image_io, 'PNG')
  image_io.seek(0)
  return send_file(image_io, mimetype='image/png')

# Displays an image with face bounding boxes
@app.route('/images/<int:id>', methods=['GET'])
def serve_image(id):
  image = db.get_image(id)
  if not image:
    abort(404)
  image_pixels = np.frombuffer(image[3], dtype=np.uint8).reshape((image[2], image[1], 3))
  image_pil = Image.fromarray(image_pixels, mode='RGB')
  image_draw = ImageDraw.Draw(image_pil)
  faces = db.get_image_faces(id)

  for face in faces:
    image_draw.rectangle(face, outline='red', width=10)

  return serve_pil_image(image_pil)

# Displays a cropped image with face bounding boxes
@app.route('/cropped-images/<int:id>', methods=['GET'])
def serve_cropped_image(id):
  cropped_image = db.get_cropped_image(id)
  if not cropped_image:
    abort(404)
  cropped_image_pixels = np.frombuffer(cropped_image[1], dtype=np.uint8).reshape((300, 300))
  cropped_image_pil = Image.fromarray(cropped_image_pixels, mode='L')
  cropped_image_draw = ImageDraw.Draw(cropped_image_pil)
  faces = db.get_cropped_image_faces(id)

  for face in faces:
    cropped_image_draw.rectangle(face, outline='black', width=3)

  return serve_pil_image(cropped_image_pil)

