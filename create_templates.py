# create_templates.py
# -*- coding: utf-8 -*-
# Cria templates minimalistas tplA.cdr e tplB.cdr

import sys
from pathlib import Path

try:
    import win32com.client as win32
except ImportError:
    print("pywin32 não encontrado. Instale com: pip install pywin32")
    sys.exit(1)

def get_corel_app(visible=True):
    """Inicializa CorelDRAW COM"""
    try:
        app = win32.GetActiveObject("CorelDRAW.Application")
        app.Visible = visible
        return app
    except Exception:
        pass
    for pid in [
        "CorelDRAW.Application.25",
        "CorelDRAW.Application",
        "CorelDRAW.Application.26",
        "CorelDRAW.Application.24",
    ]:
        try:
            app = win32.Dispatch(pid)
            app.Visible = visible
            return app
        except Exception:
            continue
    raise RuntimeError("CorelDRAW COM indisponível.")

def to_units(doc, mm):
    """Converte mm para unidades do documento"""
    cdrMillimeter = 7
    try:
        return doc.ToUnits(mm, cdrMillimeter)
    except Exception:
        return mm * 0.0393701  # mm -> inch

def create_template(corel, output_path, title_text="NOME DO RESTAURANTE"):
    """Cria um template com apenas o título no topo"""
    # Criar documento A4 Portrait
    doc = corel.CreateDocument()
    
    # Configurar página A4 (210x297mm)
    page = doc.ActivePage
    try:
        # Usar float() explicitamente para garantir tipo correto
        width = float(to_units(doc, 210))
        height = float(to_units(doc, 297))
        page.SetSize(width, height)
    except Exception as e:
        print(f"  ⚠ Aviso: não conseguiu definir tamanho A4: {e}")
    
    layer = page.ActiveLayer
    
    # Calcular posição do título (centralizado, topo da página)
    pw = float(page.SizeWidth)
    ph = float(page.SizeHeight)
    
    # Posição: 20mm do topo, centralizado
    title_y = float(ph - to_units(doc, 20))
    title_x = float(pw / 2)
    
    # Criar texto do título
    title_shape = layer.CreateArtisticText(title_x, title_y, str(title_text))
    
    # Estilizar título
    try:
        title_shape.Text.Story.Font = str("Arial")
        title_shape.Text.Story.Size = float(24)
        title_shape.Text.Story.Bold = True
        # Centralizar
        title_shape.Text.Story.Alignment = int(2)  # 2 = Center
    except Exception as e:
        print(f"  ⚠ Aviso: não conseguiu aplicar estilo ao título: {e}")
    
    # Salvar - usar string pura, não Path
    output_str = str(output_path.absolute()).replace('/', '\\')
    
    try:
        doc.SaveAs(output_str)
        print(f"✅ Criado: {output_path.name}")
    except Exception as e:
        print(f"❌ Erro ao salvar {output_path.name}: {e}")
        # Debug: mostrar o caminho sendo usado
        print(f"   Caminho tentado: {output_str}")
        return False
    
    # Fechar documento
    try:
        doc.Close(False)
    except Exception:
        pass
    
    return True

def main():
    print("=== Criando Templates Minimalistas ===\n")
    
    # Diretório atual
    base_dir = Path.cwd()
    tplA = base_dir / "tplA.cdr"
    tplB = base_dir / "tplB.cdr"
    
    # Verificar se já existem
    if tplA.exists():
        resp = input(f"⚠ {tplA.name} já existe. Sobrescrever? (s/N): ")
        if resp.lower() != 's':
            print("❌ Cancelado pelo usuário")
            return
    
    if tplB.exists():
        resp = input(f"⚠ {tplB.name} já existe. Sobrescrever? (s/N): ")
        if resp.lower() != 's':
            print("❌ Cancelado pelo usuário")
            return
    
    # Inicializar CorelDRAW
    print("Inicializando CorelDRAW...")
    try:
        corel = get_corel_app(visible=True)
    except Exception as e:
        print(f"❌ Erro ao inicializar CorelDRAW: {e}")
        return
    
    print("✅ CorelDRAW inicializado\n")
    
    # Criar templates
    print("Criando tplA.cdr (modelo 1 coluna)...")
    success_a = create_template(corel, tplA, "NOME DO RESTAURANTE")
    
    print("\nCriando tplB.cdr (modelo 2 colunas)...")
    success_b = create_template(corel, tplB, "NOME DO RESTAURANTE")
    
    # Fechar CorelDRAW
    print("\nFechando CorelDRAW...")
    try:
        corel.Quit()
    except Exception:
        pass
    
    # Resumo
    print("\n=== RESULTADO ===")
    if success_a and success_b:
        print("✅ Templates criados com sucesso!")
        print(f"   - {tplA}")
        print(f"   - {tplB}")
        print("\n➡ Agora você pode rodar o build_cardapio_dinamico.py")
    else:
        print("⚠ Alguns templates não foram criados corretamente")

if __name__ == "__main__":
    main()