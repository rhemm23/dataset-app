from flask.templating import render_template
import psycopg2 as psql
import flask

app = flask.Flask(__name__)
conn = psql.connect("dbname=capstone user=admin password=admin")

def get_data_set(id):
  cursor = conn.cursor()
  cursor.execute("""SELECT id, name FROM data_sets WHERE id = %s;""", (id,))
  data_set = cursor.fetchone()
  cursor.close()
  return data_set

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

@app.route('/data-sets/<int:id>', methods=['GET', 'DELETE'])
def data_set(id):
  if flask.request.method == 'DELETE':
    if delete_data_set(id):
      res = {
        'status': 'success'
      }
      return flask.jsonify(res), 200
    else:
      res = {
        'status': 'failed',
        'errors': [
          'Data set does not exist'
        ]
      }
      return flask.jsonify(res), 400
  else:
    data_set = get_data_set(id)
    if data_set is None:
      flask.abort(404)
    else:
      return render_template(
        'data_set.html',
        title=data_set[1]
      )

@app.route('/data-sets', methods=['GET', 'POST'])
def data_sets():
  if flask.request.method == 'POST':
    name = flask.request.form['name']
    if name is None or name == '':
      res = {
        'status': 'failed',
        'errors': [
          'Invalid name parameter'
        ]
      }
      return flask.jsonify(res), 400
    else:
      id = insert_data_set(name)
      res = {
        'status': 'success',
        'data': {
          'id': id
        }
      }
      return flask.jsonify(res), 200
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

