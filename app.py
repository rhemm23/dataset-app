from flask.templating import render_template
from retinaface import RetinaFace
from image import ImageProcessor
from PIL import Image, ImageDraw, UnidentifiedImageError, ImageOps

import psycopg2 as psql
import numpy as np
import tempfile
import pathlib
import flask
import PIL
import io

app = flask.Flask(__name__)

# API routes
import api

# Dynamic content
import dyn

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
        cropped_image_id=data_set_entry[4],
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

