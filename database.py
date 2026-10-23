from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Paciente(db.Model):
  __tablename__ = 'paciente'
  id_paciente = db.Column(db.Integer, primary_key=True)
  cpf = db.Column(db.String(11), unique=True, nullable=False)
  nome = db.Column(db.String(150), nullable=False)
  telefone = db.Column(db.String(20))
  email = db.Column(db.String(120))


class Profissional(db.Model):
  __tablename__ = 'profissional'
  id_profissional = db.Column(db.Integer, primary_key=True)
  nome = db.Column(db.String(150), nullable=False)
  cpf = db.Column(db.String(11), unique=True, nullable=False)
  telefone = db.Column(db.String(20))
  email = db.Column(db.String(120))
  registro_profissional = db.Column(db.String(30))
  tipo = db.Column(db.Integer)

  # Relacionamento para o Médico achar os dados pessoais facilmente
  medico_rel = db.relationship(
      'Medico', backref='profissional_obj', uselist=False
  )


class Medico(db.Model):
  __tablename__ = 'medico'
  id_medico = db.Column(db.Integer, primary_key=True)
  id_profissional = db.Column(
      db.Integer,
      db.ForeignKey('profissional.id_profissional'),
      unique=True,
      nullable=False,
  )
  crm = db.Column(db.String(20), unique=True, nullable=False)


class Agendamento(db.Model):
  __tablename__ = 'agendamento'
  id_agendamento = db.Column(db.Integer, primary_key=True)
  id_paciente = db.Column(
      db.Integer, db.ForeignKey('paciente.id_paciente'), nullable=False
  )
  id_medico = db.Column(
      db.Integer, db.ForeignKey('medico.id_medico'), nullable=False
  )
  data_agendamento = db.Column(db.String(20), nullable=False)
  horario = db.Column(db.String(10))
  situacao = db.Column(db.String(20), default='Agendado')
  observacoes = db.Column(db.Text)

  # Relacionamentos para puxar o nome do paciente e do médico na tabela de agendamentos
  paciente_obj = db.relationship('Paciente', backref='agendamentos')
  medico_obj = db.relationship('Medico', backref='agendamentos')