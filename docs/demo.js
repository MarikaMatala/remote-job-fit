(() => {
"use strict";
const $=id=>document.getElementById(id);
const skills=$("skills"),title=$("job-title"),ad=$("job-ad"),results=$("results"),count=$("count");
const samples={
 frontend:{title:"Junior Frontend Developer",text:"We are looking for a Junior Frontend Developer to join our product team.\n\nRequired: Good knowledge of HTML, CSS and JavaScript. You will work with React and TypeScript to build accessible, responsive user interfaces.\n\nAt least 1 year of relevant professional experience is preferred. Personal or university projects are also valued. Familiarity with Git is a plus.\n\nWe welcome applicants who are eager to learn and collaborate.",skills:"JavaScript, TypeScript, React, HTML, CSS, Git, responsive design, accessibility, UI/UX"},
 python:{title:"Python Developer",text:"We require strong Python skills and experience building REST APIs. 3+ years of professional experience is required. Experience with SQL and Docker is preferred. Knowledge of cloud platforms is a plus. This is a mid-level role.",skills:"Python, SQL, REST API, FastAPI, Docker, Git, testing, cloud"},
 media:{title:"Digital Content Producer",text:"We are seeking a digital content producer with experience in photography, video editing and social media. 2–4 years of relevant experience would be an advantage. Familiarity with Adobe Premiere, Photoshop and content management systems is preferred. Strong written communication skills are essential.",skills:"Photography, video editing, Adobe Premiere, Photoshop, social media, WordPress, communication, content production"},
 design:{title:"Junior UI/UX Designer",text:"We are looking for a junior UI/UX designer to help create accessible digital services. Experience with Figma, prototyping, user research and responsive design is preferred. A portfolio demonstrating visual design and interaction design skills is required. Internship, study and personal project experience are welcome.",skills:"Figma, UI/UX, prototyping, user research, responsive design, accessibility, visual design, HTML, CSS"}
};
const initial={title:title.value,text:ad.value,skills:skills.value};
let language="fi",lastAnalysis=null;
const esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const norm=s=>String(s).normalize("NFKC").toLocaleLowerCase("fi-FI");
const lines=s=>s.split(/(?<=[.!?;])\s+|[\r\n]+/).map(x=>x.trim()).filter(Boolean);
const t=(fi,en)=>language==="fi"?fi:en;
function classify(line){
 const s=norm(line);
 if(/\b(optional|not required|would be helpful|familiarity with)\b/.test(s))return"optional";
 if(/\b(preferred|preferably|nice to have|good to have|a plus|would be an advantage|bonus|desirable)\b|eduksi|katsotaan eduksi|toivottavaa/.test(s))return"preferred";
 if(/\b(required|requirement|essential|mandatory|we require|must have|proficient in)\b|vaaditaan|edellytetään|pakollinen|vähintään/.test(s))return"required";
 return"unspecified";
}
function experienceSignals(text){
 const out=[],range=/(\d+)\s*(?:-|–|to)\s*(\d+)\s*(?:years?|yrs?|vuotta|vuoden)/i,single=/(\d+)\s*\+?\s*(?:years?|yrs?|vuotta|vuoden)/i;
 const levels=[["entry",/\b(intern|internship|graduate|entry[- ]level|junior|trainee)\b|harjoittelija/i],["mid",/\b(mid[- ]level|intermediate|regular)\b|keskitaso/i],["senior",/\b(senior|lead|principal|staff engineer|head of)\b|seniori|johtava/i]];
 for(const line of lines(text)){const r=line.match(range),n=line.match(single),level=levels.find(([,re])=>re.test(line));if(!r&&!n&&!level)continue;
  const scope=/\b(project|projects|project-based|portfolio)\b|projekti/i.test(line)?t("Projekti","Project"):/\b(industry|sector|domain|commercial) experience\b|toimiala/i.test(line)?t("Toimiala","Industry"): /\b(professional|employment|work) experience\b|työkokem/i.test(line)?t("Ammatillinen","Professional"):t("Yleinen","General");
  out.push({years:r?r[1]+"–"+r[2]+" "+t("vuotta","years"):n?n[1]+(/\d+\s*\+/.test(line)?"+ ":" ")+t("vuotta","years"):"",level:level?level[0]:"",scope,evidence:line});
 }return out;
}
function analyse(){
 const profile=[...new Set(skills.value.split(/[,;\n]/).map(s=>s.trim()).filter(Boolean))],jobLines=lines(title.value+"\n"+ad.value),weights={required:1.5,preferred:1,optional:.75,unspecified:1};
 let earned=0,total=0;const matched=[],missing=[];
 for(const skill of profile){const key=norm(skill),line=jobLines.find(s=>norm(s).includes(key));const kind=line?classify(line):"unspecified";total+=weights[kind];if(line){earned+=weights[kind];matched.push({skill,kind})}else missing.push(skill)}
 const pct=total?Math.round(earned/total*100):0,exp=experienceSignals(title.value+"\n"+ad.value);lastAnalysis={pct,matched,missing,exp};
 const chips=(arr,isMissing=false)=>arr.length?arr.map(x=>'<span class="chip '+(isMissing?'missing':'')+'">'+esc(x.skill)+' <small>· '+esc(t(x.kind==="required"?"Pakollinen":x.kind==="preferred"?"Toivottu":x.kind==="optional"?"Valinnainen":"Ei luokiteltu",x.kind))+'</small></span>').join(""):'<span class="hint">'+t("Ei tunnistettuja osumia.","No matches identified.")+'</span>';
 const expHtml=exp.length?exp.map(x=>'<div class="experience"><strong>'+esc([x.years,x.level].filter(Boolean).join(" · ")||t("Kokemusmaininta","Experience signal"))+'</strong><small>'+esc(x.scope+" · "+x.evidence)+'</small></div>').join(""):'<p class="hint">'+t("Kokemusvuosia tai senioriteettia kuvaavia ilmauksia ei tunnistettu.","No years-of-experience or seniority signals were recognised.")+'</p>';
 results.innerHTML='<div class="result-head"><div><p class="eyebrow">'+t("ANALYYSI VALMIS","ANALYSIS COMPLETE")+'</p><h2>'+esc(title.value||t("Työpaikkailmoitus","Job advert"))+'</h2><p class="summary">'+matched.length+" / "+profile.length+" "+t("profiilin osaamista tunnistettiin ilmoituksesta.","profile skills recognised in the advert.")+'</p></div><div class="score"><strong>'+pct+'%</strong><small>'+t("DEMO-OSUMA","DEMO MATCH")+'</small></div></div><div class="meter" role="img" aria-label="'+pct+'%"><span style="width:'+pct+'%"></span></div><p class="hint">'+t("Suuntaa antava avainsanavertailu — ei arvio todellisesta soveltuvuudesta.","Indicative keyword comparison — not an assessment of real-world suitability.")+'</p><div class="columns"><article class="card"><h3>✓ '+t("Tunnistetut osaamiset","Matched skills")+' ('+matched.length+')</h3><div class="chips">'+chips(matched)+'</div></article><article class="card"><h3>＋ '+t("Profiilista puuttuvat","Not in profile")+' ('+missing.length+')</h3><div class="chips">'+chips(missing,true)+'</div></article></div><article class="card"><h3>'+t("Kokemus- ja senioriteettivihjeet","Experience and seniority signals")+' ('+exp.length+')</h3>'+expHtml+'</article>';
 results.scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth",block:"start"});
}
function updateCount(){count.textContent=ad.value.length.toLocaleString(language==="fi"?"fi-FI":"en-US")+" / 12 000"}
function setLanguage(next){
 language=next;document.documentElement.lang=next;
 document.querySelectorAll("[data-fi][data-en]").forEach(el=>{const value=el.dataset[next];if(value!==undefined)el.textContent=value});
 document.querySelectorAll("[data-fi-aria-label][data-en-aria-label]").forEach(el=>el.setAttribute("aria-label",el.dataset[next==="fi"?"fiAriaLabel":"enAriaLabel"]));
 document.querySelectorAll("[data-fi-placeholder][data-en-placeholder]").forEach(el=>el.placeholder=el.dataset[next==="fi"?"fiPlaceholder":"enPlaceholder"]);
 $("demo-language").setAttribute("aria-label",next==="fi"?"Change language":"Vaihda kieltä");
 updateCount();if(lastAnalysis)analyse();
}
document.querySelectorAll("[data-sample]").forEach(b=>b.addEventListener("click",()=>{const s=samples[b.dataset.sample];title.value=s.title;ad.value=s.text;updateCount()}));
document.querySelectorAll("[data-profile]").forEach(b=>b.addEventListener("click",()=>{skills.value=samples[b.dataset.profile].skills}));
ad.addEventListener("input",updateCount);
$("analyze").addEventListener("click",analyse);
$("reset-demo").addEventListener("click",()=>{title.value=initial.title;ad.value=initial.text;skills.value=initial.skills;lastAnalysis=null;updateCount();results.innerHTML='<div class="placeholder"><p class="eyebrow">'+t("03 / VERTAILUN TULOS","03 / MATCH RESULTS")+'</p><h2>'+t("Tulokset ilmestyvät tähän","Your results will appear here")+'</h2><p>'+t("Kun olet valmis, käynnistä analyysi.","Run the analysis when you are ready.")+'</p></div>'});
$("demo-language").addEventListener("click",()=>setLanguage(language==="fi"?"en":"fi"));
updateCount();
})();