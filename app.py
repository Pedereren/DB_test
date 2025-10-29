import os
from dotenv import load_dotenv
from flask import Flask, render_template_string
import psycopg2

load_dotenv()
app = Flask(__name__)

DB_VARIABLE_NAMES = [
    'DATABASE_HOST', 'DATABASE_NAME', 'DATABASE_USER', 
    'DATABASE_PASSWORD', 'DATABASE_PORT', 'DB_SSLMODE'
]

def get_db_config():
    return {
        'host': os.environ.get('DATABASE_HOST'),
        'database': os.environ.get('DATABASE_NAME'),
        'user': os.environ.get('DATABASE_USER'),
        'password': os.environ.get('DATABASE_PASSWORD'),
        'port': int(os.environ.get('DATABASE_PORT', 5432)),
        'sslmode': os.environ.get('DB_SSLMODE', 'require')
    }

def fetch_products():
    """Hent alle produkter fra tabellen."""
    config = get_db_config()
    conn = psycopg2.connect(**config)
    cur = conn.cursor()
    cur.execute("""
        SELECT product_id, barcode, description, unitprice, quantity
        FROM public.products
        ORDER BY product_id ASC;
    """)
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return colnames, rows



@app.route('/')
def show_products():
    try:
        colnames, rows = fetch_products()
        table_html = "<table class='min-w-full border-collapse border border-gray-300'>"
        table_html += "<thead class='bg-gray-100'><tr>"
        for col in colnames:
            table_html += f"<th class='border px-3 py-2 text-left'>{col}</th>"
        table_html += "</tr></thead><tbody>"
        for row in rows:
            table_html += "<tr>"
            for val in row:
                table_html += f"<td class='border px-3 py-2'>{val}</td>"
            table_html += "</tr>"
        table_html += "</tbody></table>"
        html = f"""
        <html>
        <head>
          <title>Product List</title>
          <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-50 p-8">
          <div class="max-w-5xl mx-auto bg-white p-6 rounded-lg shadow-xl">
            <h1 class="text-3xl font-bold text-indigo-700 mb-6">🧵 Lageroversigt (products)</h1>
            {table_html}
          </div>
        </body>
        </html>
        """
        return render_template_string(html)
    except Exception as e:
        return f"<h2>Databaseforbindelsesfejl:</h2><pre>{e}</pre>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
