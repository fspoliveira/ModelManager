from flask import Flask, request
from flask_restx import Api, Resource, fields
import requests

app = Flask(__name__)
api = Api(app, version='1.0', title='API Analise de Crédito Quantum Finance',
          description='Uma API simples para calcular a propensão à inadimplência e fazer predições')
ns = api.namespace('Inadimplencia', description='Operações de inadimplência')
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
                return {'mensagem': 'Dados recebidos e processados com sucesso', 'predicao': prediction}
            else:
                return api.abort(500, 'Erro ao chamar a API de predição')

@ns.route('/clustering')
class CustomerClustering(Resource):
    @api.expect(data_model)
    def post(self):
        """Envia os dados diretamente para a API de Clustering para obter a classificação de clustering"""
        if request.is_json:
            data = request.json
            # Correção da chamada à API de Clustering
            cluster_response = requests.post('http://localhost:5002/Clustering/cluster', json=data)
            if cluster_response.status_code == 200:
                cluster_info = cluster_response.json()
                return {'mensagem': 'Clustering realizado com sucesso', 'cluster_info': cluster_info}, 200
            else:
                return api.abort(500, 'Erro ao chamar a API de clustering')
        else:
            return api.abort(400, 'Requisição inválida. O corpo da requisição deve estar no formato JSON')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)