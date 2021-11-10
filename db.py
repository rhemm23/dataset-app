import psycopg2 as psql

class DB:
  def __init__(self):
    self.conn = psql.connect("dbname=capstone user=admin password=admin")

  def delete_data_set(self, id):
    cursor = self.conn.cursor()
    cursor.execute("""WITH deleted AS (DELETE FROM data_sets WHERE id = %s) SELECT COUNT(*) FROM deleted;""", (id,))
    del_cnt = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return del_cnt > 0

  def delete_data_set_entry(self, id):
    cursor = self.conn.cursor()
    cursor.execute("""WITH deleted AS (DELETE FROM data_set_entries WHERE id = %s) SELECT COUNT(*) FROM deleted;""", (id,))
    del_cnt = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return del_cnt > 0

  def delete_image(self, id):
    cursor = self.conn.cursor()
    cursor.execute("""WITH deleted AS (DELETE FROM images WHERE id = %s) SELECT COUNT(*) FROM deleted;""", (id,))
    del_cnt = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return del_cnt > 0

  def delete_cropped_image(self, id):
    cursor = self.conn.cursor()
    cursor.execute("""WITH deleted AS (DELETE FROM cropped_images WHERE id = %s) SELECT COUNT(*) FROM deleted;""", (id,))
    del_cnt = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return del_cnt > 0

  def delete_face(self, id):
    cursor = self.conn.cursor()
    cursor.execute("""WITH deleted AS (DELETE FROM faces WHERE id = %s) SELECT COUNT(*) FROM deleted;""", (id,))
    del_cnt = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return del_cnt > 0

  def delete_facial_landmark(self, id):
    cursor = self.conn.cursor()
    cursor.execute("""WITH deleted AS (DELETE FROM facial_landmarks WHERE id = %s) SELECT COUNT(*) FROM deleted;""", (id,))
    del_cnt = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return del_cnt > 0

  def insert_data_set(self, name):
    cursor = self.conn.cursor()
    cursor.execute("""INSERT INTO data_sets (name) VALUES (%s) RETURNING id;""", (name,))
    id = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return id

  def insert_data_set_entry(self, data_set_id, name):
    cursor = self.conn.cursor()
    cursor.execute("""INSERT INTO data_set_entries (data_set_id, name) VALUES (%s, %s) RETURNING id;""", (data_set_id, name))
    id = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return id

  def insert_image(self, data_set_entry_id, width, height, data):
    cursor = self.conn.cursor()
    cursor.execute("""INSERT INTO images (data_set_entry_id, width, height, data) VALUES (%s, %s, %s, %s) RETURNING id;""", (data_set_entry_id, width, height, data))
    id = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return id

  def insert_cropped_image(self, image_id, data):
    cursor = self.conn.cursor()
    cursor.execute("""INSERT INTO cropped_images (image_id, data) VALUES (%s, %s) RETURNING id;""", (image_id, data))
    id = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return id

  def insert_face(self, image_id, cropped_image_id, x0, y0, x1, y1):
    cursor = self.conn.cursor()
    cursor.execute("""INSERT INTO faces (image_id, cropped_image_id, x0, y0, x1, y1) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;""", (image_id, cropped_image_id, x0, y0, x1, y1))
    id = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return id

  def insert_facial_landmark(self, face_id, name, x, y):
    cursor = self.conn.cursor()
    cursor.execute("""INSERT INTO facial_landmarks (face_id, name, x, y) VALUES (%s, %s, %s, %s) RETURNING id;""", (face_id, name, x, y))
    id = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return id
