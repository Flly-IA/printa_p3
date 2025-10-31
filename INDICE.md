# 📚 ÍNDICE DA DOCUMENTAÇÃO - API CARDÁPIO DINÂMICO

Bem-vindo à documentação completa da API de Cardápio Dinâmico!

---

## 🎯 Por Onde Começar?

### 🆕 Novo no projeto?
1. **[INICIO_RAPIDO.md](INICIO_RAPIDO.md)** - Setup em 5 minutos
2. **[README_API.md](README_API.md)** - Documentação completa

### 💻 Vai programar?
1. **[EXEMPLOS_INTEGRACAO.md](EXEMPLOS_INTEGRACAO.md)** - Código em 10+ linguagens
2. **[ARQUITETURA.md](ARQUITETURA.md)** - Como funciona por dentro

### 🐛 Problemas?
1. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Soluções para erros comuns

---

## 📖 Documentos Disponíveis

### 1. 🚀 INICIO_RAPIDO.md
**Para:** Iniciantes  
**Tempo:** 5 minutos  
**Conteúdo:**
- Setup rápido do zero
- Checklist de instalação
- Uso básico
- Deploy em produção (resumo)
- Problemas comuns (resumo)

### 2. 📘 README_API.md
**Para:** Desenvolvedores  
**Tempo:** 30 minutos  
**Conteúdo:**
- Requisitos completos
- Instalação detalhada
- Documentação de todos os endpoints
- Estrutura de pastas
- Formato do arquivo de entrada
- Deploy em cloud (detalhado)
- Segurança e autenticação
- Monitoramento e logs
- Troubleshooting básico

### 3. 🏗️ ARQUITETURA.md
**Para:** Arquitetos / DevOps  
**Tempo:** 20 minutos  
**Conteúdo:**
- Fluxo de dados completo
- Diagramas visuais
- Ciclo de vida de requisições
- Estrutura de pastas
- Endpoints detalhados
- Segurança avançada
- Escalabilidade (workers, filas, load balancer)
- Casos de uso
- Performance e otimizações

### 4. 🔗 EXEMPLOS_INTEGRACAO.md
**Para:** Desenvolvedores (todas as linguagens)  
**Tempo:** 10 minutos por exemplo  
**Conteúdo:**
- **JavaScript/Node.js:** Fetch API, Axios
- **Python:** Requests (sync), HTTPX (async)
- **Java:** OkHttp
- **C#/.NET:** HttpClient
- **PHP:** cURL
- **Rust:** Reqwest
- **Webhook:** Callbacks em vez de polling

### 5. 🔧 TROUBLESHOOTING.md
**Para:** Quando algo der errado  
**Tempo:** 5-30 minutos (depende do problema)  
**Conteúdo:**
- 10 problemas mais comuns
- CorelDRAW não inicializa
- Módulos não encontrados
- Templates faltando
- Porta em uso
- Erros de processamento
- Timeout
- Fontes não encontradas
- Permissões
- Erros de export
- API não responde
- Script de diagnóstico completo
- Logs e debugging
- Testes unitários
- Reset completo

---

## 🗂️ Arquivos do Projeto

### 📝 Código Python

#### `api_cardapio.py` (Principal)
API FastAPI com todos os endpoints:
- `/health` - Health check
- `/cardapio/gerar` - Upload e geração
- `/cardapio/status/{job_id}` - Status do job
- `/cardapio/download/{job_id}/{file_type}` - Download
- `/cardapio/listar` - Listar jobs
- `/cardapio/limpar/{job_id}` - Remover job

#### `build_cardapio_dinamico.py` (Motor)
Processamento do cardápio:
- Parse de arquivo TXT
- Automação do CorelDRAW via COM
- Geração de PDF/PNG/CDR
- Auditoria (JSON, CSV)

#### `create_templates.py` (Utilitário)
Cria templates minimalistas tplA.cdr e tplB.cdr

#### `start_api.py` (Inicializador)
Script que verifica dependências e inicia a API

#### `test_api_client.py` (Teste)
Cliente Python completo para testar a API

