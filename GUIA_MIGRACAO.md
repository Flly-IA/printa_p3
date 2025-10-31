# 🔄 GUIA DE MIGRAÇÃO - Script Local → API

Como migrar do seu script Python local (`build_cardapio_dinamico.py`) para a API REST completa.

---

## 📊 Comparação: Antes vs Depois

### ❌ ANTES (Script Local)

```bash
python build_cardapio_dinamico.py \
  --input teste_input.txt \
  --tplA tplA.cdr \
  --tplB tplB.cdr \
  --outdir saida \
  --font Arial \
  --size 10
```

**Limitações:**
- ❌ Execução manual
- ❌ Sem interface web
- ❌ Sem API para integração
- ❌ Sem processamento assíncrono
- ❌ Difícil escalar
- ❌ Sem histórico de jobs

### ✅ DEPOIS (API REST)

```bash
# Iniciar servidor uma vez
python start_api.py

# Fazer requisições de qualquer lugar
curl -X POST http://localhost:8000/cardapio/gerar \
  -F "file=@teste_input.txt" \
  -F "font=Arial" \
  -F "font_size=10"
```

**Vantagens:**
- ✅ Interface web bonita
- ✅ API REST completa
- ✅ Processamento assíncrono
- ✅ Fácil integração
- ✅ Escalável
- ✅ Histórico de jobs
- ✅ Deploy em cloud
- ✅ Multi-usuário

---

## 🔀 Estratégias de Migração

### Estratégia 1: Big Bang (Recomendada)
Migrar tudo de uma vez se:
- ✅ Poucos usuários (< 10)
- ✅ Downtime aceitável (1-2 horas)
- ✅ Ambiente simples

**Passos:**
1. Instalar API
2. Criar templates
3. Testar completamente
4. Substituir script por API
5. Treinar usuários

### Estratégia 2: Paralela
Rodar script e API juntos se:
- ✅ Muitos usuários (> 10)
- ✅ Zero downtime necessário
- ✅ Migração gradual

**Passos:**
1. Instalar API em paralelo
2. Migrar alguns usuários
3. Validar por 1-2 semanas
4. Migrar restante
5. Desativar script

### Estratégia 3: Híbrida
API chama script existente se:
- ✅ Quer API rapidamente
- ✅ Script muito customizado
- ✅ Tempo limitado

**Passos:**
1. Criar API wrapper
2. API chama script via subprocess
3. Melhorar gradualmente

---

## 📝 Checklist de Migração

### Fase 1: Preparação (1-2 dias)

#### 1.1 Inventário
- [ ] Listar todos os scripts em uso
- [ ] Documentar customizações
- [ ] Identificar dependências
- [ ] Listar usuários

#### 1.2 Ambiente
- [ ] Provisionar servidor (se cloud)
- [ ] Instalar Python 3.8+
- [ ] Instalar CorelDRAW
- [ ] Configurar rede/firewall

#### 1.3 Backup
- [ ] Backup do script atual
- [ ] Backup dos templates
- [ ] Backup dos outputs

### Fase 2: Instalação (2-4 horas)

#### 2.1 Instalar API
```bash
# Extrair arquivos
unzip cardapio_api_completo.zip
cd cardapio-api

# Instalar dependências
pip install -r requirements_api.txt

# Verificar instalação
python -c "import fastapi; print('OK')"
```

#### 2.2 Configurar Templates
```bash
# Opção A: Usar seus templates existentes
copy tplA.cdr templates\
copy tplB.cdr templates\

# Opção B: Criar novos templates
python create_templates.py
move tplA.cdr templates\
move tplB.cdr templates\
```

#### 2.3 Testar Localmente
```bash
# Iniciar API
python start_api.py

# Em outro terminal, testar
python test_api_client.py
```

### Fase 3: Migração (1 dia)

#### 3.1 Migrar Scripts Automatizados

**ANTES (Script):**
```python
import subprocess

subprocess.run([
    'python', 'build_cardapio_dinamico.py',
    '--input', 'input.txt',
    '--tplA', 'tplA.cdr',
    '--tplB', 'tplB.cdr',
    '--outdir', 'saida'
])
```

