from app import db
from app import Pool, Server
db.create_all()

pool = Pool('prod', '1.0', '1.0')
db.session.add(pool)
db.session.commit()

for serv in ['web1', 'web2', 'batch1', 'batch2', 'db1', 'db2', 'db3', 'db4', 'db5']:
    server = Server('1', serv, 'admin', 'admin')
    db.session.add(server)
db.session.commit()
