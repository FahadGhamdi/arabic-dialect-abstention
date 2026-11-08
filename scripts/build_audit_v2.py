#!/usr/bin/env python3
"""Build the human translation-audit package v2 (after external review #5).
Files (audit/):
  rater1_DAMM_audit.xlsx      — instructions + 400 pairs (50 pilot keys + 30 confirmatory-test keys, x5 dialects) + live summary
  rater2_DAMM_audit.xlsx      — instructions + the 150 double-rated pairs (20 pilot + 10 test keys); contains NO rater-1 data
  adjudication_DAMM_audit.xlsx— paste both raters' sheets; matches by pair_id (INDEX/MATCH), agreement + Cohen's kappa per check,
                                 list of disagreements for the third rater
Summary formulas use ONLY rated rows as denominators; 'unsure' counted once per pair over all four checks.
No model output of any kind is included."""
import json, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter as L

df=pd.read_csv('data/damm.csv'); ak=json.load(open('audit/audit_keys.json'))
DIAL=['EGY','SYR','KSA','UAE','MAG']; DN={'EGY':'المصرية','SYR':'السورية','KSA':'السعودية','UAE':'الإماراتية','MAG':'المغربية'}; LET=['A','B','C','D']
pilot=ak['pilot_sample']['keys']; test=ak['confirmatory_test_sample']['keys']
dbl=set(ak['pilot_sample']['double_rated_keys'])|set(ak['confirmatory_test_sample']['double_rated_keys'])
keys=[(k,'pilot') for k in pilot]+[(k,'confirm') for k in test]
rows={(r.key,r.dialect):r for r in df[df.key.isin([k for k,_ in keys])].itertuples()}
def ch(r): return "\n".join(f"{LET[i]}. {c}" for i,c in enumerate(str(r.choices).split('|||')))
def gold(r): return f"{LET[int(r.answer)]}. {str(r.choices).split('|||')[int(r.answer)]}"
# pair list with stable ids
pairs=[]; pid=1
for k,src in keys:
    for d in DIAL:
        pairs.append(dict(pid=f"P{pid:03d}",key=k,src=src,d=d)); pid+=1
thin=Side(style='thin',color='BBBBBB'); BRD=Border(left=thin,right=thin,top=thin,bottom=thin)
HF=PatternFill('solid',fgColor='1F3864'); HFont=Font(name='Arial',bold=True,color='FFFFFF',size=10)
INF=PatternFill('solid',fgColor='FFF2CC'); F=Font(name='Arial',size=10); FB=Font(name='Arial',size=10,bold=True)
WR=Alignment(wrap_text=True,vertical='top',horizontal='right',readingOrder=2); WL=Alignment(wrap_text=True,vertical='top',horizontal='left')
HEAD=['معرّف الزوج','المصدر','معرّف السؤال','المجال','الأصل الإنجليزي (مرجع)','السؤال بالفصحى','خيارات الفصحى','الإجابة الصحيحة (فصحى)','اللهجة','السؤال باللهجة','خيارات اللهجة',
      'س1: حُفظ المعنى (الشروط/النفي/الكميات)؟','س2: الإجابة الصحيحة ما زالت صحيحة والخيارات صالحة؟','س3: لا تلميح مضاف ولا غموض جديد؟','س4: ينتمي النص إلى اللهجة المقصودة؟','ملاحظات (اذكر الكلمة/العبارة المشكِلة)']
