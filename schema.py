import psycopg2 as psql

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn = psql.connect("dbname=postgres user=admin password=admin")
cursor = conn.cursor()

conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

cursor.execute("DROP DATABASE IF EXISTS capstone;")
cursor.execute("CREATE DATABASE capstone OWNER admin;")

cursor.close()
conn.close()

db_conn = psql.connect("dbname=capstone user=admin password=admin")
db_cursor = db_conn.cursor()

db_cursor.execute(
  """
  CREATE TABLE data_sets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL
  );
  """
)
db_cursor.execute(
  """
  CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    data BYTEA NOT NULL
  );
  """
)
db_cursor.execute(
  """
  CREATE TABLE data_set_entries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    data_set_id INTEGER NOT NULL,
    image_id INTEGER NOT NULL,
    CONSTRAINT fk_images_data_set_entries FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
    CONSTRAINT fk_data_sets_data_set_entries FOREIGN KEY (data_set_id) REFERENCES data_sets(id) ON DELETE CASCADE
  );
  """
)
db_cursor.execute(
  """
  CREATE TABLE cropped_images (
    id SERIAL PRIMARY KEY,
    image_id INTEGER NOT NULL,
    data BYTEA NOT NULL,
    CONSTRAINT fk_images_cropped_images FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
  );
  """
)
db_cursor.execute(
  """
  CREATE TABLE faces (
    id SERIAL PRIMARY KEY,
    x0 INTEGER NOT NULL,
    y0 INTEGER NOT NULL,
    x1 INTEGER NOT NULL,
    y1 INTEGER NOT NULL
  );
  """
)
db_cursor.execute(
  """
  CREATE TABLE facial_landmarks (
    id SERIAL PRIMARY KEY,
    face_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    CONSTRAINT fk_faces_facial_landmarks FOREIGN KEY (face_id) REFERENCES faces(id) ON DELETE CASCADE
  );
  """
)
db_cursor.execute(
  """
  CREATE TABLE image_faces (
    id SERIAL PRIMARY KEY,
    face_id INTEGER NOT NULL,
    image_id INTEGER NOT NULL,
    CONSTRAINT fk_faces_image_faces FOREIGN KEY (face_id) REFERENCES faces(id) ON DELETE CASCADE,
    CONSTRAINT fk_images_image_faces FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
  );
  """
)
db_cursor.execute(
  """
  CREATE TABLE cropped_image_faces (
    id SERIAL PRIMARY KEY,
    face_id INTEGER NOT NULL,
    cropped_image_id INTEGER NOT NULL,
    CONSTRAINT fk_faces_image_faces FOREIGN KEY (face_id) REFERENCES faces(id) ON DELETE CASCADE,
    CONSTRAINT fk_cropped_images_image_faces FOREIGN KEY (cropped_image_id) REFERENCES cropped_images(id) ON DELETE CASCADE
  );
  """
)

db_conn.commit()
db_cursor.close()
db_conn.close()
