import os
import sys

# Garante suporte a UTF-8 no terminal Windows para emojis e caracteres especiais
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from config import Config
from models import db, User, ServicePackage, Appointment
from notifications import check_and_send_reminders, force_simulate_reminder, NOTIFICATION_LOGS
from seed_data import seed_database

def create_app():
    """Fábrica de aplicação Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializa extensões
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Por favor, faça login para acessar o painel administrativo.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    # Context Processor para disponibilizar variáveis globais nos templates
    @app.context_processor
    def inject_globals():
        return {
            'barbershop_name': app.config['BARBERSHOP_NAME'],
            'barbershop_phone': app.config['BARBERSHOP_PHONE'],
            'barbershop_address': app.config['BARBERSHOP_ADDRESS'],
            'barbershop_hours': app.config['BARBERSHOP_HOURS'],
            'now': datetime.now(),
            'notification_logs': NOTIFICATION_LOGS[:8]
        }
    
    # Criação do banco de dados e dados iniciais
    with app.app_context():
        db.create_all()
        seed_database()

    # =========================================================================
    # ROTAS PÚBLICAS (Área do Cliente)
    # =========================================================================

    @app.route('/')
    def index():
        """Página Inicial / Landing Page com serviços e pacotes do banco de dados."""
        packages = ServicePackage.query.filter_by(is_active=True).order_by(ServicePackage.price.asc()).all()
        return render_template('index.html', packages=packages)

    @app.route('/agendar', methods=['GET', 'POST'])
    def agendar():
        """Fluxo de Agendamento em Etapas (Wizard)."""
        packages = ServicePackage.query.filter_by(is_active=True).order_by(ServicePackage.price.asc()).all()
        selected_package_id = request.args.get('pacote', type=int)
        
        if request.method == 'POST':
            client_name = request.form.get('client_name', '').strip()
            client_phone = request.form.get('client_phone', '').strip()
            client_email = request.form.get('client_email', '').strip()
            package_id = request.form.get('package_id', type=int)
            date_str = request.form.get('appointment_date', '').strip()
            time_str = request.form.get('appointment_time', '').strip()
            notes = request.form.get('notes', '').strip()
            
            # Validações
            if not client_name or not client_phone or not package_id or not date_str or not time_str:
                flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
                return render_template('agendar.html', packages=packages, selected_package_id=package_id)
                
            try:
                full_datetime_str = f"{date_str} {time_str}"
                appointment_date = datetime.strptime(full_datetime_str, "%Y-%m-%d %H:%M")
            except ValueError:
                flash('Data ou horário com formato inválido. Tente novamente.', 'danger')
                return render_template('agendar.html', packages=packages, selected_package_id=package_id)
                
            if appointment_date < datetime.now():
                flash('Não é possível agendar um horário no passado! Selecione uma data e hora futura.', 'warning')
                return render_template('agendar.html', packages=packages, selected_package_id=package_id)
                
            # Verifica se o horário já está ocupado por outro cliente
            conflict = Appointment.query.filter(
                Appointment.appointment_date == appointment_date,
                Appointment.status.in_(['Pendente', 'Confirmado'])
            ).first()
            
            if conflict:
                flash('Esse horário já foi reservado por outro cliente. Por favor, escolha outro horário.', 'warning')
                return render_template('agendar.html', packages=packages, selected_package_id=package_id)
                
            # Criação do agendamento
            new_appointment = Appointment(
                client_name=client_name,
                client_phone=client_phone,
                client_email=client_email if client_email else None,
                package_id=package_id,
                appointment_date=appointment_date,
                status='Confirmado', # Já entra como confirmado ou pendente conforme a regra
                notification_sent=False,
                notes=notes if notes else None
            )
            
            db.session.add(new_appointment)
            db.session.commit()
            
            flash('Agendamento realizado com sucesso! Aguardamos você.', 'success')
            return redirect(url_for('confirmacao', id=new_appointment.id))
            
        return render_template('agendar.html', packages=packages, selected_package_id=selected_package_id)

    @app.route('/confirmacao/<int:id>')
    def confirmacao(id):
        """Página de Confirmação e Sucesso do Agendamento."""
        appointment = Appointment.query.get_or_404(id)
        
        # Link do WhatsApp pré-formatado para o cliente confirmar diretamente com a barbearia
        whatsapp_number = app.config['BARBERSHOP_PHONE'].replace('+', '').replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
        text_message = (
            f"Olá! Acabei de agendar um horário na {app.config['BARBERSHOP_NAME']}.\n"
            f"👤 Nome: {appointment.client_name}\n"
            f"✂️ Serviço: {appointment.package.name}\n"
            f"📅 Data: {appointment.full_datetime_formatted}\n"
            f"Protocolo: #{appointment.id}"
        )
        import urllib.parse
        encoded_msg = urllib.parse.quote(text_message)
        whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_msg}"
        
        return render_template('confirmacao.html', appointment=appointment, whatsapp_url=whatsapp_url)

    @app.route('/api/available-slots')
    def available_slots():
        """Retorna horários disponíveis para determinada data em formato JSON."""
        date_str = request.args.get('date')
        if not date_str:
            return jsonify({'slots': []})
            
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'slots': [], 'error': 'Data inválida'})
            
        # Gera slots das 09:00 até as 19:30 a cada 30 min
        open_hour = app.config['OPEN_HOUR']
        close_hour = app.config['CLOSE_HOUR']
        interval = app.config['SLOT_INTERVAL']
        
        # Busca agendamentos existentes no dia que não estão cancelados
        existing_appointments = Appointment.query.filter(
            db.func.date(Appointment.appointment_date) == target_date,
            Appointment.status.in_(['Pendente', 'Confirmado'])
        ).all()
        
        booked_times = {appt.appointment_date.strftime('%H:%M') for appt in existing_appointments}
        
        slots = []
        now = datetime.now()
        current_time = datetime.combine(target_date, datetime.min.time()).replace(hour=open_hour, minute=0)
        end_time = datetime.combine(target_date, datetime.min.time()).replace(hour=close_hour, minute=0)
        
        while current_time < end_time:
            time_label = current_time.strftime('%H:%M')
            is_past = (target_date == now.date() and current_time.time() <= now.time())
            is_booked = time_label in booked_times
            
            slots.append({
                'time': time_label,
                'available': (not is_past and not is_booked),
                'reason': 'Passado' if is_past else ('Ocupado' if is_booked else 'Disponível')
            })
            current_time += timedelta(minutes=interval)
            
        return jsonify({'date': date_str, 'slots': slots})

    # =========================================================================
    # AUTENTICAÇÃO DO DONO / ADMIN
    # =========================================================================

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Tela de Login para o Dono / Administrador."""
        if current_user.is_authenticated:
            return redirect(url_for('admin_dashboard'))
            
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            remember = bool(request.form.get('remember'))
            
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user, remember=remember)
                flash(f'Bem-vindo de volta, {user.name}!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('admin_dashboard'))
            else:
                flash('Usuário ou senha incorretos. Verifique suas credenciais.', 'danger')
                
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        """Encerra a sessão do Administrador."""
        logout_user()
        flash('Você saiu do painel administrativo com segurança.', 'info')
        return redirect(url_for('login'))

    # =========================================================================
    # PAINEL ADMINISTRATIVO (Protegido por @login_required)
    # =========================================================================

    @app.route('/admin')
    @login_required
    def admin_dashboard():
        """Dashboard Geral com métricas, faturamento e agenda do dia."""
        today = date.today()
        first_day_of_month = today.replace(day=1)
        
        # Agendamentos de Hoje
        today_appts = Appointment.query.filter(
            db.func.date(Appointment.appointment_date) == today
        ).order_by(Appointment.appointment_date.asc()).all()
        
        # Contadores
        total_today = len(today_appts)
        total_all = Appointment.query.count()
        total_pending = Appointment.query.filter_by(status='Pendente').count()
        
        # Faturamento Estimado do Mês (soma de agendamentos Confirmados/Concluídos no mês atual)
        month_appts = Appointment.query.filter(
            Appointment.appointment_date >= first_day_of_month,
            Appointment.status.in_(['Confirmado', 'Concluído'])
        ).all()
        
        estimated_revenue = sum(appt.package.price for appt in month_appts if appt.package)
        
        # Próximos agendamentos gerais
        upcoming_appts = Appointment.query.filter(
            Appointment.appointment_date >= datetime.now(),
            Appointment.status != 'Cancelado'
        ).order_by(Appointment.appointment_date.asc()).limit(8).all()
        
        return render_template(
            'admin/dashboard.html',
            total_today=total_today,
            total_all=total_all,
            total_pending=total_pending,
            estimated_revenue=estimated_revenue,
            today_appts=today_appts,
            upcoming_appts=upcoming_appts
        )

    @app.route('/admin/agendamentos')
    @login_required
    def admin_agendamentos():
        """Listagem completa e gestão de agendamentos com filtros."""
        status_filter = request.args.get('status', 'Todos')
        date_filter = request.args.get('periodo', 'todos')
        
        query = Appointment.query
        
        # Filtro de Status
        if status_filter != 'Todos':
            query = query.filter_by(status=status_filter)
            
        # Filtro de Data
        today = date.today()
        if date_filter == 'hoje':
            query = query.filter(db.func.date(Appointment.appointment_date) == today)
        elif date_filter == 'amanha':
            query = query.filter(db.func.date(Appointment.appointment_date) == today + timedelta(days=1))
        elif date_filter == 'semana':
            start_week = today - timedelta(days=today.weekday())
            end_week = start_week + timedelta(days=6)
            query = query.filter(
                db.func.date(Appointment.appointment_date) >= start_week,
                db.func.date(Appointment.appointment_date) <= end_week
            )
        elif date_filter == 'mes':
            start_month = today.replace(day=1)
            query = query.filter(db.func.date(Appointment.appointment_date) >= start_month)
            
        appointments = query.order_by(Appointment.appointment_date.desc()).all()
        
        return render_template(
            'admin/agendamentos.html',
            appointments=appointments,
            status_filter=status_filter,
            date_filter=date_filter
        )

    @app.route('/admin/agendamento/<int:id>/status', methods=['POST'])
    @login_required
    def update_appointment_status(id):
        """Atualiza o status de um agendamento (Confirmado, Concluído, Cancelado, etc)."""
        appt = Appointment.query.get_or_404(id)
        new_status = request.form.get('status')
        if new_status in ['Pendente', 'Confirmado', 'Concluído', 'Cancelado']:
            appt.status = new_status
            db.session.commit()
            flash(f'Status do agendamento #{appt.id} alterado para "{new_status}".', 'success')
        return redirect(request.referrer or url_for('admin_agendamentos'))

    @app.route('/admin/agendamento/<int:id>/excluir', methods=['POST'])
    @login_required
    def delete_appointment(id):
        """Exclui um agendamento do sistema."""
        appt = Appointment.query.get_or_404(id)
        db.session.delete(appt)
        db.session.commit()
        flash(f'Agendamento #{id} de {appt.client_name} foi excluído.', 'info')
        return redirect(request.referrer or url_for('admin_agendamentos'))

    # =========================================================================
    # GESTÃO DE PACOTES E PREÇOS (CRUD COMPLETO)
    # =========================================================================

    @app.route('/admin/pacotes')
    @login_required
    def admin_pacotes():
        """Página de CRUD para o dono gerenciar pacotes, preços e durações."""
        packages = ServicePackage.query.order_by(ServicePackage.price.asc()).all()
        return render_template('admin/pacotes.html', packages=packages)

    @app.route('/admin/pacotes/novo', methods=['POST'])
    @login_required
    def create_package():
        """Adiciona um novo pacote/serviço."""
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price_str = request.form.get('price', '0').replace(',', '.')
        duration = request.form.get('duration_minutes', 45, type=int)
        
        if not name or not price_str:
            flash('Nome e Preço são obrigatórios para o pacote.', 'danger')
            return redirect(url_for('admin_pacotes'))
            
        try:
            price = float(price_str)
        except ValueError:
            flash('Valor de preço inválido.', 'danger')
            return redirect(url_for('admin_pacotes'))
            
        new_package = ServicePackage(
            name=name,
            description=description,
            price=price,
            duration_minutes=duration,
            is_active=True
        )
        db.session.add(new_package)
        db.session.commit()
        
        flash(f'Pacote "{name}" criado com sucesso! Já está visível para os clientes.', 'success')
        return redirect(url_for('admin_pacotes'))

    @app.route('/admin/pacotes/<int:id>/editar', methods=['POST'])
    @login_required
    def edit_package(id):
        """Edita os dados de um pacote existente (preço, duração, nome, descrição)."""
        package = ServicePackage.query.get_or_404(id)
        
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price_str = request.form.get('price', '').replace(',', '.')
        duration = request.form.get('duration_minutes', type=int)
        is_active = bool(request.form.get('is_active'))
        
        if not name or not price_str:
            flash('Nome e Preço são obrigatórios.', 'danger')
            return redirect(url_for('admin_pacotes'))
            
        try:
            package.price = float(price_str)
        except ValueError:
            flash('Preço inválido.', 'danger')
            return redirect(url_for('admin_pacotes'))
            
        package.name = name
        package.description = description
        if duration:
            package.duration_minutes = duration
        package.is_active = is_active
        
        db.session.commit()
        flash(f'Pacote "{package.name}" atualizado com sucesso! Alterações refletidas na landing page.', 'success')
        return redirect(url_for('admin_pacotes'))

    @app.route('/admin/pacotes/<int:id>/toggle', methods=['POST'])
    @login_required
    def toggle_package(id):
        """Ativa ou desativa a exibição pública de um pacote."""
        package = ServicePackage.query.get_or_404(id)
        package.is_active = not package.is_active
        db.session.commit()
        status_text = "ativado" if package.is_active else "desativado"
        flash(f'Pacote "{package.name}" foi {status_text}.', 'info')
        return redirect(url_for('admin_pacotes'))

    @app.route('/admin/pacotes/<int:id>/excluir', methods=['POST'])
    @login_required
    def delete_package(id):
        """Exclui um pacote caso não tenha agendamentos vinculados, ou desativa."""
        package = ServicePackage.query.get_or_404(id)
        
        # Verifica se há agendamentos vinculados
        if package.appointments.count() > 0:
            package.is_active = False
            db.session.commit()
            flash(f'O pacote "{package.name}" possui agendamentos no histórico e foi apenas desativado (ocultado do público).', 'warning')
        else:
            db.session.delete(package)
            db.session.commit()
            flash(f'Pacote "{package.name}" excluído definitivamente.', 'info')
            
        return redirect(url_for('admin_pacotes'))

    # =========================================================================
    # SIMULAÇÃO DE NOTIFICAÇÕES E LEMBRETES (WhatsApp / SMS / E-mail)
    # =========================================================================

    @app.route('/admin/simular-lembretes', methods=['POST'])
    @login_required
    def trigger_reminders():
        """Dispara a checagem de lembretes para as próximas 24 horas."""
        hours = request.form.get('hours', 24, type=int)
        dispatched = check_and_send_reminders(hours_window=hours)
        
        if dispatched:
            flash(f'Sucesso! {len(dispatched)} lembrete(s) simulado(s) e enviados ao cliente e ao dono. Verifique os logs abaixo ou no console!', 'success')
        else:
            flash('Nenhum agendamento pendente de notificação encontrado dentro da janela selecionada.', 'info')
            
        return redirect(request.referrer or url_for('admin_dashboard'))

    @app.route('/admin/agendamento/<int:id>/notificar-agora', methods=['POST'])
    @login_required
    def send_single_notification(id):
        """Dispara o lembrete simulado imediatamente para um agendamento específico."""
        event = force_simulate_reminder(id)
        if event:
            flash(f'Lembrete simulado disparado com sucesso para {event["client_name"]} ({event["client_phone"]})! Log gerado no terminal.', 'success')
        else:
            flash('Agendamento não encontrado.', 'danger')
        return redirect(request.referrer or url_for('admin_agendamentos'))

    @app.route('/admin/api/verificar-lembretes', methods=['GET', 'POST'])
    @login_required
    def api_check_reminders():
        """Endpoint JSON para executar e receber os logs da simulação."""
        hours = request.args.get('hours', 24, type=int)
        dispatched = check_and_send_reminders(hours_window=hours)
        return jsonify({
            'success': True,
            'count': len(dispatched),
            'dispatched': dispatched
        })

    return app

app = create_app()

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print(" 💈 BarberShop Manager Iniciando...")
    print(" 🌐 URL Pública: http://127.0.0.1:5000")
    print(" 🔑 Painel Admin: http://127.0.0.1:5000/login")
    print(" 👤 Usuário: admin  |  Senha: admin123")
    print("=" * 60 + "\n")
    app.run(debug=True, port=5000)

