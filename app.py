from flask import Flask, render_template, redirect, request, url_for,send_from_directory
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

# Configuración de la base de datos MySQL
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'api_enotech'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

mysql = MySQL()
mysql.init_app(app)

def callBD(query:str, value:str="",devolver:str ='fetchall'):
    conn = mysql.connect()
    cursor = conn.cursor(cursor=DictCursor)
    if value == "":
        cursor.execute(query)
    else:
        cursor.execute(query, value)
      
    if devolver == "fetchone":
        datos = cursor.fetchone()
    else:
        datos = cursor.fetchall()
    conn.commit()
    return datos

@app.route('/images/<path:image>')
def uploads(image):
    return send_from_directory(os.path.join('static/uploads'),image)


@app.route('/')
@app.route('/index')
def index():
    return render_template('front-end/index.html')

@app.route('/nosotros')
def nosotros():
    return render_template('front-end/nosotros.html')

@app.route('/contacto')
def contacto():
    return render_template('front-end/contacto.html')

@app.route('/productos')
def productos():
    return render_template('front-end/productos.html')



@app.route('/getAll')
@app.route('/getAll/<filtro>',methods=['GET'])
def getAll(filtro =""):
    if filtro != "":
        valores=filtro
        query = f"SELECT a.idWine, a.winery, a.wine, b.country, a.image FROM wines AS a INNER JOIN Locations AS b ON a.id_Location = b.idLocation where a.winery like '{valores}%'"
        datos = callBD(query)
    else:
        query = "SELECT a.idWine, a.winery, a.wine, b.country, a.image FROM wines AS a INNER JOIN Locations AS b ON a.id_Location = b.idLocation"
        datos = callBD(query)
    return render_template('back-end/getAll.html', wines=datos)



@app.route('/filtros',methods=['POST','GET'])
def filtros():
    if request.method == 'POST':
        valor = request.form['valor']
        codigo =str(valor)
        if codigo == '':
            return redirect(url_for('getAll'))
        
        return redirect(url_for('getAll',filtro=codigo))
    else:
        return redirect(url_for('getAll'))
   


@app.route('/create',methods=['GET','POST'])
def create():
    if request.method == 'GET':
        sql = "SELECT idLocation, country FROM Locations"
        datos = callBD(sql)
        return render_template('back-end/create.html', locations=datos)
    
    elif request.method == 'POST':
            try:
                _winery = request.form["winery"]
                _wine = request.form["wine"]
                _location = request.form["location"]
                _image = request.files["txtFoto"]

                if _image:
                    now = datetime.now()
                    tiempo = now.strftime("%d%m%y,%H%M%S")
                    filename = tiempo +"_"+_image.filename
                    _image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    filename = "default.jpg"

                datos = (_winery, _wine, _location, filename)
                sql = "INSERT INTO wines (winery, wine, id_Location, image) VALUES (%s, %s, %s, %s)"
                callBD(sql, datos)
                return redirect(url_for('getAll'))
                
            except Exception as e:
                print("Error al agregar el vino:", e)
                return f"Error al agregar el vino: {e}", 400


@app.route('/edit/<int:id>',methods=['GET','POST'])
def edit(id):
    if request.method == 'GET':
        sql = "SELECT a.idWine, a.winery, a.wine,b.idLocation ,b.country, a.image FROM wines AS a INNER JOIN Locations AS b ON a.id_Location = b.idLocation WHERE idWine = %s"
        query = "select idLocation,country from locations where idLocation != (SELECT id_location FROM wines where idWine=%s)"
        wine = callBD(sql, id,'fetchone')
        locations = callBD(query,id)
        return render_template('back-end/edit.html', datos=wine, locations=locations)
    
    elif request.method == 'POST':
        __id = request.form["id"]
        _winery = request.form["winery"]
        _wine = request.form["wine"]
        _location = request.form["location"]
        _image = request.files["image"]

        if _image and _image.filename != '':
            query = 'select image from wines where idWine=%s'
            imageDelete =callBD(query,__id,"fetchone")
            
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'],imageDelete['image']))

            now = datetime.now()
            tiempo = now.strftime("%d%m%y,%H%M%S")
            filename = tiempo + "_" + _image.filename
            _image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            update = [_winery, _wine, _location, filename, __id]
            query = "UPDATE wines SET winery=%s, wine=%s, id_Location=%s, image=%s WHERE idWine=%s"
        else:
            update = [_winery, _wine, _location, __id]
            query = "UPDATE wines SET winery=%s, wine=%s, id_Location=%s WHERE idWine=%s"

        
        callBD(query, update)
        return redirect(url_for('getAll'))

@app.route('/delete/<int:id>')
def delete(id):
    query = "select image from wines where idWine=%s"
    image = callBD(query,id,"fetchone")
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'],image['image']))
    query = "DELETE FROM wines WHERE idWine = %s"
    callBD(query, id)
    return redirect(url_for('getAll'))


if __name__ == '__main__':
    app.run(debug=True, port=8500)