**DEPOIS (API):**
```python
import requests
import time

# Upload
with open('input.txt', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/cardapio/gerar',
        files={'file': f}
    )

job_id = response.json()['job_id']

# Aguardar conclusão
while True:
    status = requests.get(f'http://localhost:8000/cardapio/status/{job_id}').json()
    if status['status'] == 'completed':
        break
    time.sleep(2)

# Download
pdf = requests.get(f'http://localhost:8000/cardapio/download/{job_id}/pdf')
with open('saida/cardapio.pdf', 'wb') as f:
    f.write(pdf.content)
```

#### 3.2 Migrar Interface Desktop

**ANTES:** Linha de comando  
**DEPOIS:** Interface web

Simplesmente abra `web_client.html` no navegador!

#### 3.3 Migrar Integrações

**Sistema PHP:**
```php
// ANTES
exec('python build_cardapio_dinamico.py ...');

// DEPOIS
$ch = curl_init('http://localhost:8000/cardapio/gerar');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, ['file' => new CURLFile('input.txt')]);
$response = curl_exec($ch);
```

**Sistema JavaScript:**
```javascript
// ANTES
const { spawn } = require('child_process');
spawn('python', ['build_cardapio_dinamico.py', ...]);

// DEPOIS
const formData = new FormData();
formData.append('file', fileBlob);
fetch('http://localhost:8000/cardapio/gerar', {
    method: 'POST',
    body: formData
});
```

### Fase 4: Validação (1-2 dias)

#### 4.1 Testes Funcionais
- [ ] Upload de arquivo funciona
- [ ] Parsing correto
- [ ] PDF gerado corretamente
- [ ] PNG gerado corretamente
- [ ] Download funciona
- [ ] Todas as fontes funcionam
- [ ] Categorias corretas
- [ ] Preços corretos

#### 4.2 Testes de Performance
- [ ] Tempo de geração aceitável
- [ ] Múltiplas requisições simultâneas
- [ ] Uso de memória estável
- [ ] Uso de CPU aceitável

#### 4.3 Testes de Integração
- [ ] Todos os sistemas integrados funcionam
- [ ] APIs externas funcionam
- [ ] Webhooks (se aplicável) funcionam

### Fase 5: Deploy (1 dia)

#### 5.1 Produção
```bash
# Se local
python start_api.py

# Se Windows Service
nssm install CardapioAPI "C:\path\to\python.exe" "C:\path\to\start_api.py"
nssm start CardapioAPI

# Se cloud (Azure/AWS)
# Seguir README_API.md seção "Deploy em Servidor Windows"
```

#### 5.2 Monitoramento
- [ ] Health check funcionando
- [ ] Logs configurados
- [ ] Alertas configurados (opcional)

#### 5.3 Documentação
- [ ] Atualizar documentação interna
- [ ] Treinar equipe
- [ ] Criar runbook

### Fase 6: Desativação do Script (1 semana depois)

#### 6.1 Monitorar Uso
- [ ] Verificar se API está sendo usada
- [ ] Verificar se script antigo não está sendo chamado
- [ ] Resolver problemas restantes

#### 6.2 Desativar Script
- [ ] Renomear script antigo (.old)
- [ ] Mover para pasta archive/
- [ ] Remover de cronjobs/agendamentos

---

## 🔧 Resolver Incompatibilidades

### Problema 1: Argumentos Customizados

**Se seu script tem:**
```python
parser.add_argument("--meu-parametro")
```

**Solução:** Adicionar na API
```python
@app.post("/cardapio/gerar")
async def gerar_cardapio(
    ...,
    meu_parametro: Optional[str] = None
):
    ...
```

### Problema 2: Processamento Especial

**Se seu script faz:**
```python
# Processamento especial antes/depois
pre_processar(input_file)
gerar_cardapio(input_file)
pos_processar(output_file)
```

