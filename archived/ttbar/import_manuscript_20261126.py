"""Import the supplied manuscript and prepare a marked Obsidian reading copy."""
from pathlib import Path
import hashlib
import html
import json
import re
import shutil

REPO = Path(__file__).resolve().parents[1]
SOURCE = Path(r'C:/Users/69472/Desktop/xenon_monojet_ttbar_markdown')
DEST = REPO / 'ttbar_paper_update_20261126'


def reading_format(text):
    def figure(match):
        block = match[0]
        image = re.search(r'<img\s+[^>]*src="([^"]+)"[^>]*>', block)[1]
        caption = re.search(r'<figcaption>(.*?)</figcaption>', block, re.S)
        anchor = re.search(r'id="([^"]+)"', block)
        cap = caption[1] if caption else ''
        return (f'<a id="{anchor[1]}"></a>\n\n' if anchor else '') + f'![]({image})\n\n{cap}'
    text = re.sub(r'<figure\b.*?</figure>', figure, text, flags=re.S)
    text = re.sub(r'<a\s+[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                  lambda m: '['+m[2]+']('+m[1]+')', text, flags=re.S)
    text = re.sub(r'\{(?:reference-type|reference)=[^}]*\}', '', text, flags=re.S)
    text = re.sub(r'\$\$\\begin\{equation\*?\}', '$$', text)
    text = re.sub(r'\\end\{equation\*?\}\$\$', '$$', text)
    text = re.sub(r'\\label\{[^}]*\}', '', text)

    def simple_table(match):
        lines = [s for s in match[0].splitlines() if not s.startswith(':::')]
        sep = next(i for i,s in enumerate(lines) if re.fullmatch(r'\s*-{3,}(?:\s+-{3,})+\s*',s))
        spans = [(m.start(),m.end()) for m in re.finditer(r'-{3,}', lines[sep])]
        def cells(s):
            result=[]
            for i,(start,end) in enumerate(spans):
                right=spans[i+1][0] if i+1<len(spans) else len(s)
                result.append(s[start:right].strip().replace('|',r'\|'))
            return '| '+' | '.join(result)+' |'
        rows=[cells(lines[sep-1]), '| '+' | '.join(['---']*len(spans))+' |']
        tail=[]
        for line in lines[sep+1:]:
            if not line.strip(): continue
            if line.lstrip().startswith(':') or tail:
                tail.append(line.strip().lstrip(':').strip())
            else: rows.append(cells(line))
        return '\n'.join(rows)+ ('\n\n'+' '.join(tail) if tail else '')
    text = re.sub(r':::: (?:table\*?|ruledtabular)\n.*?\n::::',simple_table,text,flags=re.S)

    text=re.sub(r'^(##) (.*)$',lambda m:m[0] if '{#' in m[2] or m[2]=='Abstract'
                else '#'+m[0],text,flags=re.M)

    def heading(m):
        hashes,title,anchor=m[1],m[2],m[3]
        return f'<a id="{anchor}"></a>\n\n{hashes}# {title}'
    text=re.sub(r'^(#+) (.*?) \{#([^ }]+)[^}]*\}$',heading,text,flags=re.M)
    return text


def main():
    DEST.mkdir(exist_ok=True)
    shutil.copytree(SOURCE,DEST,dirs_exist_ok=True)
    basis=DEST/'comparison_basis'
    basis.mkdir(exist_ok=True)
    for filename in ('main.tex','appendices.tex','references.bib'):
        shutil.copy2(REPO/'prd_overleaf'/filename,basis/filename)
    raw=(SOURCE/'xenon_monojet_ttbar.md').read_text(encoding='utf-8')
    front,body=raw.split('---',2)[1:]
    title=re.search(r'^title: "(.*)"',front,re.M)[1]
    abstract=re.search(r'abstract: \|\n(.*)',front,re.S)[1].strip()
    body=body.strip()
    blocks=re.split(r'\n\s*\n',body)
    result=[]; changes=[]; in_ttbar=False; ttbar_count=0
    for block in blocks:
        if block.startswith('# '):
            in_ttbar='{#sec:ttbar_recast}' in block
        kind=None; cid=None
        if in_ttbar:
            ttbar_count+=1;kind='新增';cid=f'A02.{ttbar_count:02}'
        elif block.startswith('We also estimate the expected sensitivity'):
            kind='新增';cid='A01'
        elif block.startswith('The all-hadronic top-pair recast provides'):
            kind='新增';cid='A03'
        elif block.startswith('The experimental inputs are available'):
            kind='改写';cid='C03'
        if kind:
            changes.append(dict(id=cid,kind=kind,source_excerpt=block[:200]))
            marker=f'> [!{"tip" if kind=="新增" else "info"}] {kind} {cid}\n> 相对本地 PRD 旧稿。'
            # Keep math, tables, headings and figures structurally intact.
            structural=block.startswith(('#','$$','|','<figure'))
            if not structural:
                block='=='+re.sub(r'\s*\n\s*',' ',block)+'=='
            result.append(marker+'\n\n'+block)
        else: result.append(block)
    preface=(f'# {title}\n\n'
        '> [!info] 改动标记说明\n'
        '> 黄色高亮及“新增／改写”旁注标出正文变化。新增的顶对正文整节标记；公式、表格和图片使用旁注。换行、交叉引用转换及章节顺延不计为科研新增。详见 [[变更说明_中文]]。\n\n'
        '> [!info] 改写 C01 标题\n> 标题新增 top-pair，将顶对通道纳入文章主题。\n\n'
        '## Abstract\n\n> [!info] 改写 C02 摘要\n> 增加 470 点中 381 点达到名义预期灵敏度，以及简化背景模型的适用范围；原摘要末尾关于三个单喷注代表点的稳健性句子在此处删去。\n\n'
        '=='+abstract+'==\n\n')
    marked=reading_format(preface+'\n\n'.join(result))
    bib=(SOURCE/'references.bib').read_text(encoding='utf-8')
    keys=re.findall(r'@\w+\{([^,]+),',bib)
    entries=re.split(r'(?=@\w+\{)',bib)
    references=[]
    for entry in entries:
        keymatch=re.match(r'@\w+\{([^,]+),',entry)
        if not keymatch: continue
        key=keymatch[1]
        def field(name):
            m=re.search(r'^\s*'+name+r'\s*=\s*\{(.*)\},?\s*$',entry,re.M)
            return m[1].strip('{}') if m else ''
        name=field('title'); doi=field('doi'); eprint=field('eprint');url=field('url')
        link='https://doi.org/'+doi if doi else 'https://arxiv.org/abs/'+eprint if eprint else url
        label=f'[{key}]'
        line=f'<a id="ref-{key}"></a>\n\n{label} '+(f'[{name}]({link})' if link else name)+'. '+field('year')+'.'
        if key=='engel1991': line='> [!tip] 新增 A04 参考文献\n> 新增 Engel 1991 核形状因子文献。\n\n'+line
        references.append(line)
    def cite(m):
        return ' · '.join(f'[{key}](#ref-{key})' for key in re.findall(r'@([\w:-]+)',m[0]))
    marked=re.sub(r'\[@[^]]+\]',cite,marked)
    marked+='\n\n## References\n\n'+'\n\n'.join(references)+'\n'
    marked_path=DEST/'xenon_monojet_ttbar_改动标记.md'
    marked_path.write_text(marked,encoding='utf-8')
    image_paths=re.findall(r'!\[[^]]*\]\(([^)]+)\)',marked)
    assert len(image_paths)==26,len(image_paths)
    assert all((DEST/path).is_file() for path in image_paths)
    assert raw==(DEST/'xenon_monojet_ttbar.md').read_text(encoding='utf-8')
    assert marked.count('$$')%2==0
    assert not re.search(r'\{reference-type=|<figure|::: ruledtabular',marked)
    assert len(references)==len(keys)
    image_comparison=[]
    for p in (SOURCE/'figures').iterdir():
        old=REPO/'prd_overleaf/figures'/p.name
        image_comparison.append(dict(file=p.name,status='new' if not old.exists() else
            'unchanged' if p.read_bytes()==old.read_bytes() else 'changed'))
    metadata=dict(source=str(SOURCE),baseline='Local prd_overleaf/main.tex + appendices.tex + references.bib, snapshotted in comparison_basis',
        source_sha256=hashlib.sha256((SOURCE/'xenon_monojet_ttbar.md').read_bytes()).hexdigest(),
        changes=changes,figures=image_comparison,readable_image_links_checked=len(image_paths),
        note='Scientific statements are imported as supplied; this is a document comparison, not a fresh numerical validation.')
    (DEST/'comparison_manifest.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'destination':str(DEST),'marked_blocks':len(changes),'ttbar_new_blocks':ttbar_count,
                      'image_statuses':image_comparison},ensure_ascii=False,indent=2))


if __name__=='__main__': main()
