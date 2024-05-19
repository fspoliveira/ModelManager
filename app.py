from flask import Flask, request
from flask_restx import Api, Resource, fields
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker
from flask_migrate import Migrate
import requests
import os
from dotenv import load_dotenv
import io

# Função personalizada para carregar o arquivo .env com codificação UTF-8
def load_dotenv_utf8(dotenv_path):
    with io.open(dotenv_path, 'r', encoding='utf-8') as dotenv_file:
        load_dotenv(stream=dotenv_file)

# Carregar variáveis de ambiente do arquivo .env usando a função personalizada
dotenv_path = '.env'
load_dotenv_utf8(dotenv_path)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') == 'True'

# Configuração do SQLAlchemy
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# Configuração do Flask-Migrate
migrate = Migrate(app, Base)

api = Api(app, version='1.0', title='API Analise de Crédito Quantum Finance',
          description='Uma API simples para calcular a propensão à inadimplência e fazer predições')

ns = api.namespace('Inadimplencia', description='Operações de inadimplência')
ns1 = api.namespace('Classificação', description='Classificação Clustering')

# Definição do modelo de dados
class APIRequest(Base):
    __tablename__ = 'api_requests'
    id = Column(Integer, primary_key=True)
    request_type = Column(String(50), nullable=False)
    request_json = Column(JSON, nullable=False)
    response_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())

# Função para salvar a requisição e a resposta no banco de dados
def save_to_db(request_type, request_json, response_json):
    new_request = APIRequest(
        request_type=request_type,
        request_json=request_json,
        response_json=response_json
    )
    session.add(new_request)
    session.commit()

# Modelo esperado para entrada de dados, com exemplo
data_model = api.model('Data', {
    'loan_amount': fields.Integer(required=True, description='Quantia do empréstimo'),
    'Credit_Score': fields.Integer(required=True, description='Pontuação de crédito'),
    'loan_purpose': fields.String(required=True, description='Propósito do empréstimo (ex: car, home)'),
    'annual_income': fields.Float(required=True, description='Renda anual'),
    'term': fields.Integer(required=True, description='Duração do empréstimo em meses'),
    'rate_of_interest': fields.Float(required=True, description='Taxa de juros'),
    'age': fields.Integer(required=True, description='Idade do solicitante'),
    'employment_status': fields.String(required=True, description='Status de emprego (ex: employed, unemployed)'),
    'housing_status': fields.String(required=True, description='Status de moradia (ex: own, rent)')
})

model = api.model('PropensaoInadimplencia', {
    'data': fields.Nested(data_model, description='Dados do solicitante', example={
        "loan_amount": 20000,
        "Credit_Score": 700,
        "loan_purpose": "car",
        "annual_income": 60000,
        "term": 60,
        "rate_of_interest": 5,
        "age": 35,
        "employment_status": "employed",
        "housing_status": "own"
    })
})

cluster_input_model = api.model('ClusterValue', {
    'loan_amount': fields.Float(required=True, description='The loan amount'),
    'income': fields.Float(required=True, description='Income of the applicant'),
    'Credit_Score': fields.Float(required=True, description='Credit Score of the applicant')
})

@ns.route('/propensao')
class PropensaoInadimplencia(Resource):
    @api.expect(data_model)
    def post(self):
        """Calcula a propensão à inadimplência com base nos dados fornecidos"""
        if request.is_json:
            data = request.json
            # Chama a API de predição do outro servidor
            response = requests.post('http://localhost:5001/Prediction/predict', json=data)
            if response.status_code == 200:
                prediction = response.json()
                save_to_db('propensao', data, prediction)
                return {'mensagem': 'Dados recebidos e processados com sucesso', 'predicao': prediction}
            else:
                return api.abort(500, 'Erro ao chamar a API de predição')

@ns1.route('/clustering')
class CustomerClustering(Resource):
    @api.expect(cluster_input_model)
    def post(self):
        """Envia os dados diretamente para a API de Clustering para obter a classificação de clustering"""
        if request.is_json:
            data = request.json
            # Correção da chamada à API de Clustering
            cluster_response = requests.post('http://localhost:5002/Clustering/cluster', json=data)
            if cluster_response.status_code == 200:
                cluster_info = cluster_response.json()
                save_to_db('clustering', data, cluster_info)
                return {'mensagem': 'Clustering realizado com sucesso', 'cluster_info': cluster_info}, 200
            else:
                return api.abort(500, 'Erro ao chamar a API de clustering')
        else:
            return api.abort(400, 'Requisição inválida. O corpo da requisição deve estar no formato JSON')

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(debug=True, host='0.0.0.0', port=5000)