from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Modelo do Administrador / Dono da Barbearia."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), default="Barbeiro Chefe")
    email = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class ServicePackage(db.Model):
    """Modelo de Pacote/Serviço oferecido pela barbearia."""
    __tablename__ = 'service_packages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    duration_minutes = db.Column(db.Integer, default=45, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com agendamentos
    appointments = db.relationship('Appointment', backref='package', lazy='dynamic')
    
    @property
    def price_formatted(self):
        """Retorna o preço no formato brasileiro: R$ XX,XX."""
        return f"R$ {self.price:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')
    
    @property
    def duration_formatted(self):
        """Retorna a duração formatada: ex: '45 min' ou '1h 15min'."""
        if self.duration_minutes >= 60:
            hrs = self.duration_minutes // 60
            mins = self.duration_minutes % 60
            return f"{hrs}h {mins}min" if mins > 0 else f"{hrs}h"
        return f"{self.duration_minutes} min"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'price_formatted': self.price_formatted,
            'duration_minutes': self.duration_minutes,
            'duration_formatted': self.duration_formatted,
            'is_active': self.is_active
        }

    def __repr__(self):
        return f'<ServicePackage {self.name} - R${self.price}>'


class Appointment(db.Model):
    """Modelo de Agendamento realizado por cliente."""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(120), nullable=False)
    client_phone = db.Column(db.String(30), nullable=False)
    client_email = db.Column(db.String(120), nullable=True)
    package_id = db.Column(db.Integer, db.ForeignKey('service_packages.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(30), default='Pendente', nullable=False) # 'Pendente', 'Confirmado', 'Concluído', 'Cancelado'
    notification_sent = db.Column(db.Boolean, default=False, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def date_formatted(self):
        """Retorna a data formatada: ex: '15/11/2026'."""
        return self.appointment_date.strftime('%d/%m/%Y')
    
    @property
    def time_formatted(self):
        """Retorna a hora formatada: ex: '14:30'."""
        return self.appointment_date.strftime('%H:%M')
    
    @property
    def full_datetime_formatted(self):
        """Retorna data e hora formatadas: '15/11/2026 às 14:30'."""
        return self.appointment_date.strftime('%d/%m/%Y às %H:%M')
        
    @property
    def phone_digits_only(self):
        """Remove caracteres não numéricos do telefone para links do WhatsApp."""
        import re
        digits = re.sub(r'\D', '', self.client_phone or '')
        if len(digits) in [10, 11] and not digits.startswith('55'):
            digits = '55' + digits
        return digits
    
    @property
    def status_badge_class(self):
        """Classes Tailwind para estilizar o status do agendamento."""
        status_map = {
            'Pendente': 'bg-amber-500/10 text-amber-400 border border-amber-500/30',
            'Confirmado': 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30',
            'Concluído': 'bg-blue-500/10 text-blue-400 border border-blue-500/30',
            'Cancelado': 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
        }
        return status_map.get(self.status, 'bg-gray-500/10 text-gray-400 border border-gray-500/30')

    def to_dict(self):
        return {
            'id': self.id,
            'client_name': self.client_name,
            'client_phone': self.client_phone,
            'client_email': self.client_email,
            'package_id': self.package_id,
            'package_name': self.package.name if self.package else 'N/A',
            'price': self.package.price if self.package else 0.0,
            'price_formatted': self.package.price_formatted if self.package else 'R$ 0,00',
            'appointment_date': self.appointment_date.isoformat(),
            'date_formatted': self.date_formatted,
            'time_formatted': self.time_formatted,
            'status': self.status,
            'notification_sent': self.notification_sent,
            'notes': self.notes
        }

    def __repr__(self):
        return f'<Appointment {self.client_name} - {self.appointment_date}>'

