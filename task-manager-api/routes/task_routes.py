"""Rotas de Task — camada fina que delega ao controller."""
from flask import Blueprint, request, jsonify

from controllers import task_controller

task_bp = Blueprint('tasks', __name__)


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(task_controller.listar()), 200


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    return jsonify(task_controller.obter(task_id)), 200


@task_bp.route('/tasks', methods=['POST'])
def create_task():
    return jsonify(task_controller.criar(request.get_json())), 201


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    return jsonify(task_controller.atualizar(task_id, request.get_json())), 200


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task_controller.deletar(task_id)
    return jsonify({'message': 'Task deletada com sucesso'}), 200


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    resultados = task_controller.buscar(
        request.args.get('q', ''),
        request.args.get('status', ''),
        request.args.get('priority', ''),
        request.args.get('user_id', ''),
    )
    return jsonify(resultados), 200


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    return jsonify(task_controller.estatisticas()), 200