WID=[10,9,16,16,45,45,40,28,10,45,40,16,16,16,16,30]
QCOLS=['L','M','N','O']  # Q1..Q4 columns in the audit sheets
def audit_sheet(ws, plist):
    ws.sheet_view.rightToLeft=True; ws.freeze_panes='J2'
    for j,h in enumerate(HEAD,1):
        c=ws.cell(row=1,column=j,value=h); c.font=HFont; c.fill=HF; c.alignment=Alignment(wrap_text=True,vertical='center',horizontal='center'); c.border=BRD; ws.column_dimensions[L(j)].width=WID[j-1]
    ws.row_dimensions[1].height=48; r=2
    for p in plist:
        m=rows[(p['key'],'MSA')]; e=rows[(p['key'],'ENG')]; x=rows[(p['key'],p['d'])]
        vals=[p['pid'],('تجريبي' if p['src']=='pilot' else 'تأكيدي'),p['key'],p['key'].split('|')[0],f"{e.question}\n{ch(e)}",m.question,ch(m),gold(m),DN[p['d']],x.question,ch(x),'','','','','']
        for j,v in enumerate(vals,1):
            c=ws.cell(row=r,column=j,value=v); c.font=F; c.border=BRD; c.alignment=WL if j==5 else WR
            if j>=12: c.fill=INF
        ws.row_dimensions[r].height=150; r+=1
    dv=DataValidation(type='list',formula1='"نعم,لا,غير متأكد"',allow_blank=True); dv.error='اختر: نعم / لا / غير متأكد'; ws.add_data_validation(dv)
    for col in QCOLS: dv.add(f'{col}2:{col}{r-1}')
    return r-1
INSTR=[('تدقيق تكافؤ الترجمة اللهجية — DialectalArabicMMLU (الإصدار 2)',True),
 ('الغرض: التحقق من أن النسخة اللهجية تغيّر «الغلاف اللغوي» فقط مع بقاء المعنى والإجابة الصحيحة وصلاحية الخيارات. أنت لا تقيّم أي نموذج لغوي؛ هذا الملف لا يحوي أي نتائج نماذج، والعينة اختيرت عشوائيًا ببذور مثبتة قبل الاطلاع على أي نتيجة.',False),
 ('العينة: 50 سؤالًا من العينة التجريبية + 30 سؤالًا من مجموعة الاختبار التأكيدي، × 5 لهجات = 400 زوج (الفصحى ← لهجة). عمود «المصدر» للتوثيق فقط ولا يغيّر طريقة التقييم.',False),
 ('كيفية التعبئة: املأ الأعمدة المظللة بالأصفر فقط (س1–س4 + الملاحظات) لكل صف. قارن عمودَي «السؤال باللهجة/خيارات اللهجة» بعمودَي الفصحى؛ الأصل الإنجليزي مرجع إضافي للمعنى والإجابة. لا تفرز الصفوف ولا تحذف أعمدة؛ معرّف الزوج (العمود الأول) هو مفتاح المطابقة.',False),
 ('س1 حُفظ المعنى: هل السؤال اللهجي يسأل الشيء نفسه؟ انتبه إلى النفي (لا/ليس/ما)، الشروط (إذا/إلا/فقط)، الكميات والأرقام والوحدات، والمصطلحات التخصصية. أي تغيير في هذه = «لا».',False),
 ('س2 الإجابة والخيارات: هل الخيار المحدد كإجابة صحيحة ما زال صحيحًا في النسخة اللهجية؟ وهل الخيارات الأربعة سليمة (لم يُحذف/يُكرر/يُشوَّه خيار، ولم يصبح خياران متكافئين)؟',False),
 ('س3 الوضوح: هل أُضيف تلميح يسهّل الإجابة أو غموض جديد يصعّبها؟ إن كان النص سليمًا = «نعم». (يُحلَّل منفصلًا عن س1/س2 لأنه قد يغيّر الصعوبة دون تغيير الإجابة.)',False),
 ('س4 الانتماء للهجة: هل يقرأ النص كنص مكتوب بتلك اللهجة فعلًا؟ قيّم هذا للهجاتك التي تتقنها فقط؛ وإلا اكتب «غير متأكد».',False),
 ('القيم: نعم / لا / غير متأكد (قائمة منسدلة). عند «لا» أو «غير متأكد» اكتب في الملاحظات الكلمة أو العبارة المسببة. «غير متأكد» لا تُحسب سليمة: تُبلَّغ منفصلة وتُستبعد في تحليل الحساسية الصارم. لا تصحّح النص.',False),
 ('الأسئلة التخصصية الملتبسة (طب/قانون/رياضيات) تُحال إلى مختص؛ اكتب «يحتاج مختص» في الملاحظات.',False),
 ('سياسة معلنة مسبقًا: لا يُصحَّح ولا يُستبعد أي سؤال من التحليلات الرئيسية بأثر رجعي. يُستخدم التدقيق لتقدير نسبة الأزواج المعيبة لكل لهجة (مع فاصل ثقة يراعي التعنقد في الأسئلة)، ولتحليل حساسية مُعلن: استبعاد الأزواج المعيبة (س1 أو س2 = لا)، ثم الصارم (أي «لا» أو «غير متأكد» في س1–س3)، وحد محافظ: لا يمكن لاستبعاد نسبة f من الأزواج أن يغيّر أي مؤشر نسبي بأكثر من f.',False),
 ('المصدر: MBZUAI/Dialectal-Arabic-MMLU (CC-BY-4.0). العينة: audit/audit_keys.json (بذرتا 20261104 و20261106).',False)]
