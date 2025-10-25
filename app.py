from flask import Flask, render_template, request
 
app = Flask(__name__)
 
@app.route('/')
def home():
    return "Hello Papu"
 
@app.route("/index")
def index():
 
    titulo= "IEVN1003 - PWA"
    listado= ["Opera 1", "Opera 2","Opera 3", "Opera 4"]
 
    return render_template('/index.html', titulo = titulo, listado = listado)
 
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