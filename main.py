from flask import Flask, render_template, request, flash, redirect, url_for
import pandas as pd
import locale

# Configura el locale para Colombia
locale.setlocale(locale.LC_ALL, 'es_CO')

# Cargar el archivo de Excel
Auxilio = pd.read_excel('Auxilio.xlsx', sheet_name='Auxilio')
Auxilio = Auxilio.rename(columns={'CodigoConductor': 'codigo', 'ClasificaciónDía': 'Tipo'})

# Crear el diccionario de usuarios
usuarios = Auxilio.set_index('codigo')['identificacion'].to_dict()

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_flash'  # Necesaria para flash()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        codigo = request.form['codigo']
        identificacion = request.form['identificacion']  # Contraseña ingresada

        # Validar credenciales
        if codigo.isdigit() and int(codigo) in usuarios and str(usuarios[int(codigo)]) == identificacion:
            # Filtrar datos del conductor
            df_filtrado = Auxilio[Auxilio['codigo'] == int(codigo)]
            
            Acumulado = df_filtrado['Dinero Dia'].sum()
            Acumulado = locale.currency(round(Acumulado), grouping=True).replace(",00", "")

            Nombre_Empleado = df_filtrado['nombre_completo'].unique()

            # Obtener el mes de la primera fila
            if not df_filtrado.empty:
                mes = pd.to_datetime(df_filtrado['Fecha'].iloc[0]).strftime('%B')  # Formatea el mes
            else:
                mes = None

            df_filtrado['Dinero Dia'] = df_filtrado['Dinero Dia'].apply(lambda x: locale.currency(round(x), grouping=True).replace(",00", ""))

            df_filtrado = df_filtrado[['Fecha', 'Tipo', 'Cumplimiento Turno', 'Cumplimiento Tabla Partida', 
                                       'Servicio Cliente', 'Tiempo Adicional', 'Comportamiento Seguro', 
                                       'Puntos Dia', 'Dinero Dia']]

            tabla_html = df_filtrado.to_html(index=False, classes='table table-striped table-bordered table-hover')    
        else:
            # Credenciales incorrectas
            flash("Código o contraseña errados. Intente nuevamente.")
            return redirect(url_for('index'))
    else:
        tabla_html = None
        Acumulado = None
        Nombre_Empleado = None
        mes = None

    return render_template('index.html', tabla=tabla_html, acumulado=Acumulado, nombre=Nombre_Empleado, mes=mes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
