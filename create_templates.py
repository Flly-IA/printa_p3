# create_templates.py
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

try:
    import win32com.client as win32
    from pywintypes import com_error
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

def create_template(corel, output_path, title_text="NOME DO RESTAURANTE"):
    """Cria um template com apenas o título no topo"""
    doc = corel.CreateDocument()
    page = doc.ActivePage
    layer = page.ActiveLayer
    
    # Criar texto do título
    pw = page.SizeWidth
    ph = page.SizeHeight
    title_x = pw / 2.0
    title_y = ph - 1.0
    
    title_shape = layer.CreateArtisticText(title_x, title_y, title_text)
    
    try:
        title_shape.Text.Story.Font = "Arial"
        title_shape.Text.Story.Size = 24
        title_shape.Text.Story.Bold = True
        title_shape.Text.Story.Alignment = 2
    except Exception as e:
        print(f"   Aviso: estilo: {e}")
    
    # Salvar - usar string pura
    output_str = str(output_path.absolute()).replace('/', '\\')
    
    try:
        doc.SaveAs(output_str)
        print(f" Criado: {output_path.name}")
        success = True
    except Exception as e:
        print(f" Erro ao salvar {output_path.name}: {e}")
        success = False
    
    try:
        doc.Close(False)
    except Exception:
        pass
    
    return success

def main():
    print("=== Criando Templates ===\n")
    base_dir = Path.cwd()
    tplA = base_dir / "tplA.cdr"
    tplB = base_dir / "tplB.cdr"
    
    print("Inicializando CorelDRAW...")
    try:
        corel = get_corel_app(visible=True)
    except Exception as e:
        print(f" Erro: {e}")
        return
    
    print(" CorelDRAW OK\n")
    
    print("Criando tplA.cdr...")
    success_a = create_template(corel, tplA, "NOME DO RESTAURANTE")
    
    print("\nCriando tplB.cdr...")
    success_b = create_template(corel, tplB, "NOME DO RESTAURANTE")
    
    print("\nFechando CorelDRAW...")
    try:
        corel.Quit()
    except Exception:
        pass
    
    print("\n=== RESULTADO ===")
    if success_a and success_b:
        print(" Templates criados!")
        print(f"   - {tplA}")
        print(f"   - {tplB}")
    else:
        print(" Erro ao criar templates")

if __name__ == "__main__":
    main()
