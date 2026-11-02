"""Author original math exercises, never copy text/diagrams from a book."""
import sys,json,textwrap
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'daily'))
import catalog

def wrap(s,width): return textwrap.wrap(s,width=width,break_long_words=False,break_on_hyphens=False)

def make(topic,title,variant,level,kind,params,question,explanation,spoken):
    result=catalog.solve(kind,params); answer=catalog.value(result)
    # Numeric distractors are unique and exact, including fractions.
    options=[answer,catalog.value(result+1),catalog.value(result-1)]
    if kind=='probability':
        total=params['red']+params['blue']
        options=[answer,catalog.value(catalog.Fraction(params['blue'],total)),catalog.value(catalog.Fraction(params['red'],total+1))] if params['draws']==1 else [answer,catalog.value(catalog.Fraction(params['red'],total)),catalog.value(1-result)]
    shift=(variant+level)%3; options=options[shift:]+options[:shift]
    r={'catalog_id':f'{topic}-{variant+1:02d}-L{level}','level':level,'difficulty':catalog.LEVELS[level-1],
       'kind':kind,'params':params,'question':question,'question_lines':wrap(question,32),
       'next':answer,'choices':options,'correct':options.index(answer),'explanation':explanation,
       'solution_lines':wrap(explanation,38),'spoken_answer':spoken.format(answer=answer)}
    catalog.validate_round(r)
    return r

