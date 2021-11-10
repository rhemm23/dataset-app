from flask.templating import render_template
import psycopg2 as psql
import pathlib
import flask
import PIL

app = flask.Flask(__name__)
conn = psql.connect("dbname=capstone user=admin password=admin")

def update_data_set_entry(id, name):
  cursor = conn.cursor()
  cursor.execute("""WITH updated AS (UPDATE data_set_entries SET name = %s WHERE id = %s RETURNING *) SELECT COUNT(*) FROM updated;""", (name, id))
  upd_cnt = cursor.fetchone()[0]
  conn.commit()
  cursor.close()
  return upd_cnt > 0

def delete_data_set_entry(id):
  cursor = conn.cursor()
  cursor.execute("""WITH deleted AS (DELETE FROM data_set_entries WHERE id = %s RETURNING *) SELECT COUNT(*) FROM deleted;""", (id,))
  del_cnt = cursor.fetchone()[0]
  conn.commit()
  cursor.close()
  return del_cnt > 0

def get_data_set_entry(id):
  cursor = conn.cursor()
  cursor.execute("""SELECT id, name FROM data_set_entries WHERE id = %s;""", (id,))
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

def process_pil_image(image):
  print('test')

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
        title='Data Set Entry - {}'.format(data_set_entry[1])
      )

@app.route('/data-sets/<int:id>/upload', methods=['POST'])
def data_set_upload(id):
  image = flask.request.files['image']
  if image is None:
    return err('Missing image file')
  else:
    extension = pathlib.Path(image.filename).suffix
    if extension not in ['.png', '.jpeg']:
      return err('Invalid file extension')
    else:
      try:
        pil_image = PIL.Image.open(image)
        id = process_pil_image(pil_image)
        if id is not None:
          return ok()
        else:
          return err('Could not process image')

      except PIL.UnidentifiedImageError:
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

