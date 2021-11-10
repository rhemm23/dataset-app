from flask import Flask, render_template, request

import psycopg2 as psql
import math

app = Flask(__name__)
conn = psql.connect("dbname=faces user=admin password=admin")

def get_image_count():
  cursor = conn.cursor()
  cursor.execute("""SELECT COUNT(*) FROM images;""")
  count = cursor.fetchone()[0]
  cursor.close()
  return count

def get_original_images(page):
  cursor = conn.cursor()
  cursor.execute("""SELECT id, width, height, google_file_name FROM images ORDER BY id asc LIMIT 50 OFFSET %s;""", (page * 50,))
  images = cursor.fetchall()
  cursor.close()
  return images

@app.route('/original-images')
def original_images():

  # Determine page number
  page = request.args.get('page')
  if page is None:
    page = 0
  else:
    try:
      page = int(page)
    except:
      page = 0

  image_count = get_image_count()
  page_count = math.ceil(image_count / 50)

  if page >= page_count:
    page = page_count - 1
  elif page < 0:
    page = 0

  images = get_original_images(page)

  return render_template(
    'original_images.html',
    title='Original Images',
    page=page,
    images=images,
    page_count=page_count
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

