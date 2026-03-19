"""
Jessica AI - VS Code Copilot Agent API Server

Runs Jessica as an API service that can be called from VS Code extension.
"""

import os
import sys
import json
import logging
from typing import Dict, Any
from datetime import datetime

# Try importing Flask - if not available, provide setup instructions
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError:
    print("ERROR: Flask not installed!")
    print("Install with: pip install flask flask-cors")
    exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for VS Code extension

# Global reference to Jessica instance
jessica_instance = None
health_module = None
# Simple in-memory task queue for VS Code automation
TASK_QUEUE: list[Dict[str, Any]] = []
excel_module = None


@app.route('/authorize', methods=['GET'])
def authorize_info():
    """Compatibility endpoint for clients expecting /authorize."""
    return jsonify({
        'status': 'available',
        'message': 'Authorization endpoint is reachable.',
        'note': 'This API uses local/offline auth by default. Configure OAuth in webapp/app.py if needed.'
    }), 200


def initialize_jessica():
    """Initialize Jessica AI instance"""
    global jessica_instance
    try:
        logger.info("Initializing Jessica AI...")
        # Ensure project root is on sys.path when running as a script
        # This makes `import jessica` work even if invoked via direct file path
        api_dir = os.path.dirname(os.path.abspath(__file__))
        pkg_dir = os.path.dirname(api_dir)  # .../jessica
        project_root = os.path.dirname(pkg_dir)  # project root
        for p in (project_root, pkg_dir):
            if p and p not in sys.path:
                sys.path.insert(0, p)
        # Import advice skill module
        from jessica.skills import advice_skill
        # Import system health module
        from jessica.monitoring import system_health as _system_health
        # Import Excel automation
        from jessica.automation import excel as _excel
        
        jessica_instance = advice_skill
        global health_module
        health_module = _system_health
        global excel_module
        excel_module = _excel
        logger.info("✓ Jessica AI initialized")
        return jessica_instance
    except Exception as e:
        logger.error(f"Could not initialize Jessica: {e}")
        import traceback
        traceback.print_exc()
        return None


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'service': 'Jessica AI Copilot Agent',
        'timestamp': datetime.now().isoformat(),
        'jessica_loaded': jessica_instance is not None,
        'health_available': health_module is not None,
        'excel_available': (excel_module is not None and excel_module.is_available())
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint for Copilot agent
    
    Expected payload:
    {
        "message": "user question",
        "context": {
            "editor": "code",
            "language": "python",
            "selection": "code snippet"
        }
    }
    """
    global jessica_instance
    
    try:
        # Initialize on first request if not already done
        if not jessica_instance:
            logger.info("Initializing Jessica on first request...")
            initialize_jessica()
            
        if not jessica_instance:
            return jsonify({'error': 'Jessica initialization failed'}), 500
        
        data = request.get_json()
        message = data.get('message', '').strip()
        context = data.get('context', {})
        
        if not message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Process with Jessica
        logger.info(f"Received: {message[:50]}...")
        
        # Use Jessica's advice skill
        intent = {"text": message, "intent": "advice"}
        # Attach system health to context for resource-aware responses
        if health_module:
            context = {**context, "system_health": health_module.get_system_health()}
        response = jessica_instance.run(intent, context, [], None)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'model': 'jessica-offline-ai'
        })
    
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/agent/capabilities', methods=['GET'])
def get_capabilities():
    """Return Jessica's capabilities as an agent"""
    return jsonify({
        'name': 'Jessica AI',
        'version': '1.0.0',
        'capabilities': [
            'code-review',
            'code-completion',
            'code-explanation',
            'debugging',
            'documentation',
            'refactoring',
            'creative-thinking',
            'decision-making',
            'problem-solving',
            'emotional-intelligence'
        ],
        'skills': [
            'emotional_intelligence',
            'conflict_resolution',
            'decision_making',
            'financial_literacy',
            'travel_planning',
            'tech_support',
            'thinking_frameworks',
            'storytelling',
            'etiquette',
            'first_aid',
            'home_maintenance',
            'recipes',
            'logical_fallacies',
            'professional_communication',
            'systems_thinking',
            'digital_wellness',
            'chess',
            'code_evolution'
        ],
        'features': {
            'offline': True,
            'local_models': True,
            'adaptive_learning': True,
            'semantic_memory': True,
            'knowledge_stores': 17
        }
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get Jessica status and metrics"""
    if not jessica_instance:
        return jsonify({'status': 'offline', 'error': 'Jessica not initialized'}), 500
    
    return jsonify({
        'status': 'online',
        'name': 'Jessica AI',
        'model_router': 'multi-model',
        'memory': {
            'context_aware': True,
            'semantic_memory': True,
            'learning_enabled': True
        },
        'system_health': health_module.get_system_health() if health_module else None,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/system/health', methods=['GET'])
def system_health():
    """Return system health metrics and safe-to-run decision."""
    if not health_module:
        return jsonify({'error': 'health module not available'}), 500
    return jsonify(health_module.can_run_heavy_task())


def main():
    """Run the API server"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║  Jessica AI - VS Code Copilot Agent API Server                ║
    ║  Running on http://localhost:8080                             ║
    ║                                                                ║
    ║  Endpoints:                                                    ║
    ║  - GET  /health              → Health check                   ║
    ║  - GET  /api/status          → Jessica status                 ║
    ║  - GET  /api/agent/capabilities → Agent capabilities          ║
    ║  - POST /api/chat            → Chat/query Jessica             ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize Jessica
    result = initialize_jessica()
    if result:
        print(f"✓ Jessica initialized successfully (type: {type(result)})")
    else:
        print("✗ WARNING: Jessica initialization returned None!")
    
    # Run Flask app
    app.run(
        host='localhost',
        port=8080,
        debug=False,
        threaded=True
    )


# --- VS Code Task Queue Endpoints ---
@app.route('/api/tasks', methods=['GET'])
def list_tasks():
    return jsonify({
        'count': len(TASK_QUEUE),
        'tasks': TASK_QUEUE
    })


@app.route('/api/tasks', methods=['POST'])
def enqueue_task():
    try:
        item = request.get_json(force=True)
        if not isinstance(item, dict):
            return jsonify({'error': 'task must be an object'}), 400
        # Minimal validation
        item.setdefault('id', f"t-{len(TASK_QUEUE)+1}")
        item.setdefault('created', datetime.now().isoformat())
        TASK_QUEUE.append(item)
        return jsonify({'enqueued': True, 'queue_size': len(TASK_QUEUE), 'task': item}), 200
    except Exception as e:
        logger.error(f"enqueue_task error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/next', methods=['GET'])
def dequeue_task():
    try:
        if not TASK_QUEUE:
            return jsonify({'task': None}), 200
        item = TASK_QUEUE.pop(0)
        return jsonify({'task': item}), 200
    except Exception as e:
        logger.error(f"dequeue_task error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks', methods=['DELETE'])
def clear_tasks():
    try:
        TASK_QUEUE.clear()
        return jsonify({'cleared': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- Office Automation Endpoints ---
@app.route('/api/automation/excel/open', methods=['POST'])
def excel_open():
    if not excel_module or not excel_module.is_available():
        return jsonify({'ok': False, 'error': 'Excel automation not available'}), 500
    data = request.get_json(force=True) or {}
    visible = bool(data.get('visible', True))
    file_path = data.get('path')
    result = excel_module.open_excel(file_path=file_path, visible=visible)
    return jsonify(result), 200 if result.get('ok') else 500


if __name__ == '__main__':
    main()
