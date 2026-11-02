"""Readable PDF companion to the exact bank used by production (optional ReportLab)."""
import sys
from pathlib import Path
from xml.sax.saxutils import escape
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'daily'))
import catalog
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/catalogo-acertijos-v1.pdf'
FONT=ROOT/'assets/fonts/Barlow-Bold.ttf'
pdfmetrics.registerFont(TTFont('Barlow',str(FONT)))
W,H=420,595
BLUE=HexColor('#0b2545');YELLOW=HexColor('#d59400')

def paragraph(c,text,x,y,width,size=12,color=BLUE):
    style=ParagraphStyle('body',fontName='Barlow',fontSize=size,leading=size*1.32,textColor=color)
    p=Paragraph(escape(text),style);_,h=p.wrap(width,H)
    p.drawOn(c,x,y-h)
    return y-h

def footer(c,page):
    c.setFillColor(BLUE);c.setFont('Barlow',9)
    c.drawString(26,20,'RETO VISUAL 70 | Catálogo original v1 | 02/11/2026')
    c.drawRightString(W-26,20,str(page))

def main():
    bank=catalog.load();OUT.parent.mkdir(exist_ok=True)
    c=canvas.Canvas(str(OUT),pagesize=(W,H))
    c.setTitle('Reto Visual 70 - Catálogo de 90 ejercicios con soluciones')
    c.setAuthor('Reto Visual 70')
    y=paragraph(c,'RETO VISUAL 70',26,554,W-52,28)
    y=paragraph(c,'90 ejercicios. 30 selecciones. Tres niveles.',26,y-22,W-52,22)
    for text in [
        'Cada selección contiene un nivel básico, uno intermedio y uno avanzado, con opciones y solución. La dificultad es relativa dentro de su tema: combina bases de secundaria y preparatoria.',
        'Diez temas: álgebra, porcentajes, sucesiones, geometría, sistemas, potencias, funciones, probabilidad, combinatoria y promedios.',
        'Los textos, datos y soluciones son originales del proyecto. El libro de Dudeney se usó como referencia temática; este documento no reproduce sus textos ni ilustraciones.',
        'El historial reserva también los ejercicios rechazados. Un cambio de opciones, fecha o posición no vuelve nuevo un ejercicio. Si se agota el catálogo, la producción se bloquea y pide ampliarlo.',
        'Las respuestas incluidas son para revisión. En el video aparecen al final de cada nivel. Cada video requiere tu aprobación exacta antes de programarse.'
    ]: y=paragraph(c,text,26,y-17,W-52,12)
    footer(c,1);c.showPage()
    for page,pack in enumerate(bank['packs'],2):
        c.setFillColor(BLUE);c.rect(0,H-75,W,75,fill=1,stroke=0)
        paragraph(c,pack['title'],26,H-20,W-52,20,HexColor('#ffffff'))
        paragraph(c,f"Selección {page-1:02d} / 30 | {pack['pack_id']}",26,H-51,W-52,10,HexColor('#ffdd77'))
        y=H-94
        for r in pack['rounds']:
            paragraph(c,f"NIVEL {r['level']} - {r['difficulty']}",26,y,W-52,13,YELLOW)
            y=paragraph(c,r['question'],26,y-23,W-52,14)
            y=paragraph(c,' | '.join(f'{"ABC"[i]}) {v}' for i,v in enumerate(r['choices'])),26,y-9,W-52,13)
            y=paragraph(c,f"Respuesta { 'ABC'[r['correct']] }: {r['next']}. {r['explanation']}",26,y-9,W-52,11)
            paragraph(c,'ID: '+r['catalog_id'],26,y-7,W-52,8)
            y-=39
            assert y>35, (pack['pack_id'],r['level'],y)
        footer(c,page);c.showPage()
    c.save()
    print(OUT)

if __name__=='__main__':main()
