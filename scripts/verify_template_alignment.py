"""Compare fixed page artwork and typography against the native Word PDF."""
from pathlib import Path
import json
import pymupdf as fitz
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
reference = fitz.open(ROOT / 'reference/2026/word-render.pdf')

def spans(page):
    return [s for b in page.get_text('dict')['blocks'] for l in b.get('lines', []) for s in l['spans'] if s['text'].strip()]

def ink(page, rect):
    p = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=fitz.Rect(rect), colorspace=fitz.csGRAY)
    return np.frombuffer(p.samples, dtype=np.uint8).reshape(p.height, p.width) < 220

def tolerant_overlap(a,b):
    # One rendered pixel permits antialiasing differences, not visible drift.
    da = np.array(Image.fromarray(a).filter(ImageFilter.MaxFilter(3)), dtype=bool)
    db = np.array(Image.fromarray(b).filter(ImageFilter.MaxFilter(3)), dtype=bool)
    return min(float((a & db).sum()/max(a.sum(),1)),float((b & da).sum()/max(b.sum(),1)))

results = {}
for name in ['example.pdf','example-color.pdf']:
    doc = fitz.open(ROOT/name)
    assert len(doc)>=3
    assert abs(doc[0].rect.width-reference[0].rect.width)<.1
    assert abs(doc[0].rect.height-reference[0].rect.height)<.1
    areas = {
        'cover_logos_and_heading': (0,(85,85,515,310)),
        'cover_labels_and_rules': (0,(85,370,210,562)),
        'abstract_heading': (1,(125,115,480,212)),
        'abstract_title_label': (1,(60,240,128,275)),
        'abstract_label': (1,(260,305,340,335)),
    }
    scores={}
    for label,(page,rect) in areas.items():
        score=tolerant_overlap(ink(reference[page],rect),ink(doc[page],rect))
        assert score>.995,(name,label,score)
        scores[label]=round(score,6)
    deltas=[]
    for i,needles in [(0,['中国研究生创新实践系列大赛','数学建模竞赛','参赛队号','队员姓名']),(1,['中国研究生创新实践系列大赛','数学建模竞赛','题 目：','摘 要：'])]:
        refsp=spans(reference[i]);outsp=spans(doc[i])
        for text in needles:
            a=next(s for s in refsp if s['text'].strip()==text)
            b=next(s for s in outsp if s['text'].strip()==text)
            delta=max(abs(a['origin'][j]-b['origin'][j]) for j in [0,1])
            assert delta<.05,(text,delta)
            assert abs(a['size']-b['size'])<.05
            deltas.append(delta)
    for i in range(1,len(doc)):
        footer=[s for s in spans(doc[i]) if s['text'].strip()==str(i) and s['origin'][1]>780]
        assert len(footer)==1,(name,i,'footer')
        assert abs(footer[0]['origin'][1]-790.32)<.1
        assert abs(footer[0]['size']-9.12)<.05
        assert len(doc[i].get_text().strip())>10
    body=[s for s in spans(doc[2]) if 'SimSun' in s['font'] and len(s['text'])>15]
    assert body and all(abs(s['size']-12)<.1 for s in body)
    title=[s for s in spans(doc[1]) if 'SimHei' in s['font']]
    assert title and any(abs(s['size']-16)<.1 for s in title)
    heads=[s for s in spans(doc[2]) if 'SimHei' in s['font']]
    assert heads and any(abs(s['size']-14)<.1 for s in heads)
    results[name]={'pages':len(doc),'static_ink_overlap_with_one_pixel_tolerance':scores,'max_sampled_position_error_bp':round(max(deltas),6),'footer_baseline_bp':790.32,'body_size_bp':round(body[0]['size'],3),'status':'PASS'}
output=ROOT/'reference/2026/alignment-verification.json'
output.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(output.read_text())
