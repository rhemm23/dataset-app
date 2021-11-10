import psycopg2 as psql

class DB:
  def __init__(self):
    self.conn = psql.connect("dbname=capstone user=admin password=admin")

  def get_cropped_image_faces(self, id):
    cursor = self.conn.cursor()
    cursor.execute("""SELECT x0, y0, x1, y1 FROM faces WHERE cropped_image_id = %s;""", (id,))
    faces = cursor.fetchall()
    cursor.close()
    return faces

  def get_image_faces(self, id):
    cursor = self.conn.cursor()
    cursor.execute("""SELECT x0, y0, x1, y1 FROM faces WHERE image_id = %s;""", (id,))
    faces = cursor.fetchall()
    cursor.close()
    return faces

  def get_cropped_image(self, id):
    cursor = self.conn.cursor()
    cursor.execute("""SELECT image_id, data FROM cropped_images WHERE id = %s;""", (id,))
    cropped_image = cursor.fetchone()
    cursor.close()
    return cropped_image

  def get_image(self, id):
    cursor = self.conn.cursor()
    cursor.execute("""SELECT data_set_entry_id, width, height, data FROM images WHERE id = %s;""", (id,))
    image = cursor.fetchone()
    cursor.close()
    return image

  def does_data_set_exist(self, id):
    cursor = self.conn.cursor()
    cursor.execute("""SELECT EXISTS (SELECT 1 FROM data_sets WHERE id = %s);""", (id,))
    res = cursor.fetchone()[0]
    cursor.close()
    return res

  def update_data_set_entry(self, id, name):
    cursor = self.conn.cursor()
    cursor.execute("""WITH updated AS (UPDATE data_set_entries SET name = %s WHERE id = %s RETURNING *) SELECT COUNT(*) FROM updated;""", (name, id))
    upd_cnt = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return upd_cnt > 0

  def update_data_set(self, id, name):
    cursor = self.conn.cursor()
    cursor.execute("""WITH updated AS (UPDATE data_sets SET name = %s WHERE id = %s RETURNING *) SELECT COUNT(*) FROM updated;""", (name, id))
    upd_cnt = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return upd_cnt > 0

  def facial_landmark_count(self):
    cursor = self.conn.cursor()
    cursor.execute("""SELECT COUNT(*) FROM facial_landmarks;""")
    count = cursor.fetchone()[0]
    cursor.close()
    return count

  def face_count(self):
    cursor = self.conn.cursor()
    cursor.execute("""SELECT COUNT(*) FROM faces;""")
    count = cursor.fetchone()[0]
    cursor.close()
    return count

  def cropped_image_count(self):
    cursor = self.conn.cursor()
    cursor.execute("""SELECT COUNT(*) FROM cropped_images;""")
    count = cursor.fetchone()[0]
    cursor.close()
    return count

  def image_count(self):
    cursor = self.conn.cursor()
    cursor.execute("""SELECT COUNT(*) FROM images;""")
    count = cursor.fetchone()[0]
    cursor.close()
    return count

  def data_set_entry_count(self):
    cursor = self.conn.cursor()
    cursor.execute("""SELECT COUNT(*) FROM data_set_entries;""")
    count = cursor.fetchone()[0]
    cursor.close()
    return count

  def data_set_count(self):
    cursor = self.conn.cursor()
    cursor.execute("""SELECT COUNT(*) FROM data_sets;""")
    count = cursor.fetchone()[0]
    cursor.close()
    return count

  def delete_data_set(self, id):
    cursor = self.conn.cursor()
    cursor.execute("""WITH deleted AS (DELETE FROM data_sets WHERE id = %s RETURNING *) SELECT COUNT(*) FROM deleted;""", (id,))
    del_cnt = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return del_cnt > 0

  def delete_data_set_entry(self, id):
    cursor = self.conn.cursor()
    cursor.execute("""WITH deleted AS (DELETE FROM data_set_entries WHERE id = %s RETURNING *) SELECT COUNT(*) FROM deleted;""", (id,))
    del_cnt = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return del_cnt > 0

  def delete_image(self, id):
    cursor = self.conn.cursor()
    cursor.execute("""WITH deleted AS (DELETE FROM images WHERE id = %s RETURNING *) SELECT COUNT(*) FROM deleted;""", (id,))
    del_cnt = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return del_cnt > 0

  def delete_cropped_image(self, id):
    cursor = self.conn.cursor()
    cursor.execute("""WITH deleted AS (DELETE FROM cropped_images WHERE id = %s RETURNING *) SELECT COUNT(*) FROM deleted;""", (id,))
    del_cnt = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return del_cnt > 0

  def delete_face(self, id):
    cursor = self.conn.cursor()
    cursor.execute("""WITH deleted AS (DELETE FROM faces WHERE id = %s RETURNING *) SELECT COUNT(*) FROM deleted;""", (id,))
    del_cnt = cursor.fetchone()[0]
    self.conn.commit()
    cursor.close()
    return del_cnt > 0

  def delete_facial_landmark(self, id):
    cursor = self.conn.cursor()
    cursor.execute("""WITH deleted AS (DELETE FROM facial_landmarks WHERE id = %s RETURNING *) SELECT COUNT(*) FROM deleted;""", (id,))
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
