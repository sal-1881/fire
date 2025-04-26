
from flask import Flask, render_template, request, redirect, send_file
import sqlite3
from fpdf import FPDF
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('fire_quotation.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS fire_quotation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            policy_number TEXT,
            risk_type TEXT,
            sum_insured REAL,
            premium_rate REAL,
            premium_amount REAL,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        client_name = request.form['client_name']
        policy_number = request.form['policy_number']
        risk_type = request.form['risk_type']
        sum_insured = float(request.form['sum_insured'])
        premium_rate = float(request.form['premium_rate'])
        premium_amount = (sum_insured * premium_rate) / 100
        notes = request.form['notes']

        conn = sqlite3.connect('fire_quotation.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO fire_quotation (client_name, policy_number, risk_type, sum_insured, premium_rate, premium_amount, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (client_name, policy_number, risk_type, sum_insured, premium_rate, premium_amount, notes))
        conn.commit()
        conn.close()

        return redirect('/generate_pdf')
    return render_template('index.html')

@app.route('/generate_pdf')
def generate_pdf():
    conn = sqlite3.connect('fire_quotation.db')
    c = conn.cursor()
    c.execute('SELECT * FROM fire_quotation ORDER BY id DESC LIMIT 1')
    data = c.fetchone()
    conn.close()

    if not os.path.exists('pdfs'):
        os.makedirs('pdfs')

    pdf_path = os.path.join('pdfs', f'fire_quotation_{data[0]}.pdf')
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'عرض سعر تأمين الحريق / Fire Quotation', ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)

    fields = [
        ('اسم العميل / Client Name', data[1]),
        ('رقم الوثيقة / Policy Number', data[2]),
        ('نوع الخطر / Risk Type', data[3]),
        ('مبلغ التأمين / Sum Insured', data[4]),
        ('نسبة القسط / Premium Rate', data[5]),
        ('مبلغ القسط / Premium Amount', data[6]),
        ('ملاحظات / Notes', data[7]),
    ]

    for label, value in fields:
        pdf.cell(0, 10, f'{label}: {value}', ln=True)

    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
