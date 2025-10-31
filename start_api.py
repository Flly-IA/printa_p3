# start_api.py
# -*- coding: utf-8 -*-
"""
Script para inicializar a API de Cardápio Dinâmico
"""

import sys
from pathlib import Path

def check_requirements():
    """Verificar se todas as dependências estão instaladas"""
    missing = []
    
    try:
        import fastapi
    except ImportError:
        missing.append("fastapi")
    
    try:
        import uvicorn
    except ImportError:
        missing.append("uvicorn")
    
    if sys.platform == "win32":
        try:
            import win32com.client
        except ImportError:
            missing.append("pywin32")
    
    if missing:
        print("❌ Dependências faltando:")
        for dep in missing:
            print(f"   - {dep}")
        print("\n💡 Instale com: pip install -r requirements_api.txt")
        return False
    
    return True

def check_templates():
    """Verificar se templates existem"""
    templates_dir = Path(__file__).parent / "templates"
    tpl_a = templates_dir / "tplA.cdr"
    tpl_b = templates_dir / "tplB.cdr"
    
    if not templates_dir.exists():
        templates_dir.mkdir()
        print("⚠️  Pasta 'templates' criada")
    
    if not tpl_a.exists() or not tpl_b.exists():
        print("⚠️  Templates CDR não encontrados!")
        print("📝 Execute: python create_templates.py")
        print("   e copie os arquivos tplA.cdr e tplB.cdr para a pasta 'templates'")
        return False
    
    return True

def main():
    print("=" * 60)
    print("🚀 API CARDÁPIO DINÂMICO")
    print("=" * 60)
    print()
    
    # Verificações
    print("1️⃣ Verificando dependências...")
    if not check_requirements():
        sys.exit(1)
    print("   ✅ Todas as dependências instaladas")
    
    print("\n2️⃣ Verificando templates...")
    if not check_templates():
        sys.exit(1)
    print("   ✅ Templates encontrados")
    
    print("\n3️⃣ Iniciando servidor...")
    print("=" * 60)
    print()
    
    # Iniciar API
    import uvicorn
    uvicorn.run(
        "api_cardapio:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
