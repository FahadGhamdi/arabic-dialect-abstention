#!/usr/bin/env python3
"""Build the MDPI LaTeX version of the manuscript from paper/manuscript_v0.4.md.

- front matter (title, featured application, abstract, keywords) and back matter are read from the markdown;
- the body (sections 1–6) is converted by pandoc with natbib citations, then patched (\\cite, figure widths, tables);
- paper/latex/main.tex is written against the MDPI class (Definitions/mdpi.cls from the rticles distribution, Sept 2024);
- latexmk -pdf produces paper/latex/main.pdf.
Usage: python3 scripts/build_latex.py [--no-compile]
"""
import os, re, subprocess, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'paper', 'manuscript_v0.4.md')
TEX = os.path.join(ROOT, 'paper', 'latex')
os.makedirs(os.path.join(TEX, 'Definitions'), exist_ok=True)
os.makedirs(os.path.join(TEX, 'figures'), exist_ok=True)

md = open(SRC, encoding='utf-8').read()
title = re.search(r'^title:\s*"(.+?)"\s*$', md, re.M).group(1)
feat = re.search(r'\*\*Featured Application\.\*\*\s*(.+?)\n\n', md, re.S).group(1).strip()
abstract = re.search(r'\*\*Abstract\.\*\*\s*(.+?)\n\n', md, re.S).group(1).strip()
keywords = re.search(r'\*\*Keywords:\*\*\s*(.+?)\n', md).group(1).strip()
body = md.split('# 1. Introduction', 1)[1].split('# Back matter', 1)[0]
body = '# Introduction' + body
# strip the leading numbers from headings (the class numbers them)
body = re.sub(r'^(#+)\s*\d+(?:\.\d+)*\.\s+', r'\1 ', body, flags=re.M)
back = md.split('# Back matter', 1)[1].split('# Appendices', 1)[0]
appx = md.split('# Appendices', 1)[1].split('# References', 1)[0]
# each appendix becomes a \section (the class prints "Appendix A" etc. itself)
appx = re.sub(r'^## Appendix [A-F]\.\s+', '# ', appx, flags=re.M)
appx = re.sub(r'<!-- .*? -->\n?', '', appx)


def field(name):
    m = re.search(r'\*\*' + re.escape(name) + r'\.\*\*\s*(.+?)\n\n', back + '\n\n', re.S)
    return m.group(1).strip() if m else ''


def md2tex(s, standalone=False):
    p = subprocess.run(['pandoc', '-f', 'markdown', '-t', 'latex', '--natbib', '--wrap=none', '--top-level-division=section'],
                       input=s, capture_output=True, text=True, check=True)
    return p.stdout


def tex_inline(s):
    t = md2tex(s).strip()
    t = re.sub(r'\\citep\{([^}]*)\}', r'\\cite{\1}', t)
    t = re.sub(r'\\citet\{([^}]*)\}', r'\\cite{\1}', t)
    return t


def patch(tex):
    tex = re.sub(r'\\citep\{([^}]*)\}', r'\\cite{\1}', tex)
    tex = re.sub(r'\\citet\{([^}]*)\}', r'\\cite{\1}', tex)
    # figures: copy PDFs, set width, let them float (tbp) so that no page is left half empty
    for m in re.finditer(r'\\includegraphics\{\.\./figures/([^}]+)\}', tex):
        shutil.copy2(os.path.join(ROOT, 'figures', m.group(1)), os.path.join(TEX, 'figures', m.group(1)))
    tex = re.sub(r'\\includegraphics\{\.\./figures/([^}]+)\}', r'\\includegraphics[width=\\textwidth]{figures/\1}', tex)
    tex = tex.replace('\\begin{figure}\n', '\\begin{figure}[tbp]\n')
    # captions: drop the leading "Figure N." / "Figure A1." that pandoc keeps inside the caption text
    tex = re.sub(r'\\caption\{Figure [A-Z]?\d+\.\s*', r'\\caption{', tex)
    # tables: pandoc writes longtables; every table here fits on one page, so each becomes a floating table (no page
    # left half empty, no table split across pages) with the "Table N." paragraph that precedes it as its caption.
    def tab(m):
        num, cap, lt = m.group(1), m.group(2), m.group(3)
        spec = re.search(r'\\begin\{longtable\}\[\]\{(.*?)\}\n\\toprule', lt, re.S).group(1)
        head = re.search(r'\\toprule\\noalign\{\}\n(.*?)\\endhead\n', lt, re.S).group(1)
        body = lt.split('\\endlastfoot\n', 1)[1].rsplit('\\end{longtable}', 1)[0]
        return ('\\begin{table}[tbp]\\footnotesize\\setlength{\\tabcolsep}{4pt}\n\\caption{' + cap + '}\\label{tab:' + num + '}\n\\begin{tabular}{' + spec + '}\n\\toprule\\noalign{}\n' + head +
                body + '\\bottomrule\\noalign{}\n\\end{tabular}\n\\end{table}\n')
    tex = re.sub(r'(?m)^Table ([A-Z]?\d+)\.\s*([^\n]+?)\n\n(\\begin\{longtable\}.*?\\end\{longtable\})', tab, tex, flags=re.S)
    return tex


