"""Three readable, exact worked steps after each future math answer."""
from fractions import Fraction
from math import comb, factorial
import textwrap
import catalog

TITLE='ESTE ES EL PROCEDIMIENTO'
STEP_SECONDS=4
SECONDS=3*STEP_SECONDS

def worked(r):
    p=r['params'];kind=r['kind'];answer=r['next'];steps=[]
    def add(text,calculation):
        lines=textwrap.wrap(text,32,break_long_words=False,break_on_hyphens=False)
        assert 1<=len(lines)<=3 and len(calculation)<=42
        steps.append({'instruction':text,'lines':lines,'calculation':calculation})
    if kind=='linear':
        total=p['b']-p['c'];sign='-' if p['c']>=0 else '+'
        add('Aísla el término que contiene x.',f"{p['a']}x = {p['b']} {sign} {abs(p['c'])} = {total}")
        add('Divide ambos lados entre el coeficiente.',f"x = {total} / {p['a']} = {answer}")
        add('Sustituye para comprobar la igualdad.',f"{p['a']} x {answer} {('+' if p['c']>=0 else '-')} {abs(p['c'])} = {p['b']}")
    elif kind=='quadratic':
        root=int(Fraction(answer));other=root-p['a']
        add('Pasa todo al lado izquierdo.',f"x² - {p['a']}x - {p['constant']} = 0")
        add('Factoriza el polinomio.',f'(x - {root})(x + {other}) = 0')
        add('Iguala cada factor a cero y elige x positivo.',f'x = {root} o x = {-other}; elige {root}')
    elif kind=='percent':
        first=Fraction(p['base']*(100+p['first']),100)
        add('Convierte el primer cambio en un factor.',f"1 + ({p['first']}/100) = {catalog.value(Fraction(100+p['first'],100))}")
        add('Aplica ese factor al precio inicial.',f"{p['base']} x {catalog.value(Fraction(100+p['first'],100))} = {catalog.value(first)}")
        add('Comprueba el precio final, sin otro cambio.' if p['second']==0 else 'Aplica el segundo cambio al nuevo precio.',f"{catalog.value(first)} x {catalog.value(Fraction(100+p['second'],100))} = {answer}")
    elif kind=='sequence':
        n=p['n']-1
        add('Cuenta los cambios desde el primer término.',f"{p['n']} - 1 = {n} cambios")
        if p['mode']=='arithmetic':
            add('Multiplica los cambios por la diferencia.',f"{n} x {p['step']} = {n*p['step']}")
            add('Suma ese avance al primer término.',f"{p['start']} + {n*p['step']} = {answer}")
        else:
            add('Eleva la razón al número de cambios.',f"{p['step']}^{n} = {p['step']**n}")
            add('Multiplica por el primer término.',f"{p['start']} x {p['step']**n} = {answer}")
    elif kind=='geometry':
        if p['mode']=='area':
            add('Usa la fórmula del área del rectángulo.','Área = base x altura')
            add('Sustituye las medidas dadas.',f"Área = {p['a']} x {p['b']}")
            add('Multiplica; expresa el área en unidades cuadradas.',f'Área = {answer} u²')
        elif p['mode']=='hypotenuse':
            square=p['a']**2+p['b']**2
            add('Aplica el teorema de Pitágoras.',f"c² = {p['a']}² + {p['b']}²")
            add('Calcula y suma ambos cuadrados.',f"c² = {p['a']**2} + {p['b']**2} = {square}")
            add('Toma la raíz positiva para una longitud.',f'raíz de {square} = {answer}')
        else:
            add('Usa el área del triángulo.','Área = base x altura / 2')
            add('Multiplica el área por dos.',f"2 x {catalog.value(Fraction(p['area'],2))} = {p['area']}")
            add('Divide entre la altura para hallar la base.',f"base = {p['area']} / {p['height']} = {answer}")
    elif kind=='system':
        if p['mode']=='sum':
            add('Suma las ecuaciones para eliminar y.',f"2x = {p['total']} + {p['difference']}")
            add('Divide la suma entre dos.',f"x = {p['total']+p['difference']} / 2 = {answer}")
            add('Resta x al total para comprobar ambos datos.',f"y = {p['total']} - {answer} = {catalog.value(p['total']-Fraction(answer))}")
        else:
            base=p['count']*p['cheap'];extra=p['cost']-base;diff=p['expensive']-p['cheap']
            add('Supón que todos los boletos son baratos.',f"{p['count']} x {p['cheap']} = {base}")
            add('Calcula cuánto se pagó por encima de esa base.',f"{p['cost']} - {base} = {extra}")
            add('Divide el extra entre la diferencia de precios.',f'{extra} / ({p["expensive"]} - {p["cheap"]}) = {answer}')
    elif kind=='power':
        exponent=p['a']+p['b']
        add('Al multiplicar la misma base, suma exponentes.',f"{p['a']} + ({p['b']}) = {exponent}")
        add('Conserva la base con el nuevo exponente.',f"{p['base']}^{exponent}")
        add('Calcula la potencia resultante.',f"{p['base']}^{exponent} = {answer}")
    elif kind=='function':
        x=p['x'];a=p['a']*x*x;b=p['b']*x
        add('Sustituye x en cada término de la función.',f"x = {x}; x² = {x*x}")
        add('Calcula los términos con sus signos.',f"{p['a']}x² = {a}; {p['b']}x = {b}")
        add('Suma todos los términos, incluida la constante.',f"{a} + ({b}) + ({p['c']}) = {answer}")
    elif kind=='probability':
        total=p['red']+p['blue'];n=p['draws'];good=comb(p['red'],n);all_cases=comb(total,n)
        def groups(count):
            product=' x '.join(str(count-j) for j in range(n))
            return (product if n==1 else f'({product}) / {factorial(n)}')+f' = {comb(count,n)}'
        add('Cuenta los grupos posibles, sin importar el orden.',groups(total))
        add('Cuenta los grupos con todas las bolas rojas.',groups(p['red']))
        add('Divide casos favorables entre casos posibles.',f'P = {good}/{all_cases} = {answer}')
    elif kind=='counting':
        a=p['a'];b=p['b']
        if p['mode']=='product':
            add('Elige una camisa entre las disponibles.',f'{a} opciones de camisa')
            add('Cada camisa se combina con cada pantalón.',f'{b} opciones por camisa')
            add('Multiplica las opciones independientes.',f'{a} x {b} = {answer}')
        elif p['mode']=='choose':
            add('El orden no importa: usa combinaciones.',f'C({a},{b}) = {a}! / ({b}! x {a-b}!)')
            add('Cuenta primero los pares ordenados.',f'{a} x {a-1} = {a*(a-1)}')
            add('Divide entre dos para no repetir cada pareja.',f'{a*(a-1)} / 2 = {answer}')
        else:
            add('Los cargos son distintos: el orden sí importa.',f'{a} opciones para el primer cargo')
            add('Cada persona elegida deja una opción menos.',f'{a-1} para el segundo; {a-2} para el tercero')
            add('Multiplica sin repetir personas.',f'{a} x {a-1} x {a-2} = {answer}')
    elif kind=='average':
        total=p['target']*p['count'];known=sum(p['known'])
        add('Multiplica el promedio por el número de datos.',f"Total = {p['target']} x {p['count']} = {total}")
        add('Suma los datos que ya conoces.',' + '.join(map(str,p['known']))+f' = {known}')
        add('Resta esa suma al total necesario.',f'x = {total} - {known} = {answer}')
    else:raise ValueError('No worked procedure for this math kind')
    assert len(steps)==3
    return steps

def apply(data):
    """Insert twelve seconds per level; approved historical plans stay untouched."""
    data.update(procedure_version=1,procedure_title=TITLE,duration_seconds=106)
    for i,r in enumerate(data['rounds']):
        offset=i*SECONDS
        r.update(start=r['start']+offset,answer=r['answer']+offset,
                 procedure_start=r['end']+offset,end=r['end']+offset+SECONDS,
                 procedure_steps=worked(r),procedure_seconds=SECONDS)

def samples(data):
    times=[2.]
    for r in data['rounds']:
        times += [float(r['start']+2),float(r['answer']+2)]
        if 'procedure_start' in r:times += [float(r['procedure_start']+STEP_SECONDS*j+2) for j in range(3)]
    return sorted(times+[float(data.get('duration_seconds',70)-2)])
