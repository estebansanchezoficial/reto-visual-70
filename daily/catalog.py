"""Finite, original Spanish math bank. An exhausted bank stops production."""
from pathlib import Path
from fractions import Fraction
from math import comb, factorial, isqrt
import hashlib, json

PATH = Path(__file__).with_name('puzzle-catalog.json')
LEVELS = ['BÁSICO', 'INTERMEDIO', 'AVANZADO']

def value(number):
    number = Fraction(number)
    return str(number.numerator) if number.denominator == 1 else f'{number.numerator}/{number.denominator}'

def solve(kind, p):
    """Exact arithmetic; no eval, remote model or floating point answer keys."""
    if kind == 'linear': return Fraction(p['b']-p['c'], p['a'])
    if kind == 'quadratic':
        discriminant=p['a']**2+4*p['constant']
        assert isqrt(discriminant)**2==discriminant and p['constant']>0
        return Fraction(p['a']+isqrt(discriminant),2)
    if kind == 'percent': return Fraction(p['base'] * (100+p['first']) * (100+p['second']), 10000)
    if kind == 'sequence': return p['start'] + p['step']*(p['n']-1) if p['mode']=='arithmetic' else p['start']*p['step']**(p['n']-1)
    if kind == 'geometry':
        if p['mode']=='area': return p['a']*p['b']
        if p['mode']=='hypotenuse':
            square=p['a']**2+p['b']**2
            assert isqrt(square)**2==square
            return isqrt(square)
        return Fraction(p['area'], p['height'])
    if kind == 'system': return Fraction(p['total']+p['difference'],2) if p['mode']=='sum' else Fraction(p['cost']-p['count']*p['cheap'],p['expensive']-p['cheap'])
    if kind == 'power': return Fraction(p['base'])**p['a'] * Fraction(p['base'])**p['b']
    if kind == 'function': return p['a']*p['x']**2+p['b']*p['x']+p['c']
    if kind == 'probability':
        if p['draws']==1: return Fraction(p['red'],p['red']+p['blue'])
        return Fraction(comb(p['red'],p['draws']),comb(p['red']+p['blue'],p['draws']))
    if kind == 'counting':
        if p['mode']=='product': return p['a']*p['b']
        if p['mode']=='choose': return comb(p['a'],p['b'])
        return factorial(p['a'])//factorial(p['a']-p['b'])
    if kind == 'average': return p['target']*p['count']-sum(p['known'])
    raise ValueError(f'Unknown catalog solver: {kind}')

def exercise_key(r):
    if r.get('catalog_id'):
        content=[r['kind'],r['params']]
    else:
        # Legacy rounds: ignore options, timing, narration and position.
        if 'word' in r: content=['word',r['word']]
        elif 'a' in r and 'op' in r: content=['operation',sorted([r['a'],r['b']]) if r['op']=='+' else [r['a'],r['b']],r['op']]
        elif 'sequence' in r: content=['sequence',r['sequence'],r['next']]
        else: content=['color',sorted(r['items']),r['target'],r['new']]
    return hashlib.sha256(json.dumps(content,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def validate_round(r):
    assert r['next']==value(solve(r['kind'],r['params'])), 'Incorrect catalog answer'
    assert r['level'] in [1,2,3] and r['difficulty']==LEVELS[r['level']-1]
    assert len(r['choices'])==3 and len(set(r['choices']))==3
    assert r['choices'][r['correct']]==r['next']
    assert 1<=len(r['question_lines'])<=4 and max(map(len,r['question_lines']))<=38
    assert 1<=len(r['solution_lines'])<=2 and max(map(len,r['solution_lines']))<=42
    assert r['explanation'] and r['spoken_answer']

def load():
    bank=json.loads(PATH.read_text(encoding='utf-8'))
    assert bank['rights']=='original_project_text_and_parameters'
    ids=set(); keys=set()
    for pack in bank['packs']:
        assert [r['level'] for r in pack['rounds']]==[1,2,3]
        for r in pack['rounds']:
            validate_round(r)
            assert r['catalog_id'] not in ids and exercise_key(r) not in keys
            ids.add(r['catalog_id']);keys.add(exercise_key(r))
    return bank

def select(history, rejected_family=None):
    used_ids={r.get('catalog_id') for h in history for r in h.get('rounds',[])}
    used_keys={exercise_key(r) for h in history for r in h.get('rounds',[])}
    # Every presented/rejected version counts. Avoid the most recent five topics.
    recent=[h.get('family') for h in sorted(history,key=lambda h:(h.get('episode',0),h.get('revision',1)))][-5:]
    for pack in load()['packs']:
        family='catalog_'+pack['topic']
        if family in recent or family==rejected_family: continue
        if any(r['catalog_id'] in used_ids or exercise_key(r) in used_keys for r in pack['rounds']): continue
        return json.loads(json.dumps(pack))
    raise ValueError('Catálogo agotado o sin tema suficientemente distinto: añadir ejercicios revisados; no reciclar.')
