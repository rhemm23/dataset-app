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
  CREATE TABLE data_set_entries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    data_set_id INTEGER NOT NULL,
    CONSTRAINT fk_data_sets_data_set_entries FOREIGN KEY (data_set_id) REFERENCES data_sets(id) ON DELETE CASCADE
  );
  """
)
db_cursor.execute(
  """
  CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    data_set_entry_id INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    data BYTEA NOT NULL,
    CONSTRAINT fk_data_set_entries_images FOREIGN KEY (data_set_entry_id) REFERENCES data_set_entries(id) ON DELETE CASCADE
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
  CREATE TABLE sub_images (
    id SERIAL PRIMARY KEY,
    cropped_image_id INTEGER NOT NULL,
    scale NUMERIC NOT NULL,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    data BYTEA NOT NULL,
    is_face BOOLEAN NOT NULL DEFAULT FALSE,
    rotation NUMERIC NOT NULL DEFAULT 0,
    CONSTRAINT fk_cropped_images_sub_images FOREIGN KEY (cropped_image_id) REFERENCES cropped_images(id) ON DELETE CASCADE
  );
  """
)
db_cursor.execute(
  """
  CREATE TABLE faces (
    id SERIAL PRIMARY KEY,
    image_id INTEGER,
    cropped_image_id INTEGER,
    x0 INTEGER NOT NULL,
    y0 INTEGER NOT NULL,
    x1 INTEGER NOT NULL,
    y1 INTEGER NOT NULL,
    CONSTRAINT fk_images_faces FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
    CONSTRAINT fk_cropped_images_faces FOREIGN KEY (cropped_image_id) REFERENCES cropped_images(id) ON DELETE CASCADE
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

db_conn.commit()
db_cursor.close()
db_conn.close()
