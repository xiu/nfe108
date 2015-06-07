# Projet NFE108

Pour install les dependences :
pip install -r requirements.txt

Premierement, executer le bootstrap :
```
python bootstrap.py
```

Ensuite lancer l'app :
```
python app.py
```

Nous pouvons ensuite executer des requetes sur l'application :

Lister le pool prod :
```
curl http://127.0.0.1:5000/pool/prod -uadmin:admin
```

Changer les versions du pool prod:
```
curl -XPUT -H"Content-type: application/json" http://127.0.0.1:5000/pool/prod -uadmin:admin -d '{"app_web": "2.0", "app_loading": "2.0"}'
```

Utiliser l'enc :
```
python enc.py web1
```
