"""
Script de Inicialização e Povoamento do Banco de Dados (Seed Data).
Cria o usuário administrador padrão e pacotes de serviço iniciais.
"""

from datetime import datetime, timedelta
from models import db, User, ServicePackage, Appointment

def seed_database():
    """Popula o banco de dados com dados iniciais se estiver vazio."""
    # 1. Usuário Administrador
    if not User.query.first():
        admin = User(
            username='admin',
            name='Carlos Barbeiro (Dono)',
            email='contato@barbershopmanager.com.br'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print(" -> Administrador criado: admin / admin123")
        
    # 2. Pacotes de Serviços
    if not ServicePackage.query.first():
        packages = [
            ServicePackage(
                name="Corte Tradicional Masculino",
                description="Corte com tesoura e máquina, alinhamento dos fios, acabamento milimétrico na navalha e finalização com pomada modeladora premium.",
                price=55.00,
                duration_minutes=45,
                is_active=True
            ),
            ServicePackage(
                name="Barba Terapia com Toalha Quente",
                description="Modelagem e alinhamento de barba com óleos essenciais, esfoliação facial, toalha quente aromática e pós-barba refrescante.",
                price=50.00,
                duration_minutes=40,
                is_active=True
            ),
            ServicePackage(
                name="Combo Clássico: Cabelo + Barba",
                description="A combinação perfeita e mais pedida! Corte de cabelo completo somado à experiência relaxante da barba terapia com toalha quente.",
                price=95.00,
                duration_minutes=75,
                is_active=True
            ),
            ServicePackage(
                name="Combo Supremo VIP: Cabelo, Barba & Sobrancelha",
                description="Experiência completa da barbearia: corte executivo ou degradê, barba completa, design de sobrancelha na navalha e massagem capilar.",
                price=120.00,
                duration_minutes=90,
                is_active=True
            ),
            ServicePackage(
                name="Camuflagem de Fios Grisalhos / Pigmentação",
                description="Tonalização suave e natural para disfarçar fios brancos na barba ou cabelo com aspecto rejuvenescido e moderno.",
                price=75.00,
                duration_minutes=50,
                is_active=True
            )
        ]
        db.session.add_all(packages)
        db.session.commit()
        print(" -> 5 Pacotes de serviços iniciais criados com sucesso!")
        
        # 3. Alguns agendamentos de exemplo para demonstrar o painel imediatamente
        today = datetime.now()
        pkg_combo = ServicePackage.query.filter_by(name="Combo Clássico: Cabelo + Barba").first()
        pkg_corte = ServicePackage.query.filter_by(name="Corte Tradicional Masculino").first()
        pkg_barba = ServicePackage.query.filter_by(name="Barba Terapia com Toalha Quente").first()
        pkg_vip = ServicePackage.query.filter_by(name="Combo Supremo VIP: Cabelo, Barba & Sobrancelha").first()

        sample_appts = [
            Appointment(
                client_name="Lucas Albuquerque",
                client_phone="(11) 99123-4567",
                client_email="lucas.albuquerque@email.com",
                package_id=pkg_combo.id if pkg_combo else 1,
                appointment_date=today.replace(hour=14, minute=30, second=0, microsecond=0),
                status="Confirmado",
                notification_sent=False,
                notes="Prefere corte degrade navalhado bem baixo nas laterais."
            ),
            Appointment(
                client_name="Rodrigo Santoro",
                client_phone="(11) 98765-1122",
                client_email="rodrigo.s@email.com",
                package_id=pkg_barba.id if pkg_barba else 2,
                appointment_date=today.replace(hour=16, minute=0, second=0, microsecond=0),
                status="Pendente",
                notification_sent=False,
                notes="Primeira vez na barbearia. Foco na linha da bochecha."
            ),
            Appointment(
                client_name="Matheus Ferreira",
                client_phone="(11) 97654-3210",
                client_email="matheus.f@email.com",
                package_id=pkg_vip.id if pkg_vip else 3,
                appointment_date=today.replace(hour=17, minute=30, second=0, microsecond=0),
                status="Confirmado",
                notification_sent=False,
                notes="Cliente VIP há 2 anos."
            ),
            Appointment(
                client_name="Gabriel Medina",
                client_phone="(11) 99887-7665",
                client_email="gabriel.m@email.com",
                package_id=pkg_corte.id if pkg_corte else 1,
                appointment_date=(today + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0),
                status="Pendente",
                notification_sent=False,
                notes="Corte tesoura no topo."
            )
        ]
        db.session.add_all(sample_appts)
        db.session.commit()
        print(" -> Agendamentos de demonstração criados com sucesso!")
        
    db.session.commit()

