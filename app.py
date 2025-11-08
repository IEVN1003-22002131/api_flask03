from flask import jsonify, Flask, render_template, request, make_response, redirect, url_for, flash
from forms import UserForm, Figuras, PizzaForm
from datetime import datetime
from wtforms.validators import InputRequired
import json
import forms
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pizzeria' 
PRECIOS_TAMANO = {'Chica': 40, 'Mediana': 80, 'Grande': 120}
PRECIOS_INGREDIENTES = {'Jamon': 10, 'Pina': 10, 'Champiñones': 10}

@app.route('/Pizza', methods=['GET', 'POST'])
def Pizza():
    customer_data_str = request.cookies.get('customer_data', '{}')
    customer_data = json.loads(customer_data_str)

    if 'fecha' in customer_data and customer_data['fecha']:
        try:
            customer_data['fecha'] = datetime.strptime(customer_data['fecha'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            customer_data.pop('fecha', None)

    if request.method == 'POST':
        form = PizzaForm(request.form)
    else:
        form = PizzaForm(data=customer_data)

    pizzas_pedido_str = request.cookies.get('pizzas_pedido', '[]')
    pizzas_pedido = json.loads(pizzas_pedido_str)
    
    ventas_str = request.cookies.get('cookie_ventas', '[]')
    ventas = json.loads(ventas_str)

    ventas_acumuladas = {}
    total_ventas_dia = 0
    for v in ventas:
        nombre = v.get('nombre', 'Desconocido')
        total = v.get('total', 0)
        ventas_acumuladas[nombre] = ventas_acumuladas.get(nombre, 0) + total
        total_ventas_dia += total
    
    ventas_display = list(ventas_acumuladas.items())
    ventas_visibles_str = request.cookies.get('ventas_visibles', 'true')
    ventas_visibles = (ventas_visibles_str == 'true')
    resp = make_response(redirect(url_for('Pizza')))

    if request.method == 'POST':
        accion = request.form.get('accion')

        def guardar_datos_cliente(response):
            fecha_data = form.fecha.data
            customer_data_to_save = {
                'nombre': form.nombre.data,
                'direccion': form.direccion.data,
                'telefono': form.telefono.data,
                'fecha': fecha_data.strftime('%Y-%m-%d') if fecha_data else None
            }
            response.set_cookie('customer_data', json.dumps(customer_data_to_save), path='/')

        if accion == 'agregar':
            if form.tamano.validate(form) and form.num_pizzas.validate(form):
                tamano = form.tamano.data
                ingredientes = form.ingredientes.data
                num_pizzas = form.num_pizzas.data
                
                subtotal_base = PRECIOS_TAMANO.get(tamano, 0)
                subtotal_ingredientes = sum(PRECIOS_INGREDIENTES.get(ing, 0) for ing in ingredientes)
                subtotal_total = (subtotal_base + subtotal_ingredientes) * num_pizzas
                
                nueva_pizza = {
                    'tamano': tamano,
                    'ingredientes': ", ".join(ingredientes), 
                    'num_pizzas': num_pizzas,
                    'subtotal': subtotal_total
                }
                
                pizzas_pedido.append(nueva_pizza)
                
                resp.set_cookie('pizzas_pedido', json.dumps(pizzas_pedido), path='/')
                guardar_datos_cliente(resp)                
                return resp
            else:
                flash('Verifica el tamaño y cantidad de pizzas.')
                return render_template('pizzeria.html', form=form, pizzas_pedido=pizzas_pedido, ventas_display=ventas_display, total_ventas_dia=total_ventas_dia, ventas_visibles=ventas_visibles)

        elif accion == 'quitar':
            try:
                index_a_quitar = int(request.form.get('pizza_index'))
                if 0 <= index_a_quitar < len(pizzas_pedido):
                    pizzas_pedido.pop(index_a_quitar)
                    
                resp.set_cookie('pizzas_pedido', json.dumps(pizzas_pedido), path='/')
                return resp
            except (ValueError, TypeError):
                flash('No se puede quitar la esta orden.')
                return resp
        
        elif accion == 'terminar':
            campos_cliente_validos = (
                form.nombre.validate(form) &
                form.direccion.validate(form) &
                form.telefono.validate(form) &
                form.fecha.validate(form)
            )
            
            if campos_cliente_validos:
                if not pizzas_pedido:
                    flash('La orden minima es de una pizza"', 'error')
                    return render_template('pizzeria.html', form=form, pizzas_pedido=pizzas_pedido, ventas_display=ventas_display, total_ventas_dia=total_ventas_dia, ventas_visibles=ventas_visibles)
                else:
                    total_pedido_actual = sum(p['subtotal'] for p in pizzas_pedido)
                    
                    flash(f'Total a pagar: ${total_pedido_actual:.2f}', 'success')

                    nueva_venta = {
                        'nombre': form.nombre.data,
                        'direccion': form.direccion.data,
                        'telefono': form.telefono.data,
                        'fecha': form.fecha.data.strftime('%d-%m-%Y'), 
                        'total': total_pedido_actual
                    }
                    ventas.append(nueva_venta)
                    
                    resp.set_cookie('cookie_ventas', json.dumps(ventas), path='/')
                    resp.set_cookie('pizzas_pedido', '[]', max_age=0, path='/')
                    resp.set_cookie('customer_data', '{}', max_age=0, path='/')
                    resp.set_cookie('ventas_visibles', 'true', path='/')
                    return resp
            else:
                flash('Registra los datos de la orden.', 'error')
                return render_template('pizzeria.html', form=form, pizzas_pedido=pizzas_pedido, ventas_display=ventas_display, total_ventas_dia=total_ventas_dia, ventas_visibles=ventas_visibles)

        elif accion == 'limpiar_ventas':
            flash('No hay ventas recientes', 'info')
            resp.set_cookie('cookie_ventas', '[]', max_age=0, path='/')
            return resp
            
        elif accion == 'toggle_ventas':
            if ventas_visibles:
                ventas_visibles_nuevo = 'false'
            else: 
                ventas_visibles_nuevo = 'true'
            
            resp.set_cookie('ventas_visibles', ventas_visibles_nuevo, path='/')
            return resp
        
    return render_template('pizzeria.html', 
                           form=form, 
                           pizzas_pedido=pizzas_pedido, 
                           ventas_display=ventas_display, 
                           total_ventas_dia=total_ventas_dia,
                           ventas_visibles=ventas_visibles)

# ------------------------------------------------------------------------


@app.route('/')
def home():
    return "Holaaaa"

@app.route("/index")
def index():
    titulo= "IEVN1003 - PWA"
    listado= ["Opera 1", "Opera 2","Opera 3", "Opera 4"]
 
    return render_template('/index.html', titulo = titulo, listado = listado)

@app.route("/Alumnos", methods=['GET','POST'])
def alumnos():
    mat=0
    nom=""
    ape=""
    em=""
    estudiantes=[]
    datos={}

    alumnos_clase=UserForm(request.form)
    if request.method== 'POST'and alumnos_clase.validate():
        mat=alumnos_clase.matricula.data
        nom=alumnos_clase.nombre.data
        ape=alumnos_clase.apellido.data
        em=alumnos_clase.email.data
        datos={"matricula":mat, "nombre":nom, "apellido":ape, "correo":em}

        datos_str=request.cookies.get('estudiante')
        if not datos_str:
            return"No hay cookies"
        tem=json.loads(datos_str)
        estudiantes=tem
        estudiantes=json.loads(datos_str)
        print(type(estudiantes))
        estudiantes.append(datos)

    response=make_response(render_template('alumnos.html', form=alumnos_clase,
                              mat=mat,nom=nom,ape=ape,em=em))
    
    response.set_cookie('estudiante', json.dumps(estudiantes))
    return response

@app.route("/get_cookie")
def get_cookie():
    datos_str=request.cookies.get('estudiante')
    if not datos_str:
        return"No hay cookies"
    datos=json.loads(datos_str)
    return jsonify(datos)

@app.route('/figuras', methods=['GET', 'POST'])
def figuras():
    formulario = Figuras(request.form)
    area = None
    nombrefig = ""
    figura_seleccionada = None 

    if request.method == 'POST':
        formafig = formulario.forma.data
        figura_seleccionada = formafig  
        if formafig == 'triangle':
            formulario.altura.validators = [InputRequired(message="Se requiere la altura.")]
        elif formafig == 'rectangle':
            formulario.largo.validators = [InputRequired(message="Se requiere el largo.")]
            formulario.ancho.validators = [InputRequired(message="Se requiere el ancho.")]
        elif formafig == 'circle':
            formulario.radio.validators = [InputRequired(message="Se requiere el radio.")]
        elif formafig == 'pentagon':
            formulario.lado.validators = [InputRequired(message="Se requiere el lado.")]


        if formulario.validate():
            try:
                if formafig == 'triangle':
                    base = formulario.base.data
                    altura = formulario.altura.data
                    area = 0.5 * base * altura
                    nombrefig = "Triángulo"

                elif formafig == 'rectangle':
                    largo = formulario.largo.data
                    ancho = formulario.ancho.data
                    area = largo * ancho
                    nombrefig = "Rectángulo"

                elif formafig == 'circle':
                    radio = formulario.radio.data
                    area = math.pi * (radio**2)
                    nombrefig = "Círculo"

                elif formafig == 'pentagon':
                    lado = formulario.lado.data
                    apotema = (lado / 2) / math.tan(math.radians(36))
                    area = (5 / 2) * lado * apotema
                    nombrefig = "Pentágono"
            
            except TypeError:
                pass 
    
    return render_template('figuras.html', 
                           form=formulario, 
                           area=area, 
                           nombrefig=nombrefig,
                           figura_seleccionada=figura_seleccionada) 
@app.route('/distancia')
def distancia():
    return render_template('/distancia.html')
 
@app.route('/operas', methods= ['GET', 'POST'])
def operas():
 
    resultado = 0  
 
    if request.method == 'POST':
        n1 = request.form.get('n1')
        n2 = request.form.get('n2')
        resultado = float(n1)+float(n2)
 
    return render_template('/operas.html', resultado = resultado)
 
@app.route('/about')
def about():
    return "<h1>This is about the page<h1/>"
 
@app.route("/numero/<int:n>")
def numero(n):
    return "Numero: {}".format(n)
 
@app.route("/user/<int:id>/<string:username>")
def username(id, username):
    return "ID {} nombre: {}".format(id, username)
 
@app.route("/suma/<float:n1>/<float:n2>")
def func(n1, n2):
    return "La suma: {}".format(n1 + n2)
 
@app.route("/prueba")
def prueba():
    return """
    <h1>Prueba de HTML<h1/>
    <p>Esto es una prueba</p>
    <ul>
        <li>Elemento 1</li>
        <li>Elemento 2</li>
        <li>Elemento 3</li>
    </ul>
    """
 
if __name__ == '__main__':
    app.run(debug=True)