"""Rotas de relatórios e categorias — camada fina que delega ao controller."""
from flask import Blueprint, request, jsonify

from controllers import report_controller

report_bp = Blueprint('reports', __name__)


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    return jsonify(report_controller.resumo()), 200


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    return jsonify(report_controller.por_usuario(user_id)), 200


@report_bp.route('/categories', methods=['GET'])
def get_categories():
    return jsonify(report_controller.listar_categorias()), 200


@report_bp.route('/categories', methods=['POST'])
def create_category():
    return jsonify(report_controller.criar_categoria(request.get_json())), 201


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    return jsonify(report_controller.atualizar_categoria(cat_id, request.get_json())), 200


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    report_controller.deletar_categoria(cat_id)
    return jsonify({'message': 'Categoria deletada'}), 200
