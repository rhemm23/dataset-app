from flask import render_template, abort
from app import app
from db import DB

db = DB()

# Website index
@app.route('/', methods=['GET'])
def index():
  return render_template(
    'index.html',
    title='Data Set Manager',
    data_set_count=db.data_set_count()
  )

# View data sets
@app.route('/data-sets', methods=['GET'])
def view_data_sets():
  return render_template(
    'data_sets.html',
    title='Data Sets',
    data_sets=db.get_data_sets()
  )

# View a data set
@app.route('/data-sets/<int:id>', methods=['GET'])
def view_data_set(id):
  data_set = db.get_data_set(id)
  if not data_set:
    abort(404)
  return render_template(
    'data_set.html',
    title='Data Set - {}'.format(data_set[1]),
    data_set_entries=db.get_data_set_entries(id),
    data_set_id=id
  )

# View a data set entry
@app.route('/data-set-entries/<int:id>', methods=['GET'])
def view_data_set_entry(id):
  data_set_entry = db.get_data_set_entry(id)
  if not data_set_entry:
    abort(404)
  return render_template(
    'data_set_entry.html',
    title='Data Set Entry - {}'.format(data_set_entry[0]),
    image_id=data_set_entry[1],
    width=data_set_entry[2],
    height=data_set_entry[3],
    cropped_image_id=data_set_entry[4]
  )
