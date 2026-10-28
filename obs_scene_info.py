"""Describe the active OBS scene for Dock without changing overlay pages or URLs."""
def dock_scene(layout, scene):
    pages=(layout or {}).get('pages') or []
    active=next((p for p in pages if p.get('id')==(layout or {}).get('activePageId')),pages[0] if pages else {})
    def resolve(value):
        if not value:return active
        if str(value).isdigit() and 1<=int(value)<=len(pages):return pages[int(value)-1]
        return next((p for p in pages if str(p.get('id','')).lower()==str(value).lower() or str(p.get('name','')).lower()==str(value).lower()),pages[0] if pages else {})
    result={**scene,'sources':[]}
    for source in scene.get('sources',[]):
        page=resolve(source.get('pinned_page'))
        widgets=[dict(w,enabled=not w.get('hidden',False),name=w.get('title',w.get('name',w.get('type','')))) for w in page.get('widgets',[])]
        result['sources'].append({**source,'display_page_id':page.get('id',''),'display_page_name':page.get('name',page.get('id','')),'widgets':widgets})
    if result['sources']:
        first=result['sources'][0];result.update(source_name=first['source_name'],is_pinned=first['is_pinned'],pinned_page=first['pinned_page'],display_page_id=first['display_page_id'],display_page_name=first['display_page_name'])
    else:result.update(source_name='',is_pinned=False,pinned_page=None,display_page_id=active.get('id',''),display_page_name=active.get('name',active.get('id','')))
    result['multiple_sources']=len(result['sources'])>1
    return result
