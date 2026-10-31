import os

class Config:
    """Configurações da aplicação BarberShop Manager."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'barbershop-secret-key-super-segura-2026')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(BASE_DIR, 'barbershop.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Informações da Barbearia
    BARBERSHOP_NAME = "BarberShop Premium"
    BARBERSHOP_PHONE = "+55 (11) 98765-4321"
    BARBERSHOP_ADDRESS = "Av. Paulista, 1000 - Bela Vista, São Paulo - SP"
    BARBERSHOP_HOURS = "Terça a Sábado das 09h às 20h"
    
    # Configurações de Agendamento
    OPEN_HOUR = 9       # 09:00
    CLOSE_HOUR = 20     # 20:00 (último atendimento por volta das 19h / 19h30)
    SLOT_INTERVAL = 30  # Intervalo de 30 minutos para slots

