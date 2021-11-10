from flask import Flask, render_template

import psycopg2 as psql

app = Flask(__name__)
conn = psql.connect("dbname=faces user=admin password=admin")

def get_image_count():
  cursor = conn.cursor()
  cursor.execute("""SELECT COUNT(*) FROM images;""")
  count = cursor.fetchone()[0]
  cursor.close()
  return count

@app.route('/original-images')
def original_images():
  return render_template(
    'original_images.html',
    title='Original Images'
  )

@app.route('/')
def index():
    return render_template(
      'index.html',
      title='Dataset Manager',
      image_count=get_image_count()
    )

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)