def instr_sheet(ws, extra=None):
    ws.sheet_view.rightToLeft=True; ws.column_dimensions['A'].width=130
    items=INSTR+([extra] if extra else [])
    for i,(t,b) in enumerate(items,1):
        c=ws.cell(row=i,column=1,value=t); c.font=Font(name='Arial',size=12 if b else 10,bold=b); c.alignment=WR; ws.row_dimensions[i].height=30 if b else 52
# ---------------- rater 1 ----------------
wb=Workbook(); instr_sheet(wb.active); wb.active.title='التعليمات'
ws=wb.create_sheet('التدقيق'); n1=audit_sheet(ws,pairs)
sm=wb.create_sheet('ملخص'); sm.sheet_view.rightToLeft=True
hdr=['اللهجة','أزواج مقيَّمة (س1 وس2 معبّآن)','س1 = لا','س2 = لا','س3 = لا','س4 = لا','أزواج فيها «غير متأكد» (أي فحص)','أزواج معيبة (س1 أو س2 = لا)','نسبة المعيب من المقيَّم','نسبة المعيب+غير متأكد (صارم، س1–س3)']
for j,h in enumerate(hdr,1):
    c=sm.cell(row=1,column=j,value=h); c.font=HFont; c.fill=HF; c.alignment=Alignment(wrap_text=True,horizontal='center',vertical='center'); sm.column_dimensions[L(j)].width=20
sm.row_dimensions[1].height=58
A=f"التدقيق!$I$2:$I${n1}"; Q={q:f"التدقيق!${c}$2:${c}${n1}" for q,c in zip(['Q1','Q2','Q3','Q4'],QCOLS)}
def put(r,c,v,fmt=None,bold=False):
    x=sm.cell(row=r,column=c,value=v); x.font=FB if bold else F; x.border=BRD
    if fmt: x.number_format=fmt
for i,d in enumerate(DIAL,2):
    put(i,1,DN[d]); sel=f"({A}=A{i})"
    rated=f'SUMPRODUCT({sel}*({Q["Q1"]}<>"")*({Q["Q2"]}<>""))'; put(i,2,"="+rated)
    for j,q in enumerate(['Q1','Q2','Q3','Q4'],3): put(i,j,f'=SUMPRODUCT({sel}*({Q[q]}="لا"))')
    put(i,7,f'=SUMPRODUCT({sel}*((({Q["Q1"]}="غير متأكد")+({Q["Q2"]}="غير متأكد")+({Q["Q3"]}="غير متأكد")+({Q["Q4"]}="غير متأكد"))>0))')
    put(i,8,f'=SUMPRODUCT({sel}*((({Q["Q1"]}="لا")+({Q["Q2"]}="لا"))>0))')
    put(i,9,f'=IF(B{i}=0,"",H{i}/B{i})','0.0%')
    put(i,10,f'=IF(B{i}=0,"",SUMPRODUCT({sel}*({Q["Q1"]}<>"")*({Q["Q2"]}<>"")*((({Q["Q1"]}<>"نعم")+({Q["Q2"]}<>"نعم")+(({Q["Q3"]}<>"نعم")*({Q["Q3"]}<>"")))>0))/B{i})','0.0%')
