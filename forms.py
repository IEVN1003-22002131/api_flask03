from wtforms import Form
from wtforms import StringField, RadioField, SelectMultipleField, IntegerField, DateField
from wtforms import validators, widgets, SubmitField,FloatField, EmailField 
from wtforms.validators import InputRequired, Optional


class UserForm(Form):
    matricula=IntegerField('Matricula', 
    [validators.DataRequired(message= "La matricula es obligatoria")])

    nombre=StringField('Nombre', 
    [validators.DataRequired(message= "El Campo es requerido")])

    apellido=StringField('Apellido', 
    [validators.DataRequired(message= "El Campo es requerido")])

    email=EmailField('Email', 
    [validators.Email(message= "Ingrese Correo Valido")])


class Figuras(Form):
    forma = RadioField(
        'Seleccione una forma: ',
        choices=[
            ('triangle', 'Triangulo'),
            ('rectangle', 'Rectangulo'),
            ('circle', 'Circulo'),
            ('pentagon', 'Pentagono')
        ],
        validators=[InputRequired(message="Selecciona una forma para calcular")]
    )

    base = FloatField('Base: ', validators=[Optional()]) 
    altura = FloatField('Altura: ', validators=[Optional()])
    largo = FloatField('Largo: ', validators=[Optional()])
    ancho = FloatField('Ancho: ', validators=[Optional()])
    radio = FloatField('Radio: ', validators=[Optional()])
    lado = FloatField('Longitud de un lado: ', validators=[Optional()])
    enviar = SubmitField('Calcular Area')


class PizzaForm(Form):
    nombre = StringField('Nombre', [
        validators.DataRequired(message='Este dato es obligatorio')
    ])
    direccion = StringField('Dirección', [
        validators.DataRequired(message='Este dato es obligatorio')
    ])
    telefono = StringField('Teléfono', [
        validators.DataRequired(message='Este dato es obligatorio'),
        validators.Length(min=7, max=10, message='El teléfono debe tener max. 10 digitos')
    ])
    fecha = DateField('Fecha de Compra', format='%Y-%m-%d', validators=[
        validators.DataRequired(message='Este dato es obligatorio')
    ])
    
    tamano = RadioField('Tamaño de la Pizza', choices=[
        ('Chica', 'Chica - $40'),
        ('Mediana', 'Mediana - $80'),
        ('Grande', 'Grande - $120')
    ], validators=[validators.Optional()])

    ingredientes = SelectMultipleField('Ingredientes', choices=[
        ('Jamon', 'Jamón - $10'),
        ('Pina', 'Piña - $10'),
        ('Champiñones', 'Champiñon - $10')
    ], 
    widget=widgets.ListWidget(prefix_label=False), 
    option_widget=widgets.CheckboxInput(),
    validators=[validators.Optional()]
    )

    num_pizzas = IntegerField('Num. de Pizzas', 
        default=1,
        validators=[
            validators.NumberRange(min=1, message='Minimo 1 pizza por orden'),
            validators.Optional()
        ])