body_tex = patch(md2tex(body))
# unicode that mathpazo/pdftex may not have: keep text symbols via newunicodechar-free replacements
rep = {'τ': r'$\tau$', 'α': r'$\alpha$', 'Δ': r'$\Delta$', 'κ': r'$\kappa$', '≤': r'$\le$', '≥': r'$\ge$', '≈': r'$\approx$', '∈': r'$\in$',
       '⌈': r'$\lceil$', '⌉': r'$\rceil$', '×': r'$\times$', '→': r'$\rightarrow$', '−': '--', '±': r'$\pm$', 'q̂': r'$\hat{q}$', '′': r'$^{\prime}$',
       '⟶': r'$\rightarrow$'}
feat = tex_inline(feat); abstract = tex_inline(abstract); keywords = tex_inline(keywords); title = tex_inline(title)
for k, v in rep.items():
    body_tex = body_tex.replace(k, v)
    feat = feat.replace(k, v); abstract = abstract.replace(k, v); title = title.replace(k, v)
# "--" produced from the minus sign must not become an en dash inside numbers: use \mbox{-}? Use math minus instead
body_tex = re.sub(r'--(\d)', r'$-$\1', body_tex)
body_tex = re.sub(r'--(\.\d)', r'$-$\1', body_tex)

back_tex = {k: tex_inline(field(k)) for k in ['Supplementary Materials', 'Author Contributions', 'Funding', 'Institutional Review Board Statement',
                                                 'Informed Consent Statement', 'Data Availability Statement', 'Acknowledgments', 'Conflicts of Interest']}
appx_tex = patch(md2tex(appx))
for k, v in rep.items():
    appx_tex = appx_tex.replace(k, v)
appx_tex = re.sub(r'--(\d)', r'$-$\1', appx_tex)
appx_tex = re.sub(r'--(\.\d)', r'$-$\1', appx_tex)
# appendix: floats may sit where they are written, and none may drift past its appendix or into the references
appx_tex = appx_tex.replace('[tbp]', '[htbp]')
appx_tex += '\n\\FloatBarrier\n'   # one barrier before the references; within the appendices the floats flow
ai_tex = tex_inline(re.search(r'## 3\.7\. Use of generative AI tools\n\n(.+?)\n\n#', md, re.S).group(1))
for k, v in rep.items():
    ai_tex = ai_tex.replace(k, v)
    back_tex = {kk: vv.replace(k, v) for kk, vv in back_tex.items()}