r=len(DIAL)+2; put(r,1,'الإجمالي',bold=True)
for j in range(2,9): put(r,j,f'=SUM({L(j)}2:{L(j)}{r-1})',bold=True)
put(r,9,f'=IF(B{r}=0,"",H{r}/B{r})','0.0%',True)
put(r,10,f'=IF(B{r}=0,"",SUMPRODUCT(({Q["Q1"]}<>"")*({Q["Q2"]}<>"")*((({Q["Q1"]}<>"نعم")+({Q["Q2"]}<>"نعم")+(({Q["Q3"]}<>"نعم")*({Q["Q3"]}<>"")))>0))/B{r})','0.0%',True)
r+=2; put(r,1,'حسب المصدر',bold=True); S=f"التدقيق!$B$2:$B${n1}"
for i,src in enumerate(['تجريبي','تأكيدي']):
    rr=r+1+i; put(rr,1,src); sel=f"({S}=A{rr})"
    put(rr,2,f'=SUMPRODUCT({sel}*({Q["Q1"]}<>"")*({Q["Q2"]}<>""))'); put(rr,8,f'=SUMPRODUCT({sel}*((({Q["Q1"]}="لا")+({Q["Q2"]}="لا"))>0))'); put(rr,9,f'=IF(B{rr}=0,"",H{rr}/B{rr})','0.0%')
r+=4; sm.cell(row=r,column=1,value='ملاحظة: المقامات = الأزواج التي عُبّئ فيها س1 وس2 معًا؛ النسب تبقى فارغة حتى يبدأ التقييم. نسبة العيوب على مستوى اللهجة تُعامل في التحليل كعناقيد (50+30 سؤالًا)، لا 400 مشاهدة مستقلة.').font=F
wb.save('audit/rater1_DAMM_audit.xlsx')
# ---------------- rater 2 (no rater-1 data) ----------------
wb2=Workbook(); instr_sheet(wb2.active,('ملاحظة للمقيّم الثاني: هذا الملف مستقل؛ لا تطّلع على تقييم المقيّم الأول قبل تسليم ملفك. يحوي 150 زوجًا (20 سؤالًا تجريبيًا + 10 أسئلة تأكيدية × 5 لهجات).',False)); wb2.active.title='التعليمات'
p2=[p for p in pairs if p['key'] in dbl]; ws2=wb2.create_sheet('التدقيق'); n2=audit_sheet(ws2,p2); wb2.save('audit/rater2_DAMM_audit.xlsx')
# ---------------- adjudication workbook ----------------
wb3=Workbook(); w=wb3.active; w.title='التعليمات'; w.sheet_view.rightToLeft=True; w.column_dimensions['A'].width=130
for i,t in enumerate(['ملف التحكيم: الصق ورقة «التدقيق» كاملة من ملف المقيّم الأول في الورقة «المقيّم 1»، ومن ملف المقيّم الثاني في «المقيّم 2» (من الخلية A1 بالترتيب نفسه للأعمدة). المطابقة تتم بمعرّف الزوج لا بترتيب الصفوف.',
 'ورقة «الاتفاق» تحسب لكل فحص: عدد الأزواج المقيَّمة من الاثنين، نسبة الاتفاق الملاحظ، الاتفاق المتوقع بالصدفة، ومعامل كابا لكوهين (3 فئات: نعم/لا/غير متأكد).',
 'ورقة «الخلافات» تعرض لكل زوج مزدوج التقييم قيمتَي المقيّمَين في س1–س4 وعلامة «خلاف» إن اختلفا في أي فحص؛ يحسمها مقيّم ثالث في العمود المخصص، ويُوثَّق الحسم.'],1):
    c=w.cell(row=i,column=1,value=t); c.font=F; c.alignment=WR; w.row_dimensions[i].height=60
for name in ['المقيّم 1','المقيّم 2']:
    s=wb3.create_sheet(name); s.sheet_view.rightToLeft=True
    for j,h in enumerate(HEAD,1):
        c=s.cell(row=1,column=j,value=h); c.font=HFont; c.fill=HF; c.alignment=Alignment(wrap_text=True,horizontal='center'); s.column_dimensions[L(j)].width=WID[j-1]
