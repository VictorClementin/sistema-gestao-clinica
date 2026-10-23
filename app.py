from datetime import datetime
from database import Agendamento, Medico, Paciente, Profissional, db
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinica.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
  db.create_all()


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/pacientes')
def pacientes():
  lista = Paciente.query.all()
  return render_template('pacientes.html', pacientes=lista)


@app.route('/medicos')
def medicos():
  lista = Medico.query.all()
  return render_template('medicos.html', medicos=lista)


@app.route('/agendamentos')
def agendamentos():
  lista_agendamentos = Agendamento.query.all()
  lista_pacientes = Paciente.query.all()
  lista_medicos = Medico.query.all()
  return render_template(
      'agendamentos.html',
      agendamentos=lista_agendamentos,
      pacientes=lista_pacientes,
      medicos=lista_medicos,
  )


@app.route('/adicionar_paciente', methods=['POST'])
def adicionar_paciente():
  novo_paciente = Paciente(
      cpf=request.form.get('cpf'),
      nome=request.form.get('nome'),
      telefone=request.form.get('telefone'),
      email=request.form.get('email'),
  )
  db.session.add(novo_paciente)
  db.session.commit()
  return redirect(url_for('pacientes'))


@app.route('/adicionar_medico', methods=['POST'])
def adicionar_medico():
  novo_prof = Profissional(
      nome=request.form.get('nome'),
      cpf=request.form.get('cpf'),
      telefone=request.form.get('telefone'),
      email=request.form.get('email'),
      registro_profissional=request.form.get('crm'),
      tipo=1,
  )
  db.session.add(novo_prof)
  db.session.commit()

  novo_medico = Medico(
      id_profissional=novo_prof.id_profissional, crm=request.form.get('crm')
  )
  db.session.add(novo_medico)
  db.session.commit()
  return redirect(url_for('medicos'))


@app.route('/adicionar_agendamento', methods=['POST'])
def adicionar_agendamento():
  data_bruta = request.form.get('data')
  try:
    data_formatada = datetime.strptime(data_bruta, '%Y-%m-%d').strftime(
        '%d/%m/%Y'
    )
  except:
    data_formatada = data_bruta

  novo_agendamento = Agendamento(
      id_paciente=request.form.get('id_paciente'),
      id_medico=request.form.get('id_medico'),
      data_agendamento=data_formatada,
      horario=request.form.get('horario'),
      observacoes=request.form.get('observacoes'),
      situacao='Agendado',
  )
  db.session.add(novo_agendamento)
  db.session.commit()
  return redirect(url_for('agendamentos'))


# --- ROTAS DE EXCLUSÃO ---


@app.route('/deletar_paciente/<int:id>')
def deletar_paciente(id):
  paciente = Paciente.query.get_or_404(id)
  db.session.delete(paciente)
  db.session.commit()
  return redirect(url_for('pacientes'))


@app.route('/deletar_medico/<int:id>')
def deletar_medico(id):
  medico = Medico.query.get_or_404(id)
  prof = (
      Profissional.query.get(medico.id_profissional)
      if medico.id_profissional
      else None
  )
  db.session.delete(medico)
  if prof:
    db.session.delete(prof)
  db.session.commit()
  return redirect(url_for('medicos'))


@app.route('/deletar_agendamento/<int:id>')
def deletar_agendamento(id):
  agendamento = Agendamento.query.get_or_404(id)
  db.session.delete(agendamento)
  db.session.commit()
  return redirect(url_for('agendamentos'))


if __name__ == '__main__':
  app.run(debug=True)