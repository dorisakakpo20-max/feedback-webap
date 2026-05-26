import os
from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2  # Utilisez 'pyodbc' si vous êtes sur Azure SQL Server

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'un_secret_par_defaut_pour_les_tests')

# Récupération de la chaîne de connexion Azure depuis les variables d'environnement
# (Très important pour la sécurité sur Azure App Service)
DB_CONNECTION_STRING = os.environ.get('AZURE_DATABASE_URL')

def get_db_connection():
    # Exemple de connexion pour Azure Database for PostgreSQL
    # Si vous utilisez Azure SQL Server, changez cette partie avec pyodbc
    try:
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        return conn
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return None

# Route principale : affiche le formulaire et les feedbacks existants
@app.route('/', methods=['GET'])
def index():
    conn = get_db_connection()
    feedbacks = []
    if conn:
        cursor = conn.cursor()
        # On récupère les feedbacks (créez la table 'feedbacks' au préalable)
        try:
            cursor.execute('SELECT name, email, message FROM feedbacks ORDER BY id DESC;')
            feedbacks = cursor.fetchall()
        except Exception as e:
            print(f"Erreur lors de la récupération : {e}")
        finally:
            cursor.close()
            conn.close()
    
    return render_template('index.html', feedbacks=feedbacks)

# Route pour traiter la soumission du formulaire
@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not message:
        flash('Le nom et le message sont obligatoires !', 'error')
        return redirect(url_for('index'))

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO feedbacks (name, email, message) VALUES (%s, %s, %s);',
                (name, email, message)
            )
            conn.commit()
            flash('Merci pour votre feedback !', 'success')
        except Exception as e:
            print(f"Erreur lors de l'insertion : {e}")
            flash('Une erreur est survenue lors de l\'enregistrement.', 'error')
        finally:
            cursor.close()
            conn.close()
    else:
        flash('Impossible de se connecter à la base de données.', 'error')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
