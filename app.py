import psycopg2 as psql
import flask

app = flask.Flask(__name__)
conn = psql.connect("dbname=capstone user=admin password=admin")

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
      flask.flash('Successfully deleted data set', 'success')
    else:
      flask.flash('Failed to delete data set, it does not exist', 'error')
    flask.redirect('/')
  else:
    flask.redirect('/')


@app.route('/data-sets')
def data_sets():
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

