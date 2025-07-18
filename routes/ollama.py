from flask import Blueprint, render_template, request, redirect, url_for, jsonify

# Import services with error handling
try:
    from services.ollama_service import ollama_service
except ImportError:
    ollama_service = None

ollama_bp = Blueprint('ollama', __name__)

@ollama_bp.route('/ollama_check', methods=['POST'])
def check_ollama():
    """Check Ollama status and redirect back"""
    if ollama_service:
        ollama_service.check_status()
    return redirect(url_for('leads.show_leads'))

@ollama_bp.route('/ollama_status')
def get_ollama_status():
    """Get Ollama status as JSON"""
    if ollama_service:
        status = ollama_service.check_status()
    else:
        status = {"ok": False, "msg": "Ollama service not available"}
    return jsonify(status)

@ollama_bp.route('/ollama_models')
def list_models():
    """List available Ollama models"""
    if not ollama_service:
        return jsonify({"error": "Ollama service not available"}), 500
    
    try:
        import requests
        response = requests.get(f"{ollama_service.url.replace('/api/generate', '')}/api/tags", timeout=3)
        if response.status_code == 200:
            tags = response.json().get("models", [])
            models = [tag["name"] for tag in tags]
            return jsonify({"models": models})
        else:
            return jsonify({"error": "Could not fetch models"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ollama_bp.route('/ollama_models_ui')
def models_ui():
    """Display models in UI"""
    if not ollama_service:
        return "Ollama service not available", 500
    
    available_models = ollama_service.get_available_models()
    selected_model = ollama_service.get_selected_model()
    return render_template('ollama_models.html', 
                         available_models=available_models,
                         selected_model=selected_model)

@ollama_bp.route('/set_model', methods=['POST'])
def set_model():
    """Set preferred model"""
    if not ollama_service:
        return "Ollama service not available", 500
    
    model_name = request.form.get('model_name')
    if model_name:
        ollama_service.set_preferred_model(model_name)
        print(f"[LOG] Modell ändrad till: {model_name}")
    return redirect(url_for('ollama.models_ui')) 