# test_api_client.py
# -*- coding: utf-8 -*-
"""
Cliente de exemplo para testar a API de Cardápio Dinâmico
"""

import requests
import time
from pathlib import Path

# Configuração
API_URL = "http://localhost:8000"
INPUT_FILE = "teste_input.txt"

def test_health():
    """Testar health check"""
    print("🔍 Testando health check...")
    response = requests.get(f"{API_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Resposta: {response.json()}")
    return response.status_code == 200

def upload_and_generate(file_path: str):
    """Upload e geração do cardápio"""
    print("\n📤 Enviando arquivo para processamento...")
    
    with open(file_path, 'rb') as f:
        files = {'file': (Path(file_path).name, f, 'text/plain')}
        data = {
            'font': 'Arial',
            'font_size': 10.0
        }
        
        response = requests.post(
            f"{API_URL}/cardapio/gerar",
            files=files,
            data=data
        )
    
    if response.status_code != 200:
        print(f"   ❌ Erro: {response.status_code}")
        print(f"   {response.json()}")
        return None
    
    result = response.json()
    job_id = result['job_id']
    print(f"   ✅ Job criado: {job_id}")
    print(f"   📊 Status URL: {API_URL}{result['status_url']}")
    
    return job_id

def check_status(job_id: str):
    """Verificar status do job"""
    response = requests.get(f"{API_URL}/cardapio/status/{job_id}")
    
    if response.status_code != 200:
        return None
    
    return response.json()

def wait_for_completion(job_id: str, timeout: int = 300):
    """Aguardar conclusão do processamento"""
    print("\n⏳ Aguardando processamento...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        status = check_status(job_id)
        
        if not status:
            print("   ❌ Erro ao verificar status")
            return False
        
        print(f"   📊 Status: {status['status']} - {status['message']}")
        
        if status['status'] == 'completed':
            print("\n✅ Processamento concluído!")
            print(f"   📁 Arquivos disponíveis:")
            for file_type, filename in status['files'].items():
                print(f"      - {file_type}: {filename}")
            return True
        
        elif status['status'] == 'failed':
            print(f"\n❌ Processamento falhou: {status['message']}")
            return False
        
        time.sleep(2)
    
    print("\n⏰ Timeout excedido")
    return False

def download_files(job_id: str, output_dir: str = "downloads"):
    """Baixar arquivos gerados"""
    print(f"\n📥 Baixando arquivos para '{output_dir}'...")
    
    Path(output_dir).mkdir(exist_ok=True)
    
    file_types = ['pdf', 'png', 'cdr', 'json', 'csv']
    
    for file_type in file_types:
        try:
            response = requests.get(
                f"{API_URL}/cardapio/download/{job_id}/{file_type}",
                stream=True
            )
            
            if response.status_code == 200:
                # Extrair nome do arquivo do header Content-Disposition
                filename = f"cardapio_output.{file_type}"
                if file_type == 'json':
                    filename = 'parsed.json'
                elif file_type == 'csv':
                    filename = 'auditoria.csv'
                
                output_path = Path(output_dir) / filename
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"   ✅ {filename}")
            else:
                print(f"   ⚠️  {file_type}: não disponível")
        
        except Exception as e:
            print(f"   ❌ {file_type}: erro - {str(e)}")

def list_jobs():
    """Listar todos os jobs"""
    print("\n📋 Listando jobs...")
    response = requests.get(f"{API_URL}/cardapio/listar")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Total de jobs: {data['total']}")
        
        if data['jobs']:
            print("\n   Jobs:")
            for job in data['jobs']:
                print(f"      • {job['job_id'][:8]}... - {job['status']} - {job['created_at']}")
    else:
        print(f"   ❌ Erro: {response.status_code}")

def main():
    print("=" * 60)
    print("🧪 TESTE DA API - CARDÁPIO DINÂMICO")
    print("=" * 60)
    
    # 1. Health check
    if not test_health():
        print("\n❌ API não está respondendo. Certifique-se de que está rodando.")
        return
    
    # 2. Verificar arquivo de entrada
    if not Path(INPUT_FILE).exists():
        print(f"\n❌ Arquivo '{INPUT_FILE}' não encontrado")
        return
    
    # 3. Upload e geração
    job_id = upload_and_generate(INPUT_FILE)
    if not job_id:
        return
    
    # 4. Aguardar conclusão
    if not wait_for_completion(job_id):
        return
    
    # 5. Download dos arquivos
    download_files(job_id)
    
    # 6. Listar jobs
    list_jobs()
    
    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO!")
    print("=" * 60)

if __name__ == "__main__":
    main()
