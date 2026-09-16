/* Plain JavaScript; no accounts, database, paid services or build tools. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const STORAGE_KEY = 'swansea-isoc-saved-v1';
  const ICON_BOOKMARK = '<svg width="14" height="17" viewBox="0 0 16 19" fill="none" aria-hidden="true"><path d="M3 1.5h10v15L8 13l-5 3.5v-15Z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>';
  const ICON_CARD = '<svg viewBox="0 0 20 15" fill="none" aria-hidden="true"><rect x="1" y="1" width="18" height="13" rx="1" stroke="currentColor"/><path d="M1 5h18M4 10h4" stroke="currentColor"/></svg>';
  let data, preview, activeCategory='All', search='', savedOnly=false, saved=new Set(), toastTimer;
  const validStatus = new Set(['draft','review','published']);
  const isoDate = /^\d{4}-\d{2}-\d{2}$/;
  function el(tag, cls, text) { const e=document.createElement(tag); if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e; }
  function safeUrl(value) { try { const u=new URL(value);return ['https:','http:'].includes(u.protocol)?u.href:''; } catch { return ''; } }
  function external(text, url, cls='') { const a=el('a',cls,text);a.href=safeUrl(url);a.target='_blank';a.rel='noopener noreferrer';return a; }
  function dateLabel(value) { if(!isoDate.test(value||''))return '';const d=new Date(value+'T12:00:00Z');if(isNaN(d))return '';return d.toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric',timeZone:'Europe/London'}); }
  function today() { return new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/London',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date()); }
  function showToast(text) {clearTimeout(toastTimer);$('toast').textContent=text;$('toast').hidden=false;toastTimer=setTimeout(()=>$('toast').hidden=true,3200);}
  function readSaved(){try{const p=JSON.parse(localStorage.getItem(STORAGE_KEY)||'[]');if(Array.isArray(p))saved=new Set(p.filter(x=>typeof x==='string'));}catch{saved=new Set();}}
  function writeSaved(){try{localStorage.setItem(STORAGE_KEY,JSON.stringify([...saved]));return true;}catch{return false;}}
  function isPublished(o){
    if(o.status!=='published')return false;
    // Food entries must have a recorded branch-specific halal check before live publication.
    if(o.food && (o.halalStatus!=='confirmed'||!o.halalNote.trim()))return false;
    return true;
  }
  function visibleOffers(){return data.offers.filter(o=>['exclusive','general'].includes(o.kind)&&o.name&&o.discount&&((isPublished(o))||(preview&&o.status==='review'))&&(!isoDate.test(o.expiresOn||'')||o.expiresOn>=today()));}
  function isMatch(o){let searchable=[o.name,o.category,o.discount,o.strapline,o.address,o.area,o.claimMethod].join(' ').toLocaleLowerCase();return(activeCategory==='All'||o.category===activeCategory)&&(!search||searchable.includes(search))&&(!savedOnly||saved.has(o.id));}
  function appendList(parent, items, className, tag='ul'){const list=el(tag,className);(Array.isArray(items)?items:[]).filter(Boolean).forEach(t=>list.appendChild(el('li','',t)));parent.appendChild(list);}
  function saveOffer(o,button){
    if(saved.has(o.id))saved.delete(o.id);else saved.add(o.id);
    const persisted=writeSaved();
    button.setAttribute('aria-pressed',String(saved.has(o.id)));
    button.setAttribute('aria-label',(saved.has(o.id)?'Unsave ':'Save ')+o.name);
    updateSavedCount();
    showToast((saved.has(o.id)?'Saved ':'Removed ')+o.name+(persisted?'':'. This browser cannot save it after you close the page.'));
    if(savedOnly)render();
  }
  async function shareOffer(o){
    let text=o.name+' · '+o.discount+'\n'+(o.kind==='exclusive'?'ISOC discount card':'General student offer')+' · '+o.claimMethod;
    if(!isPublished(o))text+='\nCommittee preview only — this offer is not confirmed.';
    let url='';
    if(/^https?:$/.test(location.protocol)){const u=new URL(location.href);u.search='';u.hash='offer-'+o.id;url=u.href;}
    const shareData={title:'Swansea ISOC · '+o.name,text,...(url?{url}:{})};
    if(navigator.share){try{await navigator.share(shareData);return;}catch(e){if(e.name==='AbortError')return;}}
    const contents=text+(url?'\n'+url:'');
    try{await navigator.clipboard.writeText(contents);showToast('Offer details copied.');}catch{window.prompt('Copy these offer details:',contents);}
  }
  function card(o){
    const a=el('article','offer '+o.kind);a.id='offer-'+o.id;
    const top=el('div','offer-top'), main=el('div','offer-main');
    main.append(el('p','offer-kicker',o.category+' / '+o.area),el('h3','',o.name),el('p','offer-strapline',o.strapline));
    const stub=el('div','discount-stub');
    const match=o.discount.match(/^(.*?)(?:\s+(off|back|saving))$/i);
    stub.append(el('span','discount-value',match?match[1]:o.discount),el('span','discount-word',match?match[2]:'offer'),el('span','discount-type',o.kind==='exclusive'?'ISOC CARD':'STUDENT OFFER'));
    top.append(main,stub);a.appendChild(top);
    const save=el('button','save-offer');save.type='button';save.innerHTML=ICON_BOOKMARK;save.setAttribute('aria-label',(saved.has(o.id)?'Unsave ':'Save ')+o.name);save.setAttribute('aria-pressed',String(saved.has(o.id)));save.addEventListener('click',()=>saveOffer(o,save));a.append(save);
    const claim=el('div','claim-line');const icon=el('span');icon.innerHTML=ICON_CARD;claim.append(icon,el('span','',o.claimMethod));
    if(!isPublished(o))claim.appendChild(el('span','review-label','Offer to confirm'));
    a.appendChild(claim);
    const details=el('details','offer-details');const summary=el('summary','',isPublished(o)?'How to claim & details':'View offer details');summary.setAttribute('aria-label','Details for '+o.name);details.append(summary);
    const body=el('div','details-body');
    if(!isPublished(o))body.appendChild(el('p','review-note','Committee preview only. The rate is from the supplied draft, not a newly verified agreement. Do not rely on this offer until the committee confirms it.'));
    body.append(el('h4','',isPublished(o)?'How to claim':'Proposed claim method'));
    appendList(body,o.steps,'claim-steps','ol');
    if(o.address){body.append(el('h4','','Where to go'),el('address','address',o.address));}
    if(o.terms.length){body.append(el('h4','','The details'));appendList(body,o.terms,'terms');}
    if(o.food){const n=el('p','dietary-note');n.append(el('strong','',o.halalStatus==='confirmed'?'Halal information: ':'Halal check pending: '),document.createTextNode(o.halalNote||'Confirm directly with the venue.'));if(safeUrl(o.halalSourceUrl)){n.append(document.createTextNode(' '),external('Read source',o.halalSourceUrl));}body.append(n);}
    const actions=el('div','details-actions');
    if(o.address)actions.append(external('Directions','https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(o.name+', '+o.address)));
    if(o.kind==='general'&&safeUrl(o.sourceUrl)&&isPublished(o))actions.append(external('View provider offer',o.sourceUrl));
    else if(safeUrl(o.locationSourceUrl))actions.append(external('Visit website',o.locationSourceUrl));
    const share=el('button','','Share offer');share.type='button';share.addEventListener('click',()=>shareOffer(o));actions.append(share);body.append(actions);
    const source=el('p','source-note');source.append(document.createTextNode('Offer source: '));
    if(safeUrl(o.sourceUrl))source.append(external(o.sourceLabel||'Provider',o.sourceUrl));else source.append(document.createTextNode(o.sourceLabel||'Committee confirmation pending'));
    if(o.checkedOn)source.append(document.createTextNode(' · Source checked '+dateLabel(o.checkedOn)));
    if(o.expiresOn)source.append(document.createTextNode(' · Ends '+dateLabel(o.expiresOn)));
    body.append(source);details.append(body);a.append(details);return a;
  }
  function renderFilters(){
    const cats=['All',...new Set(visibleOffers().map(o=>o.category))];if(!cats.includes(activeCategory))activeCategory='All';
    $('category-filters').replaceChildren();
    cats.forEach(c=>{const b=el('button','filter-button',c==='All'?'All places':c);b.type='button';b.setAttribute('aria-pressed',String(c===activeCategory));b.addEventListener('click',()=>{activeCategory=c;[...$('category-filters').children].forEach(x=>x.setAttribute('aria-pressed',String(x===b)));render();});$('category-filters').append(b);});
  }
  function updateSavedCount(){const count=visibleOffers().filter(o=>saved.has(o.id)).length;$('saved-count').textContent=count;$('saved-toggle').setAttribute('aria-pressed',String(savedOnly));}
  function render(){
    const visible=visibleOffers(), matching=visible.filter(isMatch);
    const filtering=activeCategory!=='All'||!!search||savedOnly;
    ['exclusive','general'].forEach(kind=>{
      const container=$(kind+'-offers'),section=$(kind);container.replaceChildren();
      const items=matching.filter(o=>o.kind===kind);
      $('nav-'+kind+'-count').textContent=visible.filter(o=>o.kind===kind).length;
      section.hidden=filtering&&!items.length;
      items.forEach(o=>container.appendChild(card(o)));
      if(!items.length&&!filtering){const empty=el('div','empty-state');empty.append(el('h3','',kind==='exclusive'?'More local offers are on their way.':'Student offers are being checked.'),el('p','',kind==='exclusive'?'Confirmed ISOC card offers will appear here. Check the student section below in the meantime.':'We’ll list the provider and how to claim each one.'));container.append(empty);}
    });
    $('no-results').hidden=matching.length>0||!filtering;
    if(savedOnly&&!matching.length){$('empty-title').textContent='Keep your favourites here.';$('empty-text').textContent='Tap the bookmark beside an offer to save it on this device.';}else{$('empty-title').textContent='No offers match just yet.';$('empty-text').textContent='Try another place, area or category.';}
    const reviewCount=matching.filter(o=>!isPublished(o)).length;
    $('result-summary').textContent=matching.length+' '+(matching.length===1?'offer':'offers')+(savedOnly?' saved':' to explore')+(reviewCount?' · '+reviewCount+' awaiting confirmation':'');
    $('clear-search').hidden=!$('search').value;
    updateSavedCount();
  }
  function applyHash(){if(location.hash.startsWith('#offer-')){const target=document.getElementById(location.hash.slice(1));if(target){target.querySelector('details').open=true;requestAnimationFrame(()=>target.scrollIntoView({block:'center',behavior:'instant'}));}}}
  function init(){
    if(!window.ISOC_DATA||!Array.isArray(window.ISOC_DATA.offers)){ $('load-error').hidden=false;$('exclusive').hidden=true;$('general').hidden=true;return; }
    data=window.ISOC_DATA;data.site=data.site||{};
    // Ignore invalid records instead of breaking the entire directory.
    const ids=new Set();
    data.offers=data.offers.filter(o=>{if(!o||!o.id||!/^[a-z0-9-]+$/.test(o.id)||ids.has(o.id)||!validStatus.has(o.status))return false;ids.add(o.id);return true;}).map(o=>({...o,terms:Array.isArray(o.terms)?o.terms:[],steps:Array.isArray(o.steps)?o.steps:[],halalNote:String(o.halalNote||''),name:String(o.name||''),discount:String(o.discount||'')}));
    preview=data.site.previewMode===true;
    const query=new URLSearchParams(location.search);
    if(query.get('view')==='public')preview=false; // Inspection only; not authentication.
    $('preview-banner').hidden=!preview;
    $('public-preview').addEventListener('click',()=>{preview=false;$('preview-banner').hidden=true;activeCategory='All';renderFilters();render();showToast('Public view: only published offers are shown. Reload to return to this preview.');});
    $('edition').textContent=data.site.year||'SWANSEA';
    if(dateLabel(data.site.lastUpdated))$('updated-label').textContent='Directory updated '+dateLabel(data.site.lastUpdated);
    readSaved();renderFilters();render();applyHash();
    $('search').addEventListener('input',e=>{search=e.target.value.trim().toLocaleLowerCase();render();});
    $('clear-search').addEventListener('click',()=>{$('search').value='';search='';render();$('search').focus();});
    $('saved-toggle').addEventListener('click',()=>{savedOnly=!savedOnly;render();});
    $('reset-filters').addEventListener('click',()=>{search='';activeCategory='All';savedOnly=false;$('search').value='';renderFilters();render();});
    window.addEventListener('hashchange',applyHash);
    window.addEventListener('storage',e=>{if(e.key===STORAGE_KEY){readSaved();render();}});
  }
  init();
})();
