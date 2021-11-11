from flask import request, jsonify
from image import ImageProcessor
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from app import app
from db import DB

db = DB()

# General API success
def api_success(data=None):
  if data:
    return jsonify(data), 200
  else:
    return '', 204

# General API error
def api_error(message):
  result = { 'error': message }
  return jsonify(result), 400

# Create data set
@app.route('/data-sets', methods=['POST'])
def create_data_set():
  name = request.form['name']
  if not name:
    return api_error('Invalid name')
  return api_success({ 'id': db.insert_data_set(name) })

# Delete data set
@app.route('/data-sets/<int:id>', methods=['DELETE'])
def delete_data_set(id):
  if db.delete_data_set(id):
    return api_success()
  else:
    return api_error('Data set does not exist')

# Update data set name
@app.route('/data-sets/<int:id>', methods=['POST'])
def update_data_set(id):
  name = request.form['name']
  if not name:
    return api_error('Invalid name')
  if db.update_data_set(id, name):
    return api_success()
  else:
    return api_error('Data set does not exist')

# Delete data set entry
@app.route('/data-set-entries/<int:id>', methods=['DELETE'])
def delete_data_set_entry(id):
  if db.delete_data_set_entry(id):
    return api_success()
  else:
    return api_error('Data set entry does not exist')

# Update data set entry name
@app.route('/data-set-entries/<int:id>', methods=['POST'])
def update_data_set_entry(id):
  name = request.form['name']
  if not name:
    return api_error('Invalid name')
  if db.update_data_set_entry(id, name):
    return api_success()
  else:
    return api_error('Data set entry does not exist')

# Upload an image to a data set
@app.route('/data-sets/<int:id>/upload', methods=['POST'])
def upload_image_to_data_set(id):
  image = request.files['image']
  if not image:
    return api_error('Missing image')
  path = Path(image.filename)
  if path.suffix not in ['.png', '.jpeg', '.jpg']:
    return api_error('Invalid image type')
  if not db.does_data_set_exist(id):
    return api_error('Data set does not exist')
  try:
    image = Image.open(image)
    image_processor = ImageProcessor(image)
    data_set_entry_id = image_processor.process_data_set_entry(id, path.stem)
    return api_success({ 'id': data_set_entry_id })
  except UnidentifiedImageError:
    return api_error('Invalid image')