from flask.templating import render_template
from retinaface import RetinaFace
from PIL import Image, ImageDraw, UnidentifiedImageError

import psycopg2 as psql
import numpy as np
import tempfile
import pathlib
import flask
import PIL
import io

app = flask.Flask(__name__)
conn = psql.connect("dbname=capstone user=admin password=admin")

def get_data_set_entries(data_set_id):
  cursor = conn.cursor()
  cursor.execute("""SELECT id, name FROM data_set_entries WHERE data_set_id = %s ORDER BY id ASC;""", (data_set_id,))
  data_set_entries = cursor.fetchall()
  cursor.close()
  return data_set_entries

def insert_data_set_entry(data_set_id, image_id, name):
  cursor = conn.cursor()
  cursor.execute("""INSERT INTO data_set_entries (data_set_id, image_id, name) VALUES (%s, %s, %s) RETURNING id;""", (data_set_id, image_id, name))
  id = cursor.fetchone()[0]
  conn.commit()
  cursor.close()
  return id

def insert_cropped_image_face(cropped_image_id, face_id):
  cursor = conn.cursor()
  cursor.execute("""INSERT INTO cropped_image_faces (cropped_image_id, face_id) VALUES (%s, %s) RETURNING id;""", (cropped_image_id, face_id))
  id = cursor.fetchone()[0]
  conn.commit()
  cursor.close()
  return id

def insert_image_face(image_id, face_id):
  cursor = conn.cursor()
  cursor.execute("""INSERT INTO image_faces (image_id, face_id) VALUES (%s, %s) RETURNING id;""", (image_id, face_id))
  id = cursor.fetchone()[0]
  conn.commit()
  cursor.close()
  return id

def insert_facial_landmark(face_id, name, x, y):
  cursor = conn.cursor()
  cursor.execute("""INSERT INTO facial_landmarks (face_id, name, x, y) VALUES (%s, %s, %s, %s) RETURNING id;""", (face_id, name, x, y))
  id = cursor.fetchone()[0]
  conn.commit()
  cursor.close()
  return id

def insert_face(x0, y0, x1, y1):
  cursor = conn.cursor()
  cursor.execute("""INSERT INTO faces (x0, y0, x1, y1) VALUES (%s, %s, %s, %s) RETURNING id;""", (x0, y0, x1, y1))
  id = cursor.fetchone()[0]
  conn.commit()
  cursor.close()
  return id

def insert_cropped_image(image_id, data):
  cursor = conn.cursor()
  cursor.execute("""INSERT INTO cropped_images (image_id, data) VALUES (%s, %s) RETURNING id;""",(image_id, data))
  id = cursor.fetchone()[0]
  conn.commit()
  cursor.close()
  return id

def insert_image(width, height, data):
  cursor = conn.cursor()
  cursor.execute("""INSERT INTO images (width, height, data) VALUES (%s, %s, %s) RETURNING id;""",(width, height, data))
  id = cursor.fetchone()[0]
  conn.commit()
  cursor.close()
  return id

def update_data_set_entry(id, name):
  cursor = conn.cursor()
  cursor.execute("""WITH updated AS (UPDATE data_set_entries SET name = %s WHERE id = %s RETURNING *) SELECT COUNT(*) FROM updated;""", (name, id))
  upd_cnt = cursor.fetchone()[0]
  conn.commit()
  cursor.close()
  return upd_cnt > 0

def delete_data_set_entry(id):
  cursor = conn.cursor()
  cursor.execute("""SELECT image_id, ci.id FROM data_set_entries AS dse INNER JOIN cropped_images AS ci ON dse.image_id = ci.image_id WHERE dse.id = %s;""", (id,))
  image_ids = cursor.fetchone()
  if image_ids is None:
    return False
  cursor.execute("""DELETE FROM data_set_entries WHERE id = %s;""", (id,))
  cursor.execute("""SELECT face_id FROM image_faces WHERE image_id = %s;""", (image_ids[0],))
  records = cursor.fetchall()
  face_ids = [record[0] for record in records]
  cursor.execute("""SELECT face_id FROM cropped_image_faces WHERE cropped_image_id = %s;""", (image_ids[1],))
  records = cursor.fetchall()
  face_ids += [record[0] for record in records]
  cursor.execute("""DELETE FROM faces WHERE id IN %s;""", (face_ids,))
  cursor.execute("""DELETE FROM images WHERE id = %s;""", (image_ids[0],))
  cursor.execute("""DELETE FROM cropped_images WHERE id = %s;""", (image_ids[1],))
  conn.commit()
  cursor.close()
  return True

