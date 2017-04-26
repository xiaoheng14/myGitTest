# -*- coding:utf-8 -*-

import json
import datetime, time
from flask import Blueprint, request, jsonify, send_from_directory
import os
import sys
sys.path.append('..')

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/hello/<opcode>/', methods=['get'])
def get_source(opcode):
    try:
	if opcode == 'l':
	    result = {'i lov you': 'l'}
	    return jsonify(result)
	elif opcode == 'm':
	    result = {'hello': 'm'}
	    return jsonify(result)
	elif opcode == 'j':
	     result = {'520': 'j'}
	     return jsonify(result)
	else:
	    result = {'wrong option': 'try again'}
	    return jsonify(result)
    except Exception as e:
	pass


@api.route('/download/<path:file_id>', methods=['get'])
def download(file_id):
    try:
	dir_str = '/home'
	return send_from_directory(directory=dir_str, filename=file_id)
    except Exception as e:
	pass

