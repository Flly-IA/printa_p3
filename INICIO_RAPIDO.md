# 🚀 Início Rápido - Acessar API Externamente

## ⚡ 3 Passos Simples

### 1️⃣ Execute o Diagnóstico

```cmd
python test_connectivity.py
```

Este script vai:
- ✅ Mostrar todos os IPs da sua VM
- ✅ Testar se a API está respondendo
- ✅ Indicar qual IP usar no n8n

### 2️⃣ Abra o Firewall (como Administrador)

**Botão direito** em `abrir_firewall.bat` > **Executar como administrador**

### 3️⃣ Use o IP Correto no n8n

O script do passo 1 vai mostrar algo como:

```
✅ 192.168.1.100 (IP LOCAL - use este para acesso externo)
```

No n8n, use:
```
http://192.168.1.100:8000/ping
```

---

## ❌ Se Não Funcionar

### Problema: "Nenhum IP local encontrado"

**Sua VM está em modo NAT.** Você tem 2 opções:

#### Opção A: Mudar para Bridge (Recomendado)

**VirtualBox:**
1. Desligue a VM
2. VirtualBox > Configurações > Rede
3. Conectado a: **Placa em modo Bridge**
4. Ligue a VM novamente

**VMware:**
1. Desligue a VM  
2. VM Settings > Network Adapter
3. Selecione: **Bridged**
4. Ligue a VM novamente

#### Opção B: Port Forwarding (se não puder mudar para Bridge)

Use o IP do seu PC HOST (não da VM): `http://IP_DO_HOST:8000`

---

## 🧪 Teste Rápido

Na VM: `curl http://localhost:8000/ping`

De outra máquina: `curl http://192.168.x.x:8000/ping`

Navegador: `http://192.168.x.x:8000/docs`
