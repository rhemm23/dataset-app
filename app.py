from flask import Flask, render_template

import psycopg2 as psql

app = Flask(__name__)
conn = psql.connect("dbname=capstone user=admin password=admin")

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

@app.route('/data-sets')
def data_sets():
  return render_template(
    'data_sets.html',
    title='Data Sets',
    data_sets=get_data_sets()
  )

@app.route('/')
def index():
  return render_template(
    'index.html',
    title='Dataset Manager',
    data_set_count=get_data_set_count()
  )

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=5000)