def get_image(id):
  cursor = conn.cursor()
  cursor.execute("""SELECT width, height, data FROM images WHERE id = %s;""", (id,))
  image = cursor.fetchone()
  cursor.execute("""SELECT f.x0, f.y0, f.x1, f.y1 FROM image_faces AS imf INNER JOIN faces AS f ON imf.face_id = f.id WHERE imf.image_id = %s;""", (id,))
  bboxes = cursor.fetchall()
  cursor.close()
  return image, bboxes

def get_data_set_entry(id):
  cursor = conn.cursor()
  cursor.execute("""SELECT dse.name, dse.image_id, img.width, img.height FROM data_set_entries AS dse INNER JOIN images AS img ON dse.image_id = img.id WHERE dse.id = %s;""", (id,))
  data_set = cursor.fetchone()
  cursor.close()
  return data_set

def get_data_set(id):
  cursor = conn.cursor()
  cursor.execute("""SELECT id, name FROM data_sets WHERE id = %s;""", (id,))
  data_set = cursor.fetchone()
  cursor.close()
  return data_set

def update_data_set(id, name):
  cursor = conn.cursor()
  cursor.execute("""WITH updated AS (UPDATE data_sets SET name = %s WHERE id = %s RETURNING *) SELECT COUNT(*) FROM updated;""", (name, id))
  upd_cnt = cursor.fetchone()[0]
  conn.commit()
  cursor.close()
  return upd_cnt > 0

def insert_data_set(name):
  cursor = conn.cursor()
  cursor.execute("""INSERT INTO data_sets (name) VALUES (%s) RETURNING id;""", (name,))
  id = cursor.fetchone()[0]
  conn.commit()
  cursor.close()
  return id

def delete_data_set(id):
  cursor = conn.cursor()
  cursor.execute("""WITH deleted AS (DELETE FROM data_sets WHERE id = %s RETURNING *) SELECT COUNT(*) FROM deleted;""", (id,))
  del_cnt = cursor.fetchone()[0]
  conn.commit()
  cursor.close()
  return del_cnt > 0

def get_data_set_count():
  cursor = conn.cursor()
  cursor.execute("""SELECT COUNT(*) FROM data_sets;""")
  data_set_count = cursor.fetchone()[0]
  cursor.close()
  return data_set_count

def get_data_sets():
  cursor = conn.cursor()
  cursor.execute("""SELECT id, name FROM data_sets ORDER BY id ASC;""")
  data_sets = cursor.fetchall()
  cursor.close()
  return data_sets

def ok(data=None):
  res = {
    'status': 'success',
  }
  if data is not None:
    res['data'] = data
  return flask.jsonify(res), 200

def err(errors=None):
  res = {
    'status': 'failed'
  }
  if errors is not None:
    if isinstance(errors, list):
      res['errors'] = errors
    else:
      res['errors'] = [errors]
  return flask.jsonify(res), 400

def process_pil_image(data_set_id, name, image):
  image = image.convert('RGB')
  width, height = image.size

  image_data = np.asarray(image).tobytes()
  image_id = insert_image(width, height, image_data)

  temp_file = tempfile.NamedTemporaryFile()
  image.save(temp_file, 'PNG')
  temp_file.seek(0)

  faces = RetinaFace.detect_faces(temp_file.name)

  max_x = float('-inf')
  max_y = float('-inf')

  min_x = float('inf')
  min_y = float('inf')

  for face in faces:

    x0 = int(faces[face]['facial_area'][0])
    y0 = int(faces[face]['facial_area'][1])
    x1 = int(faces[face]['facial_area'][2])
    y1 = int(faces[face]['facial_area'][3])

    max_x = max(max_x, x1)
    max_y = max(max_y, y1)

    min_x = min(min_x, x0)
    min_y = min(min_y, y0)

    face_id = insert_face(x0, y0, x1, y1)

    for landmark in faces[face]['landmarks']:

      x = int(faces[face]['landmarks'][landmark][0])
      y = int(faces[face]['landmarks'][landmark][0])

      insert_facial_landmark(face_id, landmark, x, y)

    insert_image_face(image_id, face_id)

  scale = 300 / width
  if width > height:
    scale = 300 / height

  scl_x0 = int(min_x * scale)
  scl_y0 = int(min_y * scale)

  scl_x1 = int(max_x * scale)
  scl_y1 = int(max_y * scale)

  res_width = 300
  res_height = 300

  crop_offset_x = 0
  crop_offset_y = 0

  if width > height:
    res_width = int(width * scale)
    crop_offset_x = min(res_width - 300, scl_x0)
  elif height > width:
    res_width = int(height * scale)
    crop_offset_y = min(res_height - 300, scl_y0)

  cropped_image = image.resize((res_width, res_height))
  cropped_image = cropped_image.crop((crop_offset_x, crop_offset_y, crop_offset_x + 300, crop_offset_y + 300))
  cropped_image = cropped_image.convert('L')

  cropped_image_data = np.asarray(image).tobytes()
  cropped_image_id = insert_cropped_image(image_id, cropped_image_data)

  for face in faces:

    x0 = int(faces[face]['facial_area'][0] * scale) - crop_offset_x
    y0 = int(faces[face]['facial_area'][1] * scale) - crop_offset_y
    x1 = int(faces[face]['facial_area'][2] * scale) - crop_offset_x
    y1 = int(faces[face]['facial_area'][3] * scale) - crop_offset_y

    face_id = insert_face(x0, y0, x1, y1)

    for landmark in faces[face]['landmarks']:

      x = int(faces[face]['landmarks'][landmark][0] * scale) - crop_offset_x
      y = int(faces[face]['landmarks'][landmark][1] * scale) - crop_offset_y

      insert_facial_landmark(face_id, landmark, x, y)

    insert_cropped_image_face(cropped_image_id, face_id)

  return insert_data_set_entry(data_set_id, image_id, name)

