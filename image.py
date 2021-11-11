from retinaface import RetinaFace
from db import DB

import numpy as np
import tempfile
import math

db = DB()

class ImageProcessor:
  def __init__(self, pil_image):
    self.pil_image = pil_image

  def process_data_set_entry(self, data_set_id, name):
    data_set_entry_id = db.insert_data_set_entry(data_set_id, name)
    self.process_image(data_set_entry_id)
    return data_set_entry_id

  def process_image(self, data_set_entry_id):
    image = self.pil_image.convert('RGB')
    width, height = image.size

    image_data = np.asarray(image).tobytes()
    image_id = db.insert_image(data_set_entry_id, width, height, image_data)

    temp_file = tempfile.NamedTemporaryFile()
    image.save(temp_file, 'PNG')
    temp_file.seek(0)

    faces = RetinaFace.detect_faces(temp_file.name)

    temp_file.close()

    min_x = float('inf')
    min_y = float('inf')

    for face in faces:

      x0 = int(faces[face]['facial_area'][0])
      y0 = int(faces[face]['facial_area'][1])
      x1 = int(faces[face]['facial_area'][2])
      y1 = int(faces[face]['facial_area'][3])

      min_x = min(min_x, x0)
      min_y = min(min_y, y0)

      face_id = db.insert_face(image_id, None, x0, y0, x1, y1)

      for landmark in faces[face]['landmarks']:

        x = int(faces[face]['landmarks'][landmark][0])
        y = int(faces[face]['landmarks'][landmark][0])

        db.insert_facial_landmark(face_id, landmark, x, y)

    scale = 300 / width
    if width > height:
      scale = 300 / height

    scl_x0 = int(min_x * scale)
    scl_y0 = int(min_y * scale)

    res_width = 300
    res_height = 300

    crop_offset_x = 0
    crop_offset_y = 0

    if width > height:
      res_width = int(width * scale)
      crop_offset_x = min(res_width - 300, scl_x0)
    elif height > width:
      res_height = int(height * scale)
      crop_offset_y = min(res_height - 300, scl_y0)

    cropped_image = image.resize((res_width, res_height))
    cropped_image = cropped_image.crop((crop_offset_x, crop_offset_y, crop_offset_x + 300, crop_offset_y + 300))
    cropped_image = cropped_image.convert('L')

    cropped_image_data = np.asarray(cropped_image).tobytes()
    cropped_image_id = db.insert_cropped_image(image_id, cropped_image_data)

    # Tuple of bbox, sub_image_index, dist, rot
    cropped_bboxes = []

    for face in faces:

      x0 = int(faces[face]['facial_area'][0] * scale) - crop_offset_x
      y0 = int(faces[face]['facial_area'][1] * scale) - crop_offset_y
      x1 = int(faces[face]['facial_area'][2] * scale) - crop_offset_x
      y1 = int(faces[face]['facial_area'][3] * scale) - crop_offset_y

      if x0 < 0 or y0 < 0 or x1 >= 300 or y1 >= 300:
        continue

      face_id = db.insert_face(None, cropped_image_id, x0, y0, x1, y1)

      left_eye_x = 0
      left_eye_y = 0

      right_eye_x = 0
      right_eye_y = 0

      for landmark in faces[face]['landmarks']:

        x = int(faces[face]['landmarks'][landmark][0] * scale) - crop_offset_x
        y = int(faces[face]['landmarks'][landmark][1] * scale) - crop_offset_y

        if landmark == 'right_eye':
          right_eye_x = x
          right_eye_y = y
        elif landmark == 'left_eye':
          left_eye_x = x
          left_eye_y = y

        db.insert_facial_landmark(face_id, landmark, x, y)

      dx = abs(right_eye_x - left_eye_x)
      dy = abs(right_eye_y - left_eye_y)

      rot = math.atan2(dy, dx)
      cropped_bboxes.append([[x0, y0, x1, y1], -1, float('inf'), rot])

    # Compute sub images
    sizes = [
      300,
      240,
      180,
      120,
      60,
      20
    ]

    # [x, y], scale, data
    sub_images = []
    for size in sizes:
      scaled_image = cropped_image.resize((size, size))
      scale = size / 300
      for row in range(0, size, 20):
        for col in range(0, size, 20):

          x0 = col
          y0 = row
          x1 = col + 20
          y1 = row + 20

          sub_image = scaled_image.crop((x0, y0, x1, y1))
          sub_image_data = np.asarray(sub_image).tobytes()

          sub_images.append([[x0, y0], scale, sub_image_data])
          sub_image_index = len(sub_images) - 1

          scl_x0 = int(x0 / scale)
          scl_y0 = int(y0 / scale)
          scl_x1 = int(x1 / scale)
          scl_y1 = int(y1 / scale)

          for i in range(len(cropped_bboxes)):

            b_x0, b_y0, b_x1, b_y1 = cropped_bboxes[i][0]

            d1 = ((scl_x0 - b_x0)**2 + (scl_y0 - b_y0)**2)**0.5
            d2 = ((scl_x1 - b_x1)**2 + (scl_y1 - b_y1)**2)**0.5

            dist = max(d1, d2)

            if dist < cropped_bboxes[i][2]:
              cropped_bboxes[i][2] = dist
              cropped_bboxes[i][1] = sub_image_index

    rot_by_ind = {}
    for bbox in cropped_bboxes:
      rot_by_ind[bbox[1]] = bbox[3]

    for i in range(len(sub_images)):
      rot = 0
      is_face = False
      if i in rot_by_ind:
        is_face = True
        rot = rot_by_ind[i]
      sub_image = sub_images[i]
      db.insert_sub_image(
        cropped_image_id,
        sub_image[0][0],
        sub_image[0][1],
        sub_image[1],
        sub_image[2],
        is_face=is_face,
        rotation=rot
      )