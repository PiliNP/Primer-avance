from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'secret_key'

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mi_base_de_datos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db = SQLAlchemy(app)

# Definición de modelos
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    lead_time = db.Column(db.Integer, nullable=False)

class BOM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_material = db.Column(db.String(100), nullable=False)
    cantidad_disponible = db.Column(db.Integer, nullable=False)
    costo = db.Column(db.Float, nullable=False)
    lead_time = db.Column(db.Integer, nullable=False)

class CentroTrabajo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    linea = db.Column(db.String(100), nullable=False)
    capacidad_inicial = db.Column(db.Integer, nullable=False)
    operarios = db.Column(db.Integer, nullable=False)
    throughput = db.Column(db.Float, nullable=False)
    costo_extra = db.Column(db.Float, nullable=False)
    presupuesto_extra = db.Column(db.Float, nullable=False)
    costo_contratacion = db.Column(db.Float, nullable=False)
    costo_despido = db.Column(db.Float, nullable=False)
    salario = db.Column(db.Float, nullable=False)

class MPS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    demanda_pronosticada = db.Column(db.Integer, nullable=False)
    inventario_seguridad = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, nullable=False)

class MRP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    periodos = db.Column(db.Integer, nullable=False)
    porcentaje_desechos = db.Column(db.Float, nullable=False)

# Crear la base de datos si no existe
with app.app_context():
    db.create_all()

# Rutas para la aplicación

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro_producto', methods=['GET', 'POST'])
def registro_producto():
    if request.method == 'POST':
        sku = request.form['sku']
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        activo = request.form['activo']
        lead_time = int(request.form['lead_time'])
        
        # Verificar si el SKU ya existe
        if Producto.query.filter_by(sku=sku).first():
            flash('Código ya existente')
            return redirect(url_for('registro_producto'))
        
        producto = Producto(sku=sku, nombre=nombre, cantidad=cantidad, precio=precio, activo=(activo == 'True'), lead_time=lead_time)
        db.session.add(producto)
        db.session.commit()
        return redirect(url_for('registro_producto'))
    
    productos = Producto.query.all()  # Recuperar todos los productos de la base de datos
    return render_template('registro_producto.html', productos=productos)

@app.route('/registro_bom', methods=['GET', 'POST'])
def registro_bom():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        costo = float(request.form['costo'])
        lead_time = int(request.form['lead_time'])
        
        componente = BOM(nombre_material=nombre, cantidad_disponible=cantidad, costo=costo, lead_time=lead_time)
        db.session.add(componente)
        db.session.commit()
        return redirect(url_for('registro_bom'))
    
    componentes_bom = BOM.query.all()  # Recuperar todos los componentes de la base de datos
    return render_template('registro_bom.html', componentes_bom=componentes_bom)

@app.route('/mps', methods=['GET', 'POST'])
def mps():
    if request.method == 'POST':
        producto_id = request.form['producto']
        periodos = int(request.form['periodos'])
        inventario_seguridad = float(request.form['inventario_seguridad'])
        
        mps_entry = MPS(producto_id=producto_id, periodos=periodos, inventario_seguridad=inventario_seguridad)
        db.session.add(mps_entry)
        db.session.commit()
        return redirect(url_for('mps'))

    productos = Producto.query.all()  # Recuperar productos para el formulario MPS
    return render_template('mps.html', productos=productos)

@app.route('/mrp', methods=['GET', 'POST'])
def mrp():
    if request.method == 'POST':
        producto_id = request.form['producto']
        periodos = int(request.form['periodos'])
        porcentaje_desechos = float(request.form['porcentaje_desechos'])
        
        mrp_entry = MRP(producto_id=producto_id, periodos=periodos, porcentaje_desechos=porcentaje_desechos)
        db.session.add(mrp_entry)
        db.session.commit()
        return redirect(url_for('mrp'))

    productos = Producto.query.all()  # Recuperar productos para el formulario MRP
    return render_template('mrp.html', productos=productos)

@app.route('/centro_trabajo', methods=['GET', 'POST'])
def centro_trabajo():
    if request.method == 'POST':
        linea = request.form['linea']
        capacidad = int(request.form['capacidad'])
        operarios = int(request.form['operarios'])
        throughput = float(request.form['throughput'])
        costo_extra = float(request.form['costo_extra'])
        presupuesto = float(request.form['presupuesto'])
        costo_contratacion = float(request.form['costo_contratacion'])
        costo_despido = float(request.form['costo_despido'])
        
        centro = CentroTrabajo(linea=linea, capacidad_inicial=capacidad, operarios=operarios, throughput=throughput,
                               costo_extra=costo_extra, presupuesto_extra=presupuesto,
                               costo_contratacion=costo_contratacion, costo_despido=costo_despido)
        db.session.add(centro)
        db.session.commit()
        return redirect(url_for('centro_trabajo'))

    centros_trabajo = CentroTrabajo.query.all()  # Recuperar centros de trabajo de la base de datos
    return render_template('centro_trabajo.html', centros_trabajo=centros_trabajo)

@app.route('/crp', methods=['GET'])
def crp():
    centros_trabajo = CentroTrabajo.query.all()  # Recuperar centros de trabajo para CRP
    return render_template('crp.html', centros_trabajo=centros_trabajo)

if __name__ == '__main__':
    app.run(debug=True)