@app.before_request
def handle_chunking():
  transfer_encoding = flask.request.headers.get("Transfer-Encoding", None)
  if transfer_encoding == u"chunked":
    flask.request.environ["wsgi.input_terminated"] = True

@app.route('/images/<int:id>', methods=['GET'])
def image(id):
  image, bboxes = get_image(id)
  if image is None:
    flask.abort(404)
  else:
    image_arr = np.frombuffer(image[2], dtype=np.uint8).reshape((image[0], image[1], 3))
    image_pil = Image.fromarray(image_arr, mode='RGB')
    image_drw = ImageDraw.Draw(image_pil)

    for bbox in bboxes:
      image_drw.rectangle(bbox, outline='red', width=10)

    image_io = io.BytesIO()
    image_pil.save(image_io, 'PNG')
    image_io.seek(0)

    return flask.send_file(image_io, mimetype='image/png')

@app.route('/data-set-entries/<int:id>', methods=['GET', 'DELETE', 'POST'])
def data_set_entry(id):
  if flask.request.method == 'DELETE':
    if delete_data_set_entry(id):
      return ok()
    else:
      return err('Data set entry does not exist')
  elif flask.request.method == 'POST':
    name = flask.request.form['name']
    if name is None or name == '':
      return err('Invalid name parameter')
    else:
      if update_data_set_entry(id, name):
        return ok({
          'id': id,
          'name': name
        })
      else:
        return err('Data set entry does not exist')
  else:
    data_set_entry = get_data_set_entry(id)
    if data_set_entry is None:
      flask.abort(404)
    else:
      return render_template(
        'data_set_entry.html',
        title='Data Set Entry - {}'.format(data_set_entry[0]),
        image_id=data_set_entry[1],
        width=data_set_entry[2],
        height=data_set_entry[3]
      )

@app.route('/data-sets/<int:id>/upload', methods=['POST'])
def data_set_upload(id):
  image = flask.request.files['image']
  if image is None:
    return err('Missing image file')
  else:
    path = pathlib.Path(image.filename)
    if path.suffix not in ['.png', '.jpeg']:
      return err('Invalid file extension')
    else:
      try:
        pil_image = Image.open(image)
        id = process_pil_image(id, path.stem, pil_image)
        return ok({
          'id': id,
          'name': path.stem
        })

      except UnidentifiedImageError:
        return err('Invalid image file')

@app.route('/data-sets/<int:id>', methods=['GET', 'DELETE', 'POST'])
def data_set(id):
  if flask.request.method == 'DELETE':
    if delete_data_set(id):
      return ok()
    else:
      return err('Data set does not exist')
  elif flask.request.method == 'POST':
    name = flask.request.form['name']
    if name is None or name == '':
      return err('Invalid name parameter')
    else:
      if update_data_set(id, name):
        return ok({
          'id': id,
          'name': name
        })
      else:
        return err('Data set does not exist')
  else:
    data_set = get_data_set(id)
    if data_set is None:
      flask.abort(404)
    else:
      return render_template(
        'data_set.html',
        title='Data Set - {}'.format(data_set[1]),
        data_set_entries=get_data_set_entries(id),
        data_set_id=id
      )

@app.route('/data-sets', methods=['GET', 'POST'])
def data_sets():
  if flask.request.method == 'POST':
    name = flask.request.form['name']
    if name is None or name == '':
      return err('Invalid name parameter')
    else:
      id = insert_data_set(name)
      return ok({ 'id': id })
  else:
    return flask.render_template(
      'data_sets.html',
      title='Data Sets',
      data_sets=get_data_sets()
    )

@app.route('/')
def index():
  return flask.render_template(
    'index.html',
    title='Dataset Manager',
    data_set_count=get_data_set_count()
  )

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=5000)

