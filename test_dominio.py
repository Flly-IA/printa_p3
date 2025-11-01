#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testar se o domínio está funcionando
"""
import socket
import sys

def test_domain():
    domain = "windows-printa.lucrativa.app"

    print("=" * 60)
    print("🔍 TESTE DE DOMÍNIO")
    print("=" * 60)
    print()

    # 1. Resolver DNS
    print(f"1️⃣  RESOLVENDO DNS: {domain}")
    print("-" * 60)
    try:
        ip = socket.gethostbyname(domain)
        print(f"✅ Domínio resolve para: {ip}")

        if ip == "190.102.40.94":
            print("✅ IP correto!")
        else:
            print(f"⚠️  IP diferente do esperado (esperado: 190.102.40.94)")
    except socket.gaierror:
        print(f"❌ Não foi possível resolver o domínio")
        sys.exit(1)
    print()

    # 2. Testar conexão
    print(f"2️⃣  TESTANDO CONEXÕES:")
    print("-" * 60)

    ports_to_test = [80, 443, 8000]

    for port in ports_to_test:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        result = sock.connect_ex((ip, port))

        if result == 0:
            print(f"✅ Porta {port}: ABERTA")
        else:
            print(f"❌ Porta {port}: FECHADA")

        sock.close()

    print()

    # 3. Recomendações
    print("=" * 60)
    print("📋 RECOMENDAÇÕES:")
    print("=" * 60)

    # Verificar se porta 80 ou 443 está aberta
    sock80 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock80.settimeout(5)
    port80_open = sock80.connect_ex((ip, 80)) == 0
    sock80.close()

    sock443 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock443.settimeout(5)
    port443_open = sock443.connect_ex((ip, 443)) == 0
    sock443.close()

    sock8000 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock8000.settimeout(5)
    port8000_open = sock8000.connect_ex((ip, 8000)) == 0
    sock8000.close()

    if port80_open or port443_open:
        print("✅ Porta 80 ou 443 está aberta!")
        print("🎯 Teste com:")
        if port80_open:
            print(f"   http://{domain}/ping")
        if port443_open:
            print(f"   https://{domain}/ping")
    elif port8000_open:
        print("⚠️  Apenas porta 8000 está aberta")
        print("🎯 Teste com:")
        print(f"   http://{domain}:8000/ping")
        print()
        print("💡 RECOMENDAÇÃO: Configure port forwarding de 80→8000")
        print("   Assim você pode usar sem :8000 na URL")
    else:
        print("❌ Nenhuma porta está aberta!")
        print()
        print("🔧 AÇÕES NECESSÁRIAS:")
        print("1. Configure Port Forwarding no roteador")
        print("2. Libere o firewall na VM")
        print("3. Certifique-se que a API está rodando")

    print()

if __name__ == "__main__":
    try:
        test_domain()
    except KeyboardInterrupt:
        print("\n\n❌ Teste cancelado")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
