from flask import Flask, render_template, redirect, request, url_for,send_from_directory
from flaskext.mysql import MySQL
import os
from werkzeug.utils import secure_filename

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

def callBD(query, value=0):
    conexion = mysql.connect()
    cursor = conexion.cursor()
    if value == 0:
        cursor.execute(query)
    else:
        cursor.execute(query, value)
    conexion.commit()
    return cursor.fetchall()

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
def getAll():
    sql = "SELECT a.idWine, a.winery, a.wine, b.country, a.image FROM wines AS a INNER JOIN Locations AS b ON a.id_Location = b.idLocation"
    datos = callBD(sql)
    return render_template('back-end/getAll.html', wines=datos)

@app.route('/create')
def create():
    sql = "SELECT idLocation, country FROM Locations"
    datos = callBD(sql)
    return render_template('back-end/create.html', locations=datos)

@app.route('/addWine', methods=["POST"])
def addWine():
    try:
        _winery = request.form["winery"]
        _wine = request.form["wine"]
        _location = request.form["location"]
        _image = request.files["txtFoto"]

        if _image:
            filename = secure_filename(_image.filename)
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

@app.route('/edit/<int:id>')
def edit(id):
    sql = "SELECT a.idWine, a.winery, a.wine, b.country, a.image FROM wines AS a INNER JOIN Locations AS b ON a.id_Location = b.idLocation WHERE idWine = %s"
    query = "SELECT idLocation, country FROM Locations"
    wine = callBD(sql, id)
    locations = callBD(query)
    return render_template('back-end/edit.html', datos=wine, locations=locations)

@app.route('/update', methods=["POST"])
def update():
    __id = request.form["id"]
    _winery = request.form["winery"]
    _wine = request.form["wine"]
    _location = request.form["location"]
    _image = request.files["image"]

    if _image and _image.filename != '':
        filename = secure_filename(_image.filename)
        _image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        filename = "default.jpg"

    update = [_winery, _wine, _location, filename, __id]
    query = "UPDATE wines SET winery=%s, wine=%s, id_Location=%s, image=%s WHERE idWine=%s"
    callBD(query, update)
    return redirect(url_for('getAll'))

@app.route('/delete/<int:id>')
def delete(id):
    query = "DELETE FROM wines WHERE idWine = %s"
    callBD(query, id)
    return redirect(url_for('getAll'))

if __name__ == '__main__':
    app.run(debug=True, port=8500)