def build():
    packs=[]
    for v in range(3):
        rows=[]
        def add(topic,title,level,kind,p,q,e,s='El resultado es {answer}.'):
            rows.append((topic,title,make(topic,title,v,level,kind,p,q,e,s)))
        # The tiers progress within each topic, relative to high-school content.
        for level,(a,x,c) in enumerate([(3+v,5+v,4),(4+v,6+v,-7),(7+v,9+v,-11)],1):
            b=a*x+c
            q=f'{a}x + {c} = {b}. ¿Cuánto vale x?' if c>=0 else f'{a}x - {-c} = {b}. ¿Cuánto vale x?'
            if level==2:
                q=f'{a}(x - 2) = {a*(x-2)}. Halla x.';c=-2*a;b=a*(x-2)
            if level==3:
                factor=5+v;constant=x*(x-factor)
                q=f'x² - {factor}x = {constant}. Halla x positivo.'
                add('algebra','Despeja la incógnita',level,'quadratic',dict(a=factor,constant=constant),q,f'(x - {x})(x + {x-factor}) = 0; x = {x}.','Equis vale {answer}.')
            else:add('algebra','Despeja la incógnita',level,'linear',dict(a=a,b=b,c=c),q,f'{a}x = {a*x}; x = {x}.','Equis vale {answer}.')
        base=200+100*v
        for l,f,s in [(1,-20,0),(2,20,-20),(3,25,-20)]:
            p=dict(base=base,first=f,second=s); ans=catalog.value(catalog.solve('percent',p))
            q=f'Precio: {base}. Descuento: 20%. ¿Precio final?' if l==1 else f'Precio: {base}. Sube {f}% y baja {-s}%. ¿Final?'
            add('porcentajes','Cambios porcentuales',l,'percent',p,q,f'{base} x {100+f}/100 x {100+s}/100 = {ans}.')
        for l,mode,start,step,n in [(1,'arithmetic',3+v,4,6),(2,'geometric',2+v,2,5),(3,'arithmetic',5+v,7,20)]:
            p=dict(mode=mode,start=start,step=step,n=n);ans=catalog.value(catalog.solve('sequence',p))
            rule=f'suma {step}' if mode=='arithmetic' else f'multiplica por {step}'
            add('sucesiones','Encuentra el término',l,'sequence',p,f'Empieza en {start}; {rule}. ¿Término {n}?',f'{start} + {n-1} x {step} = {ans}.' if mode=='arithmetic' else f'{start} x {step}^{n-1} = {ans}.')
        for l,p,q,e in [
            (1,dict(mode='area',a=6+v,b=4),f'Rectángulo de {6+v} por 4. ¿Área?',f'Área = base x altura = {(6+v)*4}.'),
            (2,dict(mode='hypotenuse',a=3*(v+1),b=4*(v+1)),f'Triángulo rectángulo: catetos {3*(v+1)} y {4*(v+1)}. ¿Hipotenusa?',f'Pitágoras: c² = {25*(v+1)**2}; c = {5*(v+1)}.'),
            (3,dict(mode='base',area=84+12*v,height=6),f'Un triángulo tiene área {42+6*v} y altura 6. ¿Base?',f'Base = 2 x área / 6 = {14+2*v}.')]:
            add('geometria','Medidas y figuras',l,'geometry',p,q,e)
        for l in [1,2,3]:
            x=8+v+l;y=3+v
            if l<3:
                p=dict(mode='sum',total=x+y,difference=x-y)
                q=f'x + y = {x+y}; x - y = {x-y}. Halla x.' if l==1 else f'Dos números suman {x+y}. Difieren en {x-y}. ¿El mayor?'
                e=f'Suma las ecuaciones: 2x = {2*x}; x = {x}.'
            else:
                p=dict(mode='tickets',count=10+v,cheap=20,expensive=35,cost=(10+v)*20+x*15)
                q=f'{10+v} boletos de 20 o 35 suman {p["cost"]}. ¿Cuántos de 35?'
                e=f'15x = {p["cost"]} - {(10+v)*20}; x = {x}.'
                # Count must include all expensive tickets.
                p['count']=15+v;p['cost']=p['count']*20+x*15
                q=f'{p["count"]} boletos de 20 o 35 suman {p["cost"]}. ¿Cuántos de 35?'
                e=f'15x = {p["cost"]} - {p["count"]*20}; x = {x}.'
            add('sistemas','Dos datos, una respuesta',l,'system',p,q,e,'La respuesta es {answer}.')
        base=2+v
        for l,a,b in [(1,2,1),(2,5,-3),(3,-2,3)]:
            p=dict(base=base,a=a,b=b);ans=catalog.value(catalog.solve('power',p))
            add('potencias','Leyes de exponentes',l,'power',p,f'{base}^{a} x {base}^{b}. ¿Resultado?',f'Suma exponentes: {base}^{a+b} = {ans}.')
        for l,a,b,c,x in [(1,0,2+v,3,4),(2,1,0,-(3+v),5),(3,1,-(3+v),2,-2)]:
            p=dict(a=a,b=b,c=c,x=x);ans=catalog.value(catalog.solve('function',p))
            expression=f'{b}x + {c}' if l==1 else (f'x² - {-c}' if l==2 else f'x² - {-b}x + {c}')
            add('funciones','Evalúa la función',l,'function',p,f'f(x) = {expression}. ¿f({x})?',f'Sustituye x por {x}: f({x}) = {ans}.')
        for l,red,blue,draws in [(1,3+v,2,1),(2,4+v,3,2),(3,5+v,3,3)]:
            p=dict(red=red,blue=blue,draws=draws);ans=catalog.value(catalog.solve('probability',p))
            q=f'{red} rojas y {blue} azules. Sacas {draws} sin devolver. ¿P(todas rojas)?'
            numerator=catalog.comb(red,draws);denominator=catalog.comb(red+blue,draws)
            add('probabilidad','Azar sin reemplazo',l,'probability',p,q,f'{numerator}/{denominator} = {ans}. Casos favorables / total.','La probabilidad es {answer}.')
        for l,mode,a,b in [(1,'product',3+v,4),(2,'choose',5+v,2),(3,'ordered',5+v,3)]:
            p=dict(mode=mode,a=a,b=b);ans=catalog.value(catalog.solve('counting',p))
            if l==1:q=f'{a} camisas y {b} pantalones. ¿Cuántos conjuntos?';e=f'{a} x {b} = {ans} conjuntos.'
            elif l==2:q=f'Elige {b} de {a} personas. No importa el orden. ¿Grupos?';e=f'C({a},{b}) = {ans}. Sin repetir personas.'
            else:q=f'De {a} personas, elige {b} cargos distintos. ¿Formas?';e=f'{a} x {a-1} x {a-2} = {ans}. Sí importa el orden.'
            add('combinatoria','Cuenta las posibilidades',l,'counting',p,q,e)
        for l,known,target,count in [(1,[6+v,8],8,3),(2,[7+v,8,9],9,4),(3,[6+v,7,8,9],9,5)]:
            p=dict(known=known,target=target,count=count);ans=catalog.value(catalog.solve('average',p))
            add('promedios','El dato que falta',l,'average',p,f'Datos: {", ".join(map(str,known))} y x. Promedio: {target}. ¿x?',f'Total = {target} x {count}; x = {ans}.','El dato faltante es {answer}.')
        for topic,title,_ in rows[::3]:
            packs.append({'pack_id':f'{topic}-{v+1:02d}','topic':topic,'title':title,'rounds':[r for t,_,r in rows if t==topic]})
    bank={'version':1,'language':'es-MX','rights':'original_project_text_and_parameters',
          'source_note':'Redacción, datos y soluciones originales del proyecto. Dudeney se consultó como referencia temática; no se copiaron textos, traducciones ni ilustraciones.',
          'reference_url':'https://www.gutenberg.org/ebooks/16713',
          'difficulty_note':'Tres niveles relativos dentro de cada tema; base de secundaria y preparatoria. No certifica un programa escolar.',
          'packs':packs}
    catalog.PATH.write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    catalog.load()
    print(f'{len(packs)} packs / {sum(len(p["rounds"]) for p in packs)} validated exercises')

if __name__=='__main__':build()
