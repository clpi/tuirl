import peewee

db = peewee.SqliteDatabase('tracker.db')

class BaseModel(peewee.Model):
    class Meta:
        database = db

class SSHKey(BaseModel):
    name = peewee.CharField(unique=True)
    host = peewee.CharField()
    user = peewee.CharField()
    port = peewee.IntegerField(default=22)
    identity_file = peewee.CharField(null=True)
    description = peewee.TextField(null=True)

class GPGKey(BaseModel):
    name = peewee.CharField(unique=True)
    key_id = peewee.CharField()
    email = peewee.CharField()
    description = peewee.TextField(null=True)

class Database(BaseModel):
    name = peewee.CharField(unique=True)
    type = peewee.CharField() # postgres, mysql, sqlite, etc.
    host = peewee.CharField()
    port = peewee.IntegerField()
    user = peewee.CharField()
    db_name = peewee.CharField()
    description = peewee.TextField(null=True)

def init_db():
    db.connect()
    db.create_tables([SSHKey, GPGKey, Database], safe=True)
    db.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
