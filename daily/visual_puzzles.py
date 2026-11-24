"""Original finite visual-math bank, activated for 24 November 2026 onwards."""
import itertools
import math

START_DATE = '2026-11-24'
TOPICS = ('balanzas', 'digitos', 'cuadrados', 'residuos')
LINES = ((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))

def candidates(kind, p):
    if kind == 'missing_digit':
        def valid(d):
            a=int(p['pattern'].replace('?',str(d)))
            if p['pattern'][0]=='?' and d==0:return False
            if p['mode']=='add':return a+p['operand']==p['result']
            if p['mode']=='multiply':return a*p['operand']==p['result']
            return a%p['divisor']==0
        return [d for d in range(10) if valid(d)]
    if kind == 'remainder':
        return [n for n in range(p['low'],p['high']+1) if all(n%d==r for d,r in p['clues'])]
    if kind == 'magic':
        grid=p['grid'];missing=[i for i,v in enumerate(grid) if v is None]
        unused=set(p['values'])-set(v for v in grid if v is not None)
        answers=[]
        for values in itertools.permutations(sorted(unused)):
            result=grid.copy()
            for i,v in zip(missing,values):result[i]=v
            if all(sum(result[i] for i in line)==p['total'] for line in LINES):answers.append(result)
        return answers
    raise ValueError(kind)

def solve(kind,p):
    if kind=='balance':
        c=p['circle_total']//p['circle_count'];t=p['pair_total']-p['circle_multiplier']*c
        q=p.get('square_total',0)-t
        return (t if p['mode']=='triangle' else c+t if p['mode']=='sum' else q*t+c)
    answers=candidates(kind,p)
    assert len(answers)==1,'Visual puzzle must have exactly one solution'
    return answers[0][p['target']] if kind=='magic' else answers[0]

def worked(kind,p,answer):
    if kind=='balance':
        c=p['circle_total']//p['circle_count'];t=p['pair_total']-p['circle_multiplier']*c
        last=f'T = {answer}' if p['mode']=='triangle' else f'C + T = {c} + {t} = {answer}'
        if p['mode']=='expression':last=f'{p["square_total"]-t} x {t} + {c} = {answer}'
        return [('C es círculo: divide su peso total.',f'C = {p["circle_total"]} / {p["circle_count"]} = {c}'),
                ('T es triángulo: resta el peso de C.',f'T = {p["pair_total"]} - {p["circle_multiplier"]*c} = {t}'),
                (f'Cuadrado: {p["square_total"]} - {t} = {p["square_total"]-t}. Multiplica y suma.' if p['mode']=='expression' else 'Sustituye los valores en la pregunta.',last)]
    if kind=='missing_digit':
        a=int(p['pattern'].replace('?',str(answer)))
        if p['mode']=='add':rows=[('Despeja el sumando incompleto.',f'{p["result"]} - {p["operand"]} = {a}'),('Compara las cifras con el enunciado.',f'{p["pattern"]} pasa a ser {a}'),('Comprueba la suma con el dígito hallado.',f'{a} + {p["operand"]} = {p["result"]}; ? = {answer}')]
        elif p['mode']=='multiply':rows=[('Divide el producto entre el factor.',f'{p["result"]} / {p["operand"]} = {a}'),('Compara las cifras del número obtenido.',f'{p["pattern"]} pasa a ser {a}'),('Comprueba la multiplicación.',f'{a} x {p["operand"]} = {p["result"]}; ? = {answer}')]
        else:
            digits=list(map(int,p['pattern'].replace('?','0')))
            alt=sum(digits[::2])-sum(digits[1::2]);sign=1 if p['pattern'].index('?')%2==0 else -1
            rows=[('Para dividir entre once, alterna sumas y restas.', 'La diferencia debe ser múltiplo de 11'),('Incluye el dígito oculto en esa diferencia.',f'{alt} {"+" if sign==1 else "-"} ? = {alt+sign*int(answer)}'),('Comprueba con una división exacta.',f'{a} / 11 = {a//11}; ? = {answer}')]
        return rows
    if kind=='magic':
        grid=p['grid'].copy();rows=[]
        while grid[p['target']] is None:
            line=next(line for line in LINES if sum(grid[i] is None for i in line)==1)
            i=next(i for i in line if grid[i] is None);known=[grid[j] for j in line if j!=i]
            grid[i]=p['total']-sum(known)
            rows.append(('Completa una línea con una sola casilla vacía.',f'{p["total"]} - {known[0]} - {known[1]} = {grid[i]}'))
        while len(rows)<3:rows.insert(0,('Cada fila, columna y diagonal tiene el mismo total.',f'Total por línea = {p["total"]}'))
        rows=rows[-3:];rows[-1]=('Así se obtiene la casilla marcada con X.',rows[-1][1]+f'; X = {answer}')
        return rows
    clues=p['clues']
    return [('Parte del intervalo y del primer residuo.',f'n = {clues[0][0]}k + {clues[0][1]}'),
            ('Filtra también con las otras pistas.' if len(clues)>1 else 'Busca ese residuo dentro del intervalo.',f'Único candidato: {answer}'),
            ('Comprueba, en orden, las divisiones dadas.', f'{answer}: sobran ' + ', '.join(str(r) for d,r in clues))]

