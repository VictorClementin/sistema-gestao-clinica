from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinica.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'chave_secreta_clinica'
db = SQLAlchemy(app)


# DIAGRAMA DE CLASSES / BANCO DE DADOS
# ==========================================
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(50), nullable=False)

class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))

class Medico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crm = db.Column(db.String(20), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(11))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medico.id'), nullable=False)
    data = db.Column(db.String(20))
    horario = db.Column(db.String(10))
    observacao = db.Column(db.String(200))
    situacao = db.Column(db.String(50))

    # Relacionamentos para puxar o nome do paciente e do médico na tabela de agendamentos
    paciente = db.relationship('Paciente', backref='agendamentos')
    medico = db.relationship('Medico', backref='agendamentos')

class Exame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    tipo_exame = db.Column(db.String(100), nullable=False)
    resultado = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

# ==========================================
# ROTAS DE AUTENTICAÇÃO E LOGIN
# ==========================================
@app.route('/')
def index():
    if 'logado' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/fazer_login', methods=['POST'])
def fazer_login():
    usuario_digitado = request.form.get('usuario', '').strip()
    senha_digitada = request.form.get('senha', '').strip()
    
    usuario_encontrado = Usuario.query.filter_by(username=usuario_digitado, senha=senha_digitada).first()
    
    if usuario_encontrado:
        session['logado'] = True
        return redirect(url_for('dashboard'))
    else:
        return "Usuário ou senha incorretos! <br><br><a href='/'>Voltar para o Login</a>"

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        novo_username = request.form.get('usuario', '').strip()
        nova_senha = request.form.get('senha', '').strip()
        
        if not novo_username or not nova_senha:
            return "Preencha todos os campos! <br><br><a href='/registrar'>Voltar</a>"

        usuario_existe = Usuario.query.filter_by(username=novo_username).first()
        if usuario_existe:
            return "Esse nome de usuário já está cadastrado! <br><br><a href='/registrar'>Tente outro nome</a>"
        
        try:
            novo_usuario = Usuario(username=novo_username, senha=nova_senha)
            db.session.add(novo_usuario)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            return f"Erro ao cadastrar: {str(e)}. <br><br><a href='/registrar'>Voltar</a>"
            
    return render_template('registrar.html')

@app.route('/sair')
def sair():
    session.clear()
    return redirect(url_for('index'))

# ==========================================
# ROTAS DO SISTEMA
# ==========================================
@app.route('/dashboard')
def dashboard():
    if 'logado' not in session: return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/pacientes', methods=['GET', 'POST'])
def pacientes():
    if 'logado' not in session: return redirect(url_for('index'))
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        
        try:
            novo_paciente = Paciente(nome=nome, cpf=cpf, telefone=telefone, email=email)
            db.session.add(novo_paciente)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return "Erro: CPF já cadastrado ou dados inválidos. <br><br><a href='/pacientes'>Voltar</a>"
            
        return redirect(url_for('pacientes'))
        
    lista_pacientes = Paciente.query.all()
    return render_template('pacientes.html', pacientes=lista_pacientes)

@app.route('/deletar_paciente/<int:id>')
def deletar_paciente(id):
    if 'logado' not in session: return redirect(url_for('index'))
    
    paciente = Paciente.query.get_or_404(id)
    try:
        db.session.delete(paciente)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return "Erro ao excluir paciente. <br><br><a href='/pacientes'>Voltar</a>"
        
    return redirect(url_for('pacientes'))

@app.route('/medicos', methods=['GET', 'POST'])
def medicos():
    if 'logado' not in session: return redirect(url_for('index'))
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        crm = request.form.get('crm', '').strip()
        cpf = request.form.get('cpf', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        
        try:
            novo_medico = Medico(nome=nome, crm=crm, cpf=cpf, telefone=telefone, email=email)
            db.session.add(novo_medico)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return "Erro: CRM já cadastrado ou dados inválidos. <br><br><a href='/medicos'>Voltar</a>"
            
        return redirect(url_for('medicos'))
        
    lista_medicos = Medico.query.all()
    return render_template('medicos.html', medicos=lista_medicos)

@app.route('/deletar_medico/<int:id>')
def deletar_medico(id):
    if 'logado' not in session: return redirect(url_for('index'))
    
    medico = Medico.query.get_or_404(id)
    try:
        db.session.delete(medico)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return "Erro ao excluir médico. <br><br><a href='/medicos'>Voltar</a>"
        
    return redirect(url_for('medicos'))

@app.route('/agendamentos', methods=['GET', 'POST'])
def agendamentos():
    if 'logado' not in session: return redirect(url_for('index'))
    
    if request.method == 'POST':
        paciente_id = request.form.get('paciente_id')
        medico_id = request.form.get('medico_id')
        data = request.form.get('data')
        horario = request.form.get('horario')
        observacao = request.form.get('observacao', '').strip()
        situacao = 'Agendado'
        
        try:
            novo_agendamento = Agendamento(
                paciente_id=paciente_id, medico_id=medico_id, 
                data=data, horario=horario, 
                observacao=observacao, situacao=situacao
            )
            db.session.add(novo_agendamento)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return "Erro ao realizar agendamento. <br><br><a href='/agendamentos'>Voltar</a>"
            
        return redirect(url_for('agendamentos'))
        
    lista_agendamentos = Agendamento.query.all()
    lista_pacientes = Paciente.query.all()
    lista_medicos = Medico.query.all()
    
    return render_template(
        'agendamentos.html', 
        agendamentos=lista_agendamentos, 
        pacientes=lista_pacientes, 
        medicos=lista_medicos
    )

@app.route('/deletar_agendamento/<int:id>')
def deletar_agendamento(id):
    if 'logado' not in session: return redirect(url_for('index'))
    
    agendamento = Agendamento.query.get_or_404(id)
    try:
        db.session.delete(agendamento)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return "Erro ao cancelar agendamento. <br><br><a href='/agendamentos'>Voltar</a>"
        
    return redirect(url_for('agendamentos'))

@app.route('/historico')
def historico():
    if 'logado' not in session: return redirect(url_for('index'))
    lista_pacientes = Paciente.query.all()
    return render_template('historico.html', pacientes=lista_pacientes)

@app.route('/prontuario/<int:paciente_id>', methods=['GET', 'POST'])
def prontuario(paciente_id):
    if 'logado' not in session: return redirect(url_for('index'))
    
    paciente = Paciente.query.get_or_404(paciente_id)
    
    if request.method == 'POST':
        tipo = request.form.get('tipo_exame', '').strip()
        resultado = request.form.get('resultado', '').strip()
        
        try:
            novo_exame = Exame(paciente_id=paciente.id, tipo_exame=tipo, resultado=resultado)
            db.session.add(novo_exame)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return "Erro ao registrar exame. <br><br><a href='/historico'>Voltar</a>"
            
        return redirect(url_for('prontuario', paciente_id=paciente.id))
        
    lista_exames = Exame.query.filter_by(paciente_id=paciente.id).all()
    return render_template('prontuario.html', paciente=paciente, exames=lista_exames)

if __name__ == '__main__':
    app.run(debug=True)