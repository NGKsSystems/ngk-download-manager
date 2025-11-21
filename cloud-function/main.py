"""
Google Cloud Function to control GCE VM for Download Manager
Handles start/stop/status of the VM remotely
"""

import functions_framework
from google.cloud import compute_v1
import os
import json
from flask import jsonify

# Configuration - Set these as environment variables in Cloud Function
PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'your-project-id')
ZONE = os.environ.get('GCP_ZONE', 'us-central1-a')
INSTANCE_NAME = os.environ.get('INSTANCE_NAME', 'instance-20251120-182738')
API_KEY = os.environ.get('API_KEY', 'your-secret-api-key')  # Simple auth

def verify_api_key(request):
    """Simple API key authentication"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return False
    token = auth_header[7:]  # Remove 'Bearer '
    return token == API_KEY

@functions_framework.http
def vm_control(request):
    """
    HTTP Cloud Function to control VM
    
    Endpoints:
        POST /start-vm - Start the VM
        POST /stop-vm - Stop the VM
        GET /vm-status - Get VM status and IP
    """
    
    # Enable CORS for mobile app
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    }
    
    # Verify API key
    if not verify_api_key(request):
        return (jsonify({'error': 'Unauthorized'}), 401, headers)
    
    # Get action from path or body
    request_json = request.get_json(silent=True)
    action = request.path.strip('/') or (request_json.get('action') if request_json else None)
    
    try:
        instance_client = compute_v1.InstancesClient()
        
        if action == 'start-vm':
            return start_vm(instance_client, headers)
        elif action == 'stop-vm':
            return stop_vm(instance_client, headers)
        elif action == 'vm-status':
            return get_vm_status(instance_client, headers)
        else:
            return (jsonify({
                'error': 'Invalid action',
                'available': ['start-vm', 'stop-vm', 'vm-status']
            }), 400, headers)
            
    except Exception as e:
        return (jsonify({'error': str(e)}), 500, headers)

def start_vm(instance_client, headers):
    """Start the VM instance"""
    try:
        # Check current status first
        instance = instance_client.get(
            project=PROJECT_ID,
            zone=ZONE,
            instance=INSTANCE_NAME
        )
        
        if instance.status == 'RUNNING':
            return (jsonify({
                'status': 'already_running',
                'message': 'VM is already running',
                'ip': get_external_ip(instance)
            }), 200, headers)
        
        # Start the instance
        operation = instance_client.start(
            project=PROJECT_ID,
            zone=ZONE,
            instance=INSTANCE_NAME
        )
        
        return (jsonify({
            'status': 'starting',
            'message': 'VM is starting',
            'operation': operation.name
        }), 200, headers)
        
    except Exception as e:
        return (jsonify({'error': f'Failed to start VM: {str(e)}'}), 500, headers)

def stop_vm(instance_client, headers):
    """Stop the VM instance"""
    try:
        # Check current status first
        instance = instance_client.get(
            project=PROJECT_ID,
            zone=ZONE,
            instance=INSTANCE_NAME
        )
        
        if instance.status == 'TERMINATED':
            return (jsonify({
                'status': 'already_stopped',
                'message': 'VM is already stopped'
            }), 200, headers)
        
        # Stop the instance
        operation = instance_client.stop(
            project=PROJECT_ID,
            zone=ZONE,
            instance=INSTANCE_NAME
        )
        
        return (jsonify({
            'status': 'stopping',
            'message': 'VM is stopping',
            'operation': operation.name
        }), 200, headers)
        
    except Exception as e:
        return (jsonify({'error': f'Failed to stop VM: {str(e)}'}), 500, headers)

def get_vm_status(instance_client, headers):
    """Get current VM status and IP"""
    try:
        instance = instance_client.get(
            project=PROJECT_ID,
            zone=ZONE,
            instance=INSTANCE_NAME
        )
        
        external_ip = get_external_ip(instance)
        
        return (jsonify({
            'status': instance.status.lower(),
            'ip': external_ip,
            'zone': ZONE,
            'instance': INSTANCE_NAME,
            'ready': instance.status == 'RUNNING',
            'api_url': f'http://{external_ip}:5000' if external_ip else None
        }), 200, headers)
        
    except Exception as e:
        return (jsonify({'error': f'Failed to get VM status: {str(e)}'}), 500, headers)

def get_external_ip(instance):
    """Extract external IP from instance"""
    try:
        if instance.network_interfaces:
            for interface in instance.network_interfaces:
                if interface.access_configs:
                    for config in interface.access_configs:
                        if config.nat_i_p:
                            return config.nat_i_p
    except:
        pass
    return None
