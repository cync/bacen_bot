#!/usr/bin/env python3
"""
Página de monitoramento do serviço bacen-cron
"""
import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sender import get_execution_logs, is_business_hours
from storage import get_store
from bacen_feed import get_normativos_hoje

def generate_monitoring_page():
    """Gera a página HTML de monitoramento"""
    
    # Coleta dados
    logs = get_execution_logs()
    current_time = datetime.now()
    business_hours_active = is_business_hours()
    
    # Estatísticas
    total_executions = len(logs)
    successful_executions = len([log for log in logs if log.get('status') == 'success'])
    error_executions = len([log for log in logs if log.get('status') == 'error'])
    skipped_executions = len([log for log in logs if log.get('status') in ['skipped', 'no_new_items']])
    
    # Última execução
    last_execution = logs[-1] if logs else None
    
    # Normativos de hoje
    try:
        normativos_hoje = get_normativos_hoje()
        normativos_count = len(normativos_hoje)
    except:
        normativos_count = 0
    
    # Status do banco
    try:
        store = get_store()
        health = store.health_check()
        db_status = health['status']
        subscribers_count = health.get('subscriber_count', 0)
    except:
        db_status = 'error'
        subscribers_count = 0
    
    # HTML da página
    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BACEN Bot - Monitoramento</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .status-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        .status-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            border-left: 4px solid #007bff;
        }}
        .status-card.success {{
            border-left-color: #28a745;
        }}
        .status-card.warning {{
            border-left-color: #ffc107;
        }}
        .status-card.danger {{
            border-left-color: #dc3545;
        }}
        .status-card h3 {{
            margin: 0 0 10px 0;
            color: #495057;
        }}
        .status-value {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .status-card.success .status-value {{
            color: #28a745;
        }}
        .status-card.warning .status-value {{
            color: #ffc107;
        }}
        .status-card.danger .status-value {{
            color: #dc3545;
        }}
        .logs-section {{
            padding: 30px;
            border-top: 1px solid #dee2e6;
        }}
        .logs-section h2 {{
            margin: 0 0 20px 0;
            color: #495057;
        }}
        .log-entry {{
            background: #f8f9fa;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #6c757d;
        }}
        .log-entry.success {{
            border-left-color: #28a745;
        }}
        .log-entry.error {{
            border-left-color: #dc3545;
        }}
        .log-entry.skipped {{
            border-left-color: #ffc107;
        }}
        .log-time {{
            font-weight: bold;
            color: #6c757d;
        }}
        .log-status {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 10px;
        }}
        .log-status.success {{
            background: #d4edda;
            color: #155724;
        }}
        .log-status.error {{
            background: #f8d7da;
            color: #721c24;
        }}
        .log-status.skipped {{
            background: #fff3cd;
            color: #856404;
        }}
        .log-details {{
            margin-top: 10px;
            font-size: 0.9em;
            color: #6c757d;
        }}
        .refresh-info {{
            text-align: center;
            padding: 20px;
            background: #e9ecef;
            color: #6c757d;
            font-size: 0.9em;
        }}
        .auto-refresh {{
            color: #007bff;
            text-decoration: none;
        }}
    </style>
    <script>
        // Auto-refresh a cada 30 segundos
        setTimeout(function() {{
            window.location.reload();
        }}, 30000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 BACEN Bot Monitor</h1>
            <p>Monitoramento do serviço bacen-cron em tempo real</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card {'success' if business_hours_active else 'warning'}">
                <h3>🕒 Status do Sistema</h3>
                <div class="status-value">{'ATIVO' if business_hours_active else 'INATIVO'}</div>
                <p>{'Horário comercial (08:00-19:25 SP)' if business_hours_active else 'Fora do horário comercial'}</p>
            </div>
            
            <div class="status-card {'success' if db_status == 'healthy' else 'danger'}">
                <h3>🗄️ Banco de Dados</h3>
                <div class="status-value">{db_status.upper()}</div>
                <p>{subscribers_count} usuário(s) inscrito(s)</p>
            </div>
            
            <div class="status-card success">
                <h3>📊 Execuções Totais</h3>
                <div class="status-value">{total_executions}</div>
                <p>Últimas 100 execuções</p>
            </div>
            
            <div class="status-card success">
                <h3>✅ Sucessos</h3>
                <div class="status-value">{successful_executions}</div>
                <p>{'%.1f' % (successful_executions/total_executions*100) if total_executions > 0 else 0}% de sucesso</p>
            </div>
            
            <div class="status-card {'warning' if error_executions > 0 else 'success'}">
                <h3>❌ Erros</h3>
                <div class="status-value">{error_executions}</div>
                <p>{'%.1f' % (error_executions/total_executions*100) if total_executions > 0 else 0}% de erro</p>
            </div>
            
            <div class="status-card success">
                <h3>📄 Normativos Hoje</h3>
                <div class="status-value">{normativos_count}</div>
                <p>Normativos encontrados hoje</p>
            </div>
        </div>
        
        <div class="logs-section">
            <h2>📋 Logs de Execução</h2>
            {generate_logs_html(logs)}
        </div>
        
        <div class="refresh-info">
            <p>🔄 Página atualiza automaticamente a cada 30 segundos | 
            <a href="#" class="auto-refresh" onclick="window.location.reload()">Atualizar agora</a></p>
            <p>Última atualização: {current_time.strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def generate_logs_html(logs):
    """Gera HTML dos logs"""
    if not logs:
        return "<p>Nenhum log de execução encontrado.</p>"
    
    # Mostra apenas os últimos 20 logs
    recent_logs = logs[-20:]
    recent_logs.reverse()  # Mais recente primeiro
    
    html_logs = []
    for log in recent_logs:
        timestamp = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
        time_str = timestamp.strftime('%d/%m/%Y %H:%M:%S')
        
        status = log.get('status', 'unknown')
        details = log.get('details', {})
        
        # Determina classe CSS baseada no status
        status_class = status
        if status == 'no_new_items':
            status_class = 'skipped'
        
        # Gera detalhes
        details_html = ""
        if details:
            details_items = []
            if 'normativos_enviados' in details:
                details_items.append(f"Normativos enviados: {details['normativos_enviados']}")
            if 'subscribers_count' in details:
                details_items.append(f"Inscritos: {details['subscribers_count']}")
            if 'duration_seconds' in details:
                details_items.append(f"Duração: {details['duration_seconds']:.1f}s")
            if 'reason' in details:
                details_items.append(f"Motivo: {details['reason']}")
            
            if details_items:
                details_html = f"<div class='log-details'>{' | '.join(details_items)}</div>"
        
        log_html = f"""
        <div class="log-entry {status_class}">
            <span class="log-time">{time_str}</span>
            <span class="log-status {status_class}">{status.upper()}</span>
            {details_html}
        </div>
        """
        html_logs.append(log_html)
    
    return ''.join(html_logs)

if __name__ == "__main__":
    html_content = generate_monitoring_page()
    print("Content-Type: text/html; charset=utf-8")
    print()
    print(html_content)