### 🌐 Interface Web

#### `web_client.html`
Interface web bonita e funcional:
- Upload de arquivo
- Seleção de fonte e tamanho
- Acompanhamento de status
- Download dos arquivos
- 100% standalone (sem frameworks)

### 📦 Configuração

#### `requirements_api.txt`
Todas as dependências Python:
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
pywin32>=306 (Windows)
pydantic>=2.0.0
aiofiles>=23.2.1
```

#### `deploy_windows.bat`
Script batch para deploy automatizado no Windows

---

## 🎓 Guias de Uso por Cenário

### Cenário 1: Restaurante Individual
**Objetivo:** Gerar cardápios manualmente via interface web

**Passos:**
1. Ler [INICIO_RAPIDO.md](INICIO_RAPIDO.md)
2. Instalar localmente
3. Usar `web_client.html`
4. Opcional: Ler [TROUBLESHOOTING.md](TROUBLESHOOTING.md) se houver problemas

### Cenário 2: Integração com Sistema Existente
**Objetivo:** Integrar API em aplicação PHP/JS/Python/etc

**Passos:**
1. Ler seção "Endpoints" em [README_API.md](README_API.md)
2. Ver exemplo da sua linguagem em [EXEMPLOS_INTEGRACAO.md](EXEMPLOS_INTEGRACAO.md)
3. Implementar chamadas HTTP
4. Tratar erros conforme [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Cenário 3: Deploy em Nuvem (Azure/AWS)
**Objetivo:** Hospedar API em servidor Windows na cloud

**Passos:**
1. Ler seção "Deploy em Servidor Windows" em [README_API.md](README_API.md)
2. Entender arquitetura em [ARQUITETURA.md](ARQUITETURA.md)
3. Criar VM Windows
4. Executar `deploy_windows.bat`
5. Configurar firewall e DNS
6. Opcional: Adicionar autenticação (ver [README_API.md](README_API.md))

### Cenário 4: Processamento em Lote
**Objetivo:** Gerar 100+ cardápios automaticamente

**Passos:**
1. Ver exemplo Python em [EXEMPLOS_INTEGRACAO.md](EXEMPLOS_INTEGRACAO.md)
2. Criar script de loop
3. Implementar fila (opcional) conforme [ARQUITETURA.md](ARQUITETURA.md)
4. Monitorar performance

### Cenário 5: Plataforma SaaS Multi-Tenant
**Objetivo:** Construir plataforma com múltiplos clientes

**Passos:**
1. Estudar [ARQUITETURA.md](ARQUITETURA.md) seção "Escalabilidade"
2. Implementar autenticação JWT (ver [README_API.md](README_API.md))
3. Adicionar Redis/Celery para fila
4. Implementar billing por job
5. Configurar load balancer

---

## 🛠️ Ferramentas Incluídas

### Scripts Utilitários

#### `diagnostic.py` (Criar a partir de TROUBLESHOOTING.md)
Diagnóstico completo do sistema:
```bash
python diagnostic.py
```
Verifica: Python, módulos, CorelDRAW, templates, pastas

#### `deploy_windows.bat`
Deploy automatizado:
```bash
deploy_windows.bat
```
Instala dependências, cria estrutura, verifica CorelDRAW

### Templates

#### `templates/tplA.cdr`
Template para cardápios pequenos (≤30 itens)
- 1 coluna
- A4 portrait
- Título centralizado

#### `templates/tplB.cdr`
Template para cardápios grandes (>30 itens)
- 2 colunas
- A4 portrait
- Título centralizado

---

## 📊 Matriz de Referência Rápida

| Preciso de... | Ver documento | Seção |
|---------------|---------------|-------|
| Instalar rapidamente | INICIO_RAPIDO.md | "Setup Rápido" |
| Documentação da API | README_API.md | "Endpoints" |
| Código Python | EXEMPLOS_INTEGRACAO.md | "Python" |
| Código JavaScript | EXEMPLOS_INTEGRACAO.md | "JavaScript" |
| Código Java | EXEMPLOS_INTEGRACAO.md | "Java" |
| Código C# | EXEMPLOS_INTEGRACAO.md | "C#" |
| Código PHP | EXEMPLOS_INTEGRACAO.md | "PHP" |
| Deploy Azure | README_API.md | "Deploy em Servidor Windows" |
| Deploy AWS | README_API.md | "Deploy em Servidor Windows" |
| Entender arquitetura | ARQUITETURA.md | Tudo |
| CorelDRAW não funciona | TROUBLESHOOTING.md | "Problema 1" |
| Erro de módulo | TROUBLESHOOTING.md | "Problema 2" |
| Porta ocupada | TROUBLESHOOTING.md | "Problema 4" |
| Timeout | TROUBLESHOOTING.md | "Problema 6" |
| Adicionar autenticação | README_API.md | "Segurança" |
| Webhook em vez de polling | EXEMPLOS_INTEGRACAO.md | "Webhook" |
| Escalabilidade | ARQUITETURA.md | "Escalabilidade" |
| Múltiplos workers | README_API.md | "Monitoramento" |

---

## 🎯 Checklist Completo

Antes de entrar em produção, verifique:

### ✅ Instalação
- [ ] Python 3.8+ instalado
- [ ] CorelDRAW instalado e licenciado
- [ ] Todas as dependências instaladas (`pip install -r requirements_api.txt`)
- [ ] Templates criados e na pasta `templates/`
- [ ] API inicia sem erros (`python start_api.py`)
- [ ] Health check respondendo (`GET /health`)

### ✅ Funcionalidade
- [ ] Upload de arquivo funciona
- [ ] Parsing correto (verificar `parsed.json`)
- [ ] CorelDRAW abre e processa
- [ ] PDF gerado corretamente
- [ ] PNG gerado corretamente
- [ ] Download funciona
- [ ] Jobs são listados
- [ ] Limpeza de jobs funciona

### ✅ Produção
- [ ] Servidor Windows dedicado
- [ ] Firewall configurado (porta 8000)
- [ ] HTTPS configurado (Nginx + Certbot)
- [ ] Autenticação implementada
- [ ] Logs configurados
- [ ] Monitoramento ativo
- [ ] Backup automático dos outputs/
- [ ] Rate limiting configurado
- [ ] Documentação atualizada

### ✅ Segurança
- [ ] Senhas não hardcoded
- [ ] HTTPS obrigatório
- [ ] Rate limiting ativo
- [ ] CORS configurado corretamente
- [ ] Inputs validados
- [ ] Arquivos temp limpos periodicamente
- [ ] Permissões de pasta corretas

---

## 🆘 Suporte e Comunidade

### Reportar Bugs
1. Executar `python diagnostic.py > diagnostico.txt`
2. Copiar mensagem de erro
3. Abrir issue no GitHub com:
   - Descrição do problema
   - Arquivo `diagnostico.txt`
   - Logs relevantes
   - Passos para reproduzir

### Contribuir
Pull requests são bem-vindos!
1. Fork do repositório
2. Criar branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push (`git push origin feature/nova-funcionalidade`)
5. Abrir Pull Request

### Dúvidas
- 📧 Email: suporte@exemplo.com
- 💬 Discord: [Link]
- 📋 GitHub Issues: [Link]
- 📚 Wiki: [Link]

---

## 📜 Licença

MIT License - Veja LICENSE.md para detalhes

---

## 🎉 Próximos Passos

Depois de ler esta documentação:

1. **Começar agora:** [INICIO_RAPIDO.md](INICIO_RAPIDO.md)
2. **Aprender mais:** [README_API.md](README_API.md)
3. **Ver código:** [EXEMPLOS_INTEGRACAO.md](EXEMPLOS_INTEGRACAO.md)
4. **Entender profundamente:** [ARQUITETURA.md](ARQUITETURA.md)
5. **Resolver problemas:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Boa sorte com seu projeto! 🚀**

*Última atualização: 30 de outubro de 2025*