def build_packs():
    import catalog
    packs=[]
    titles=['Equilibra las figuras','Encuentra el dígito','Completa el cuadrado','Descubre el número secreto']
    for v in range(10):
        for topic,title in zip(TOPICS,titles):
            rounds=[]
            for level in (1,2,3):
                if topic=='balanzas':
                    c=3+v+level;t=7+2*v+level;count=level+1;mult=1 if level==1 else 2
                    p=dict(circle_count=count,circle_total=count*c,circle_multiplier=mult,pair_total=mult*c+t,mode=['triangle','sum','expression'][level-1])
                    question=[f'{count} C = {count*c}',f'{mult} C + T = {mult*c+t}']
                    if level==3:p['square_total']=t+4+v;question += [f'Q + T = {p["square_total"]}']
                    question += [['¿T = ?','¿C + T = ?','¿Q x T + C = ?'][level-1]];kind='balance'
                elif topic=='digitos':
                    if level<3:
                        a=21+3*v+level;idx=1 if level==1 else 0;pattern=str(a)[:idx]+'?'+str(a)[idx+1:];operand=7+v if level==1 else 3+v%4
                        p=dict(mode='add' if level==1 else 'multiply',pattern=pattern,operand=operand,result=a+operand if level==1 else a*operand)
                        question=['Sustituye ? por un dígito.',f'{pattern} {"+" if level==1 else "x"} {operand} = {p["result"]}']
                    else:
                        a=11*(103+v*7);pattern=str(a)[:2]+'?'+str(a)[3:];p=dict(mode='divisible',pattern=pattern,divisor=11)
                        question=[f'{pattern} es divisible entre 11.','¿Qué dígito sustituye a ?']
                    kind='missing_digit'
                elif topic=='cuadrados':
                    shift=10*v+level;step=level;values=[shift+step*n for n in range(1,10)];grid=[shift+step*n for n in (8,1,6,3,5,7,4,9,2)]
                    missing=[[0],[0,1,4],[0,1,3,4]][level-1];target=1 if level==2 else 0
                    for i in missing:grid[i]=None
                    p=dict(grid=grid,values=values,total=3*shift+15*step,target=target);question=[f'Filas, columnas y diagonales: {p["total"]}.']
                    question += ['   '.join('X' if i==target else '?' if grid[i] is None else str(grid[i]) for i in range(j,j+3)) for j in (0,3,6)];kind='magic'
                else:
                    divisors=[[5+v%3],[3,5],[3,4,5]][level-1];period=math.prod(divisors);low=10+v*period;number=low+2+v%(period-2)
                    p=dict(low=low,high=low+period-1,clues=[[d,number%d] for d in divisors]);kind='remainder'
                    question=[f'Entero entre {low} y {p["high"]}, inclusive.']+[f'Al dividir entre {d}, sobra {r}.' for d,r in p['clues']]
                answer=str(solve(kind,p));options=[answer,str(int(answer)+1),str(int(answer)-1)];offset=(v+level)%3;options=options[offset:]+options[:offset]
                explanation=f'La respuesta es {answer}. Comprueba los pasos.'
                r=dict(catalog_id=f'visual-{topic}-{v+1:02d}-L{level}',level=level,difficulty=catalog.LEVELS[level-1],kind=kind,params=p,question=' '.join(question),question_lines=question,next=answer,choices=options,correct=options.index(answer),explanation=explanation,solution_lines=[f'Resultado: {answer}.'],spoken_answer=f'El resultado es {answer}.')
                catalog.validate_round(r);rounds.append(r)
            packs.append(dict(pack_id=f'visual-{topic}-{v+1:02d}',topic=topic,title=title,rounds=rounds))
    return packs