main = r"""%% Built by scripts/build_latex.py from paper/manuscript_v0.4.md — do not edit by hand.
\documentclass[applsci,article,submit,pdftex,oneauthor]{Definitions/mdpi}
\usepackage{longtable,booktabs,array,calc,etoolbox,placeins}
\makeatletter
\patchcmd\longtable{\par}{\if@noskipsec\mbox{}\fi\par}{}{}
\makeatother
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
% let floats fill pages instead of leaving half-empty pages before a figure
\renewcommand{\topfraction}{0.95}\renewcommand{\bottomfraction}{0.6}\renewcommand{\textfraction}{0.05}\renewcommand{\floatpagefraction}{0.85}
\setcounter{topnumber}{3}\setcounter{bottomnumber}{2}\setcounter{totalnumber}{4}
\setlist[itemize]{leftmargin=*,labelsep=5.8mm}
\setlist[enumerate]{leftmargin=*,labelsep=4.9mm}
\firstpage{1}
\makeatletter\setcounter{page}{\@firstpage}\makeatother
\pubvolume{1}\issuenum{1}\articlenumber{0}\pubyear{2026}\copyrightyear{2026}
\datereceived{ }\daterevised{ }\dateaccepted{ }\datepublished{ }
\hreflink{https://doi.org/}

\Title{TITLE}
\TitleCitation{TITLE}
\Author{Fahad AlGhamdi $^{1,*}$}
\AuthorNames{Fahad AlGhamdi}
\AuthorCitation{AlGhamdi, F.}
\address{$^{1}$ \quad Al-Baha University, Al-Baha, Saudi Arabia; [e-mail to be added]}
\corres{Correspondence: [e-mail to be added]}

\featuredapplication{FEAT}
\abstract{ABSTRACT}
\keyword{KEYWORDS}

\begin{document}

BODY

\vspace{6pt}
\supplementary{SUPP}
\authorcontributions{AUTHC}
\funding{FUNDING}
\institutionalreview{IRB}
\informedconsent{CONSENT}
\dataavailability{DATA}
\useofartificialintelligence{AIUSE}
\acknowledgments{ACK}
\conflictsofinterest{COI}

\appendixtitles{yes}
\appendixstart
\appendix
APPX

\begin{adjustwidth}{-\extralength}{0cm}
\reftitle{References}
\bibliography{references}
\PublishersNote{}
\end{adjustwidth}
\end{document}
"""
main = main.replace('TITLE', title).replace('FEAT', feat).replace('ABSTRACT', abstract).replace('KEYWORDS', keywords).replace('BODY', body_tex)
main = main.replace('SUPP', back_tex['Supplementary Materials']).replace('AUTHC', back_tex['Author Contributions']).replace('FUNDING', back_tex['Funding'])
main = main.replace('IRB', back_tex['Institutional Review Board Statement']).replace('CONSENT', back_tex['Informed Consent Statement'])
main = main.replace('DATA', back_tex['Data Availability Statement']).replace('AIUSE', ai_tex).replace('ACK', back_tex['Acknowledgments']).replace('COI', back_tex['Conflicts of Interest'])
main = main.replace('APPX', appx_tex)
open(os.path.join(TEX, 'main.tex'), 'w', encoding='utf-8').write(main)
# mdpi.bst prefixes every booktitle with "In Proceedings of the ", so the copy used here drops that prefix from the booktitle
# field (the master paper/references.bib keeps the full booktitle for other styles).
bib = open(os.path.join(ROOT, 'paper', 'references.bib'), encoding='utf-8').read()
bib = re.sub(r'(booktitle\s*=\s*\{)Proceedings of the ', r'\1', bib)
open(os.path.join(TEX, 'references.bib'), 'w', encoding='utf-8').write(bib)
for f in ['mdpi.cls', 'mdpi.bst', 'chicago2.bst', 'logo-mdpi.eps', 'logo-orcid.pdf']:
    src = os.path.join('/tmp/claude-0/mdpi_tpl', f)
    dst = os.path.join(TEX, 'Definitions', f)
    if os.path.exists(src) and not os.path.exists(dst):
        shutil.copy2(src, dst)
print('wrote', os.path.join(TEX, 'main.tex'))
if '--no-compile' not in sys.argv:
    r = subprocess.run(['latexmk', '-pdf', '-interaction=nonstopmode', '-halt-on-error', 'main.tex'], cwd=TEX, capture_output=True, text=True, errors='replace')
    print('latexmk exit', r.returncode)
    if r.returncode != 0:
        print(r.stdout[-4000:]); print(r.stderr[-2000:])
