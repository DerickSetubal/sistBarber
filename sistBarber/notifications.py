"""
Módulo de Simulação de Notificações e Lembretes (WhatsApp / SMS / E-mail)
Simula o disparo de mensagens para o Cliente e para o Dono da Barbearia.
"""

import sys
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from datetime import datetime, timedelta
from models import db, Appointment

# Histórico em memória dos disparos simulados para exibição em tempo real no Admin
NOTIFICATION_LOGS = []

def format_simulated_message(appointment, hours_remaining):
    """Gera o texto das mensagens formatadas para cliente e dono."""
    client_msg = (
        f"💈 *Lembrete BarberShop Manager* 💈\n"
        f"Olá, *{appointment.client_name}*!\n\n"
        f"Lembramos que seu atendimento está marcado para:\n"
        f"📅 *Data:* {appointment.date_formatted}\n"
        f"⏰ *Horário:* {appointment.time_formatted}\n"
        f"✂️ *Serviço:* {appointment.package.name} ({appointment.package.price_formatted})\n\n"
        f"📍 *Endereço:* Av. Paulista, 1000 - Bela Vista, SP\n"
        f"Caso precise reagendar ou cancelar, entre em contato respondendo esta mensagem.\n"
        f"Aguardamos você para uma experiência impecável!"
    )
    
    owner_msg = (
        f"🔔 *Alerta para a Barbearia / Dono* 🔔\n"
        f"Atendimento próximo em aproximadamente {hours_remaining}h:\n"
        f"👤 *Cliente:* {appointment.client_name}\n"
        f"📞 *Telefone:* {appointment.client_phone}\n"
        f"✂️ *Pacote:* {appointment.package.name}\n"
        f"🕒 *Horário:* {appointment.full_datetime_formatted}\n"
        f"💰 *Valor:* {appointment.package.price_formatted}\n"
        f"📌 *Status Atual:* {appointment.status}"
    )
    
    return client_msg, owner_msg


def log_to_console(appointment, client_msg, owner_msg, hours_remaining):
    """Exibe no terminal um log altamente formatado simulando o envio de WhatsApp/SMS."""
    border = "=" * 76
    sub_border = "-" * 76
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    print("\n" + border)
    print(f" 🚀 [DISPARO AUTOMÁTICO DE LEMBRETE SIMULADO] - {now_str}")
    print(f" Agendamento #{appointment.id} | Faltando aprox. {hours_remaining}h para o horário")
    print(border)
    print(" 📲 NOTIFICAÇÃO ENVIADA AO CLIENTE (WhatsApp / SMS):")
    print(f" Destinatário: {appointment.client_name} <{appointment.client_phone}>")
    if appointment.client_email:
        print(f" E-mail: {appointment.client_email}")
    print(sub_border)
    for line in client_msg.split('\n'):
        print(f"   {line}")
    print(sub_border)
    print(" 🔔 NOTIFICAÇÃO ENVIADA AO DONO DA BARBEARIA (Painel / WhatsApp):")
    print(sub_border)
    for line in owner_msg.split('\n'):
        print(f"   {line}")
    print(border + "\n")


def check_and_send_reminders(hours_window=24):
    """
    Verifica agendamentos próximos nas próximas `hours_window` horas
    que ainda não receberam notificação (`notification_sent == False`)
    e que não estejam cancelados.
    
    Retorna uma lista de resumos dos disparos realizados.
    """
    now = datetime.now()
    cutoff = now + timedelta(hours=hours_window)
    
    # Busca agendamentos dentro da janela de tempo ainda não notificados
    appointments = Appointment.query.filter(
        Appointment.appointment_date >= now,
        Appointment.appointment_date <= cutoff,
        Appointment.notification_sent == False,
        Appointment.status.in_(['Pendente', 'Confirmado'])
    ).all()
    
    dispatched_events = []
    
    for appt in appointments:
        # Calcular tempo restante em horas aproximadas
        diff = appt.appointment_date - now
        hours_remaining = max(1, int(diff.total_seconds() // 3600))
        
        client_msg, owner_msg = format_simulated_message(appt, hours_remaining)
        
        # Simula envio imprimindo no terminal
        log_to_console(appt, client_msg, owner_msg, hours_remaining)
        
        # Marca como notificado no banco
        appt.notification_sent = True
        
        # Salva evento para o log em memória exibido no painel
        event = {
            'id': appt.id,
            'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'client_name': appt.client_name,
            'client_phone': appt.client_phone,
            'package_name': appt.package.name if appt.package else 'Pacote',
            'appointment_time': appt.full_datetime_formatted,
            'hours_remaining': hours_remaining,
            'client_preview': client_msg[:120] + "...",
            'type': 'Lembrete Automático (24h/1h)'
        }
        NOTIFICATION_LOGS.insert(0, event)
        dispatched_events.append(event)
        
    if appointments:
        db.session.commit()
        
    return dispatched_events


def force_simulate_reminder(appointment_id):
    """
    Força o disparo imediato de lembrete para um agendamento específico,
    útil para demonstração e testes do dono no painel administrativo.
    """
    appt = Appointment.query.get(appointment_id)
    if not appt:
        return None
        
    now = datetime.now()
    if appt.appointment_date > now:
        diff = appt.appointment_date - now
        hours_remaining = max(1, int(diff.total_seconds() // 3600))
    else:
        hours_remaining = 0
        
    client_msg, owner_msg = format_simulated_message(appt, hours_remaining)
    log_to_console(appt, client_msg, owner_msg, hours_remaining)
    
    appt.notification_sent = True
    db.session.commit()
    
    event = {
        'id': appt.id,
        'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'client_name': appt.client_name,
        'client_phone': appt.client_phone,
        'package_name': appt.package.name if appt.package else 'Pacote',
        'appointment_time': appt.full_datetime_formatted,
        'hours_remaining': hours_remaining,
        'client_preview': client_msg[:120] + "...",
        'type': 'Disparo Manual pelo Dono'
    }
    NOTIFICATION_LOGS.insert(0, event)
    return event

