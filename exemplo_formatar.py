# -*- coding: utf-8 -*-
"""
Exemplo de uso do endpoint /cardapio/formatar
Envia texto direto para a API sem precisar criar arquivo
"""

import requests
import json
import time

# Configuração da API
API_URL = "http://localhost:8000"

# Texto do cardápio (exemplo fornecido)
texto_cardapio = """RELATÓRIO DE PREÇOS Lula Bar

*Cervejas 600ml*
Brahma Chopp (600ml) - R$ 11,00
Corona (600ml) - R$ 17,00
Stella Artois (600ml) - R$ 14,00
Original (600ml) - R$ 13,00
Spaten (600ml) - R$ 13,00
Skol (600ml) - R$ 11,00
Heineken (600ml) - R$ 16,00
Amstel (600ml) - R$ 12,00
Antarctica (600ml) - R$ 11,00

*Cervejas Long Neck*
Corona (long Neck) - R$ 10,00
Stella Pure Gold (long Neck) - R$ 9,00
Stella Artois (long Neck) - R$ 8,00
Heineken (long Neck) - R$ 9,00
Spaten (long Neck) - R$ 8,00

*Cervejas Litrinho*
Brahma Chopp (300ml) - R$ 4,50
Original (300ml) - R$ 5,50
Antarctica Pilsen (300ml) - R$ 4,50

*Cervejas Lata*
Brahma Chopp Duplo Malte (lata 350ml) - R$ 5,50
Brahma Chopp (lata 269ml) - R$ 3,50
Skol (lata 350ml) - R$ 4,00
Heineken (lata 350ml) - R$ 7,00
Amstel (lata 350ml) - R$ 5,50
Heineken (lata 269ml) - R$ 5,50
Amstel (lata 269ml) - R$ 4,50
Antarctica (lata 269ml) - R$ 3,50

*Refrigerantes*
Guaraná Antarctica (lata 350ml) - R$ 4,50
Guaraná Antarctica (2L) - R$ 10,00
Coca Cola (2L) - R$ 11,00

*Outros*
Água (500ml) - R$ 3,00
Suco Natural - R$ 8,00"""

def formatar_cardapio():
    """
    Envia o texto do cardápio para formatação
    """
    print("=" * 60)
    print("🚀 TESTANDO ENDPOINT /cardapio/formatar")
    print("=" * 60)

    # Dados para enviar
    payload = {
        "id": "lula-bar-001",  # ID customizado
        "text": texto_cardapio,
        "font": "Arial",
        "font_size": 10.0
    }

    print(f"\n📤 Enviando requisição para {API_URL}/cardapio/formatar")
    print(f"   ID: {payload['id']}")
    print(f"   Fonte: {payload['font']}")
    print(f"   Tamanho: {payload['font_size']}pt")
    print(f"   Tamanho do texto: {len(texto_cardapio)} caracteres")

    try:
        # Enviar requisição
        response = requests.post(
            f"{API_URL}/cardapio/formatar",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            job_id = result["job_id"]
            print(f"\n✅ Requisição aceita!")
            print(f"   Job ID: {job_id}")
            print(f"   Status: {result['status']}")
            print(f"   Mensagem: {result['message']}")

            # Aguardar processamento
            print(f"\n⏳ Aguardando processamento...")
            return monitorar_status(job_id)
        else:
            print(f"\n❌ Erro: {response.status_code}")
            print(f"   {response.text}")
            return False

    except Exception as e:
        print(f"\n❌ Erro ao conectar: {e}")
        return False

def monitorar_status(job_id):
    """
    Monitora o status do processamento
    """
    max_tentativas = 60  # 60 segundos

    for i in range(max_tentativas):
        try:
            response = requests.get(f"{API_URL}/cardapio/status/{job_id}")

            if response.status_code == 200:
                status = response.json()

                if status["status"] == "completed":
                    print(f"\n✅ Processamento concluído!")

                    # Mostrar URL do Supabase se disponível
                    if status.get("supabase_url"):
                        print(f"\n🌐 SUPABASE:")
                        print(f"   URL Pública: {status['supabase_url']}")

                    print(f"\n📦 Arquivos gerados:")
                    for tipo, nome in status.get("files", {}).items():
                        if tipo != "supabase_url":
                            print(f"      - {tipo.upper()}: {nome}")
                            print(f"        Download: {API_URL}/cardapio/download/{job_id}/{tipo}")
                    return True

                elif status["status"] == "failed":
                    print(f"\n❌ Processamento falhou!")
                    print(f"   Mensagem: {status['message']}")
                    return False

                elif status["status"] in ["pending", "processing"]:
                    print(f"   [{i+1}s] Status: {status['status']}...", end="\r")
                    time.sleep(1)

        except Exception as e:
            print(f"\n❌ Erro ao verificar status: {e}")
            return False

    print(f"\n⚠️ Timeout: Processamento demorou mais de {max_tentativas} segundos")
    return False

def baixar_arquivos(job_id):
    """
    Baixa os arquivos gerados
    """
    print(f"\n📥 Baixando arquivos do job {job_id}...")

    tipos = ["cdr", "pdf", "json", "csv"]

    for tipo in tipos:
        try:
            response = requests.get(f"{API_URL}/cardapio/download/{job_id}/{tipo}")

            if response.status_code == 200:
                filename = f"cardapio_{job_id}.{tipo}"
                with open(filename, "wb") as f:
                    f.write(response.content)
                print(f"   ✅ {filename} baixado")
            else:
                print(f"   ⚠️ {tipo.upper()} não disponível")

        except Exception as e:
            print(f"   ❌ Erro ao baixar {tipo}: {e}")

if __name__ == "__main__":
    sucesso = formatar_cardapio()

    if sucesso:
        print("\n" + "=" * 60)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 60)

        # Perguntar se quer baixar os arquivos
        resposta = input("\n💾 Deseja baixar os arquivos? (s/n): ")
        if resposta.lower() == "s":
            baixar_arquivos("lula-bar-001")
    else:
        print("\n" + "=" * 60)
        print("❌ TESTE FALHOU")
        print("=" * 60)