dis=wb3.create_sheet('الخلافات'); dis.sheet_view.rightToLeft=True
dh=['معرّف الزوج','اللهجة','س1 — م1','س1 — م2','س2 — م1','س2 — م2','س3 — م1','س3 — م2','س4 — م1','س4 — م2','خلاف؟','حسم المقيّم الثالث (س1/س2/س3/س4)','تعليل الحسم']
for j,h in enumerate(dh,1):
    c=dis.cell(row=1,column=j,value=h); c.font=HFont; c.fill=HF; c.alignment=Alignment(wrap_text=True,horizontal='center'); dis.column_dimensions[L(j)].width=14 if j<12 else 30
R1="'المقيّم 1'"; R2="'المقيّم 2'"; MAXR=1000
for i,p in enumerate(p2,2):
    dis.cell(row=i,column=1,value=p['pid']).font=F; dis.cell(row=i,column=2,value=DN[p['d']]).font=F
    col=3
    for qc in QCOLS:
        for R in (R1,R2):
            dis.cell(row=i,column=col,value=f'=IFERROR(INDEX({R}!${qc}$2:${qc}${MAXR},MATCH($A{i},{R}!$A$2:$A${MAXR},0)),"")').font=F; col+=1
    dis.cell(row=i,column=11,value=f'=IF(OR(C{i}="",D{i}="",E{i}="",F{i}=""),"",IF(OR(C{i}<>D{i},E{i}<>F{i},AND(G{i}<>"",H{i}<>"",G{i}<>H{i}),AND(I{i}<>"",J{i}<>"",I{i}<>J{i})),"خلاف","متفق"))').font=F
    for cc in (12,13): dis.cell(row=i,column=cc).fill=INF
nd=len(p2)+1
ag=wb3.create_sheet('الاتفاق'); ag.sheet_view.rightToLeft=True
ah=['الفحص','أزواج مقيَّمة من الاثنين','اتفاق ملاحظ p_o','اتفاق متوقع p_e','كابا لكوهين','خلافات']
for j,h in enumerate(ah,1):
    c=ag.cell(row=1,column=j,value=h); c.font=HFont; c.fill=HF; c.alignment=Alignment(wrap_text=True,horizontal='center'); ag.column_dimensions[L(j)].width=22
cats=['نعم','لا','غير متأكد']
for i,(q,c1,c2) in enumerate([('س1','C','D'),('س2','E','F'),('س3','G','H'),('س4','I','J')],2):
    a=f"الخلافات!${c1}$2:${c1}${nd}"; b=f"الخلافات!${c2}$2:${c2}${nd}"; both=f'({a}<>"")*({b}<>"")'
    ag.cell(row=i,column=1,value=q).font=F
    ag.cell(row=i,column=2,value=f'=SUMPRODUCT({both})').font=F
    ag.cell(row=i,column=3,value=f'=IF(B{i}=0,"",SUMPRODUCT({both}*({a}={b}))/B{i})').font=F; ag.cell(row=i,column=3).number_format='0.000'
    pe="+".join([f'(SUMPRODUCT({both}*({a}="{k}"))/B{i})*(SUMPRODUCT({both}*({b}="{k}"))/B{i})' for k in cats])
    ag.cell(row=i,column=4,value=f'=IF(B{i}=0,"",{pe})').font=F; ag.cell(row=i,column=4).number_format='0.000'
    ag.cell(row=i,column=5,value=f'=IF(OR(B{i}=0,D{i}=1),"",(C{i}-D{i})/(1-D{i}))').font=F; ag.cell(row=i,column=5).number_format='0.000'
    ag.cell(row=i,column=6,value=f'=SUMPRODUCT({both}*({a}<>{b}))').font=F
ag.cell(row=7,column=1,value='تفسير إرشادي: كابا < 0.4 ضعيف، 0.4–0.6 متوسط، 0.6–0.8 جيد، > 0.8 ممتاز (Landis & Koch). تُبلَّغ القيم لكل فحص، لا نسبة إجمالية فقط.').font=F
wb3.save('audit/adjudication_DAMM_audit.xlsx')
print('pairs',len(pairs),'rater2 pairs',len(p2),'rows',n1,n2)
