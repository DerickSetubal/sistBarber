# 💈 BarberShop Manager

Um sistema web completo, moderno e responsivo para gestão de agendamentos em barbearias de alto padrão. Desenvolvido em **Python (Flask)** com persistência em **SQLite (SQLAlchemy)**, autenticação via **Flask-Login** e interface visual elegante com **Tailwind CSS** em Dark Mode com detalhes dourados clássicos.

---

## 🔗 Links Rápidos de Acesso ao Sistema

Com o servidor em execução (`python app.py`), utilize os links diretos abaixo:

| Seção | Link Direto | Descrição |
| :--- | :--- | :--- |
| 🌐 **Página Inicial (Landing Page)** | [http://127.0.0.1:5000/](http://127.0.0.1:5000/) | Apresentação da barbearia, galeria de cortes e pacotes dinâmicos |
| 📅 **Agendamento Online (Wizard)** | [http://127.0.0.1:5000/agendar](http://127.0.0.1:5000/agendar) | Fluxo interativo em 3 etapas para reservar horário |
| 🔑 **Login do Proprietário** | [http://127.0.0.1:5000/login](http://127.0.0.1:5000/login) | Acesso restrito ao painel com proteção por senha |
| 📊 **Dashboard Administrativo** | [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin) | Métricas diárias, faturamento do mês e feed de lembretes |
| 📋 **Gestão de Agendamentos** | [http://127.0.0.1:5000/admin/agendamentos](http://127.0.0.1:5000/admin/agendamentos) | Tabela interativa com filtros de data, status e busca instantânea |
| ✂️ **Gestão de Pacotes e Preços (CRUD)** | [http://127.0.0.1:5000/admin/pacotes](http://127.0.0.1:5000/admin/pacotes) | Adicionar novos serviços, editar preços e alterar durações |

### 🔐 Credenciais Padrão do Painel
- **Usuário:** `admin`
- **Senha:** `admin123`

---

## 📖 Descrição Geral do Projeto

O **BarberShop Manager** foi projetado para atender tanto às necessidades do cliente final (proporcionando uma experiência de agendamento ágil, sem necessidade de download de aplicativo) quanto às demandas operacionais do dono da barbearia (visão de faturamento, agenda em tempo real e controle total de catálogo de serviços).

### 1. Área Pública (Experiência do Cliente)
- **Landing Page de Conversão:**
  - Identidade visual refinada com tema escuro elegante (preto ônix, ardósia e dourado `#D4AF37`).
  - Vitrine de diferenciais: Mestres barbeiros visagistas, open bar (cerveja artesanal/café expresso), barboterapia com toalha quente e ozônio.
  - Catálogo de serviços puxado dinamicamente do banco de dados (preços e tempos reais).
  - Galeria de estilos (Fade, Pompadour, Navalhado, Pigmentação de barba).
- **Wizard de Agendamento em 3 Passos:**
  - **Passo 1 (Pacote):** Seleção de serviço com indicação de duração e preço.
  - **Passo 2 (Data e Hora):** Calendário com atalhos (*Hoje*, *Amanhã*) e slots de horários gerados em tempo real pela API para evitar conflito com horários já ocupados.
  - **Passo 3 (Contato):** Formulário simples com máscara de telefone/WhatsApp e campo para preferências especiais.
- **Voucher de Confirmação:**
  - Tela de sucesso com código de protocolo do agendamento.
  - Botão de envio automático do voucher para o **WhatsApp oficial da barbearia**.
  - Botão de sincronização em 1 clique com o **Google Agenda**.

### 2. Área Administrativa (Gestão do Dono)
- **Métricas do Dashboard:**
  - Quantidade de atendimentos marcados para hoje.
  - Faturamento estimado acumulado do mês corrente (soma dos pacotes confirmados/concluídos).
  - Total de agendamentos pendentes de confirmação.
  - Histórico total de cortes realizados.
- **Gestão de Agendamentos:**
  - Tabela com filtros de data: *Hoje*, *Amanhã*, *Esta Semana*, *Este Mês*, *Todos*.
  - Filtro por status: *Pendente*, *Confirmado*, *Concluído*, *Cancelado*.
  - Busca rápida no frontend por nome ou número de telefone.
  - Ações com 1 clique para aprovar, concluir ou cancelar horários.
  - Link direto para iniciar conversa no WhatsApp com o cliente.
- **Gestão de Preços e Pacotes (CRUD Completo):**
  - **Criar:** Formulário modal para inclusão de novos serviços (nome, descrição, preço em R$, duração em minutos).
  - **Editar:** Atualização imediata de valores e descrições, refletindo no mesmo instante na landing page e na área de agendamento do cliente.
  - **Ativar/Desativar:** Ocultar pacotes do público temporariamente sem perder o histórico financeiro.
  - **Excluir:** Remoção com validação de segurança.

### 3. Sistema de Notificações / Lembretes (Simulado)
- Módulo [`notifications.py`](file:///C:/Users/User/.gemini/antigravity/scratch/barbershop_manager/notifications.py) com função automatizada que identifica agendamentos pendentes nas próximas 24 horas.
- Simula o envio de mensagens pelo WhatsApp/SMS para o **Cliente** (com lembrete de pontualidade e endereço) e para o **Dono** (com resumo do próximo cliente na cadeira).
- Registra logs detalhados e estilizados no terminal/console.
- Alimenta um feed visual de disparos dentro do próprio painel do administrador.
- Inclui botão de disparo forçado individual em cada linha da tabela de agendamentos.

---

## 📂 Arquitetura do Código

```
barbershop_manager/
│
├── app.py                      # Aplicação Flask, rotas públicas, admin e APIs
├── config.py                   # Configurações gerais (Secret key, SQLite, horários)
├── models.py                   # Modelos do banco (User, ServicePackage, Appointment)
├── notifications.py            # Motor de simulação de disparos de lembretes
├── seed_data.py                # Povoamento inicial automático do banco
├── requirements.txt            # Dependências Python
├── README.md                   # Documentação detalhada
│
├── static/
│   └── css/
│       └── style.css           # Estilos e efeitos visuais complementares
│
└── templates/
    ├── base.html               # Template base com Tailwind CDN e FontAwesome 6
    ├── index.html              # Landing Page pública com catálogo dinâmico
    ├── agendar.html            # Wizard de agendamento em 3 etapas
    ├── confirmacao.html        # Tela de voucher e confirmação
    ├── login.html              # Tela de autenticação do proprietário
    └── admin/
        ├── base_admin.html     # Layout mestre do painel com navegação
        ├── dashboard.html      # Métricas, agenda de hoje e feed de lembretes
        ├── agendamentos.html   # Tabela interativa com filtros e busca
        └── pacotes.html        # CRUD de pacotes, preços e durações
```

---

## 🛠️ Como Executar Localmente

### 1. Instalar as Dependências
Abra o terminal na pasta do projeto e execute:
```bash
pip install -r requirements.txt
```

### 2. Iniciar o Servidor
```bash
python app.py
```

O terminal exibirá a confirmação de inicialização:
```
============================================================
 💈 BarberShop Manager Iniciando...
 🌐 URL Pública: http://127.0.0.1:5000
 🔑 Painel Admin: http://127.0.0.1:5000/login
 👤 Usuário: admin  |  Senha: admin123
============================================================
 * Running on http://127.0.0.1:5000
```

---

## 🧪 Como Testar as Funcionalidades

1. **Testar Agendamento do Cliente:**
   - Acesse [http://127.0.0.1:5000/agendar](http://127.0.0.1:5000/agendar).
   - Escolha o pacote, selecione a data e o horário vago.
   - Digite seu nome e telefone e confirme. Você verá o voucher com o link do WhatsApp!
2. **Testar Alteração de Preços em Tempo Real:**
   - Acesse [http://127.0.0.1:5000/login](http://127.0.0.1:5000/login) com `admin` / `admin123`.
   - Acesse **Preços & Pacotes** ([http://127.0.0.1:5000/admin/pacotes](http://127.0.0.1:5000/admin/pacotes)).
   - Edite o preço de qualquer serviço (ex: altere de R$ 55,00 para R$ 60,00).
   - Abra a página inicial [http://127.0.0.1:5000/](http://127.0.0.1:5000/) e veja o novo preço atualizado instantaneamente!
3. **Testar Disparo de Lembretes:**
   - No Dashboard ([http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)), clique no botão **"Testar Disparo de Lembretes (24h)"**.
   - Veja o alerta visual de confirmação, o feed de lembretes atualizado e o log detalhado impresso no terminal!