**Solução:** Integrar na função `process_cardapio`
```python
def process_cardapio(job_id, input_path, config):
    try:
        # Seu código aqui
        pre_processar(input_path)
        
        # Processamento padrão
        data = builder.parse_txt(input_path)
        ...
        
        # Seu código aqui
        pos_processar(output_path)
    except Exception as e:
        ...
```

### Problema 3: Templates Customizados

**Se você tem múltiplos templates:**

**Solução:** Adicionar seleção de template
```python
@app.post("/cardapio/gerar")
async def gerar_cardapio(
    ...,
    template: str = "default"  # ou "especial", "natal", etc
):
    if template == "especial":
        tpl_a = TEMPLATES_DIR / "tplA_especial.cdr"
        tpl_b = TEMPLATES_DIR / "tplB_especial.cdr"
    else:
        tpl_a = TEMPLATES_DIR / "tplA.cdr"
        tpl_b = TEMPLATES_DIR / "tplB.cdr"
```

---

## 📈 Medir Sucesso da Migração

### KPIs

| Métrica | Antes (Script) | Meta (API) | Atual |
|---------|---------------|-----------|-------|
| Tempo de geração | 30s | < 60s | ___ |
| Requisições/dia | N/A | 100+ | ___ |
| Uptime | 90% | 99.9% | ___ |
| Satisfação usuário | 7/10 | 9/10 | ___ |
| Tempo de integração | 1 semana | 1 dia | ___ |

### Feedback dos Usuários

Após 1 semana, perguntar:
- Interface web é mais fácil?
- API é mais rápida?
- Encontrou problemas?
- Sugestões de melhoria?

---

## 🚨 Plano de Rollback

Se algo der errado:

### Opção 1: Rollback Total (< 1 hora)
```bash
# Parar API
taskkill /IM python.exe /F

# Voltar ao script
# (já deve estar em backup)

# Restaurar cronjobs
# Restaurar integrações
```

### Opção 2: Rollback Parcial
```bash
# Manter API rodando
# Voltar alguns usuários para o script
# Investigar problema
# Corrigir
# Migrar novamente
```

---

## ✅ Checklist Final

Antes de considerar migração completa:

### Técnico
- [ ] API funcionando 99.9% do tempo por 1 semana
- [ ] Performance aceitável
- [ ] Sem erros críticos
- [ ] Backup automático funcionando

### Usuários
- [ ] Todos treinados
- [ ] Documentação atualizada
- [ ] Feedback positivo
- [ ] Ninguém usando script antigo

### Negócio
- [ ] Aprovação de stakeholders
- [ ] Orçamento para manutenção
- [ ] SLA definido
- [ ] Suporte técnico preparado

---

## 🎓 Treinamento de Usuários

### Sessão 1: Básico (30min)
1. Acessar `web_client.html`
2. Fazer upload de arquivo
3. Aguardar processamento
4. Baixar PDF

### Sessão 2: Intermediário (1h)
1. Usar API via curl/Postman
2. Integrar em scripts existentes
3. Verificar status de jobs
4. Limpar jobs antigos

### Sessão 3: Avançado (2h)
1. Entender arquitetura
2. Troubleshooting comum
3. Customizar templates
4. Adicionar funcionalidades

---

## 📞 Suporte Pós-Migração

### Semana 1
- Suporte dedicado full-time
- Monitoramento constante
- Feedback diário

### Semanas 2-4
- Suporte dedicado 8h/dia
- Monitoramento regular
- Feedback semanal

### Mês 2+
- Suporte padrão
- Monitoramento automático
- Feedback mensal

---

## 🎉 Sucesso da Migração!

Parabéns! Você migrou com sucesso do script local para uma API moderna e escalável.

**Próximos passos:**
1. Coletar métricas de uso
2. Otimizar performance
3. Adicionar funcionalidades
4. Escalar conforme necessário

**Lembre-se:**
- Manter backup do script antigo por 3-6 meses
- Documentar lições aprendidas
- Compartilhar sucesso com a equipe

---

**Boa sorte na sua migração! 🚀**
