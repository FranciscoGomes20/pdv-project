# 🧾 Sistema de PDV - Versão 1.0.0

Sistema de Ponto de Venda (PDV) desenvolvido com Django e Docker.

---

## 🚀 Tecnologias Utilizadas

- Python 3.12+
- Django 5.2
- Django REST Framework
- PostgreSQL
- Docker
- Gunicorn
- Nginx
- HTML2PDF
- PyHanko

---

## 📦 Como Rodar Localmente com Docker

### 1. Clone o repositório
```
git clone https://github.com/FranciscoGomes20/pdv-project.git
cd pdv-project
```

### 2. Crie um arquivo .env na raiz do projeto:
```
DEBUG=True
SECRET_KEY=sua-secret-key-aqui
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1
POSTGRES_DB=pdv_db
POSTGRES_USER=pdv_user
POSTGRES_PASSWORD=senha123
```

### 3. Suba os containers:
```
docker-compose up --build
```
### 4. Crie o superusuário:
```
docker-compose exec web python manage.py createsuperuser
```
---
## 🔧 Endpoints da API

```/api/products/``` - CRUD de produtos

```/api/customers/``` - Clientes

```/api/sales/``` - Vendas e geração de notas

```/api/login/ ```- Autenticação com token (planejado)

```/admin/``` - Acesso ao painel de administração

---

## 📄 Funcionalidades (v1.0.0)

 Cadastro de produtos e clientes

 Registro de vendas

 Geração de nota fiscal em PDF

 Painel administrativo com Django Admin

 Docker configurado para rodar com PostgreSQL

---

## 🧠 Autor

#### Francisco Henrique Gomes
#### Desenvolvedor Backend Python
