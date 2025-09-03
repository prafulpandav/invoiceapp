from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invoices.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model
class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(100), nullable=False)
    service = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(20), nullable=False)

# ✅ PDF generate helper
def generate_pdf(invoice):
    file_name = f"invoice_{invoice.id}.pdf"
    c = canvas.Canvas(file_name, pagesize=letter)
    c.setFont("Helvetica", 16)

    c.drawString(100, 750, "Invoice")
    c.setFont("Helvetica", 12)

    c.drawString(100, 700, f"Invoice ID: {invoice.id}")
    c.drawString(100, 680, f"Customer: {invoice.customer}")
    c.drawString(100, 660, f"Service: {invoice.service}")
    c.drawString(100, 640, f"Amount: {invoice.amount}")
    c.drawString(100, 620, f"Date: {invoice.date}")

    c.showPage()
    c.save()

    return file_name

# Routes
@app.route('/')
def home():
    invoices = Invoice.query.all()
    return render_template("index.html", invoices=invoices)

@app.route('/add', methods=["GET", "POST"])
def add_invoice():
    if request.method == "POST":
        customer = request.form['customer']
        service = request.form['service']
        amount = request.form['amount']
        date = request.form['date']

        new_invoice = Invoice(customer=customer, service=service, amount=amount, date=date)
        db.session.add(new_invoice)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("add_invoice.html")

# ✅ PDF download route
@app.route('/invoice/<int:id>/pdf')
def download_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    file_name = generate_pdf(invoice)
    return send_file(file_name, as_attachment=True)

# ✅ Delete route
@app.route('/invoice/<int:id>/delete')
def delete_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    db.session.delete(invoice)
    db.session.commit()
    return redirect(url_for('home'))

# ✅ Edit/Update route
@app.route('/invoice/<int:id>/edit', methods=["GET", "POST"])
def edit_invoice(id):
    invoice = Invoice.query.get_or_404(id)

    if request.method == "POST":
        invoice.customer = request.form['customer']
        invoice.service = request.form['service']
        invoice.amount = request.form['amount']
        invoice.date = request.form['date']

        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit_invoice.html", invoice=invoice)

# ✅ Run block always at last
if __name__ == "__main__":
    with app.app_context():
        if not os.path.exists("invoices.db"):
            db.create_all()
    app.run(debug=True)
