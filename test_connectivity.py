#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar conectividade da API
"""
import socket
import requests
import sys

def get_all_ips():
    """Pega todos os IPs da máquina"""
    hostname = socket.gethostname()

    try:
        # IP principal
        primary_ip = socket.gethostbyname(hostname)

        # Todos os IPs
        all_ips = socket.getaddrinfo(hostname, None)
        unique_ips = set()
        for ip_info in all_ips:
            ip = ip_info[4][0]
            if ':' not in ip:  # Ignorar IPv6
                unique_ips.add(ip)

        return list(unique_ips)
    except Exception as e:
        print(f"❌ Erro ao obter IPs: {e}")
        return []

def test_url(url, timeout=5):
    """Testa se uma URL responde"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, f"Status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Conexão recusada (API não está rodando?)"
    except requests.exceptions.Timeout:
        return False, "Timeout (firewall bloqueando?)"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("🔍 TESTE DE CONECTIVIDADE DA API")
    print("=" * 60)
    print()

    # 1. Mostrar IPs
    print("1️⃣  ENDEREÇOS IP DESTA MÁQUINA:")
    print("-" * 60)
    ips = get_all_ips()
    for ip in ips:
        if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172."):
            print(f"   ✅ {ip} (IP LOCAL - use este para acesso externo)")
        elif ip.startswith("127."):
            print(f"   ℹ️  {ip} (localhost)")
        else:
            print(f"   ⚠️  {ip} (IP público ou outro)")
    print()

    # 2. Testar localhost
    print("2️⃣  TESTE: http://localhost:8000/ping")
    print("-" * 60)
    success, result = test_url("http://localhost:8000/ping")
    if success:
        print(f"   ✅ SUCESSO!")
        print(f"   📝 Resposta: {result.get('message', 'N/A')}")
        print(f"   🖥️  Servidor: {result.get('server', {}).get('hostname', 'N/A')}")
    else:
        print(f"   ❌ FALHOU: {result}")
        print(f"   💡 Dica: Certifique-se que a API está rodando (python api_cardapio.py)")
        sys.exit(1)
    print()

    # 3. Testar cada IP local
    print("3️⃣  TESTANDO CADA IP LOCAL:")
    print("-" * 60)
    local_ips = [ip for ip in ips if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172.")]

    if not local_ips:
        print("   ⚠️  Nenhum IP local encontrado!")
        print("   💡 Sua VM pode estar em modo NAT. Configure Port Forwarding ou mude para Bridge.")
    else:
        for ip in local_ips:
            url = f"http://{ip}:8000/ping"
            print(f"   Testando: {url}")
            success, result = test_url(url)
            if success:
                print(f"   ✅ FUNCIONA! Use este no n8n: {url}")
            else:
                print(f"   ❌ Falhou: {result}")
            print()

    # 4. Resumo
    print("=" * 60)
    print("📋 RESUMO:")
    print("=" * 60)
    if local_ips:
        print(f"✅ API está rodando")
        print(f"✅ IPs locais encontrados: {', '.join(local_ips)}")
        print()
        print("🎯 PRÓXIMOS PASSOS:")
        print("1. Use um dos IPs acima no n8n")
        print("2. Certifique-se que n8n e esta VM estão na mesma rede")
        print("3. Se ainda não funcionar, execute: abrir_firewall.bat (como admin)")
    else:
        print(f"⚠️  API está rodando, mas sem IPs locais detectados")
        print()
        print("🎯 AÇÕES NECESSÁRIAS:")
        print("1. Configure sua VM em modo Bridge (recomendado)")
        print("   OU")
        print("2. Configure Port Forwarding na VM (se usar NAT)")
        print()
        print("📖 Consulte: SOLUCAO_ACESSO_EXTERNO.md")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Teste cancelado pelo usuário")
        sys.exit(0)
