import json
d=json.load(open('data_src.json'))
allse=[s for w in d['SBW'].values() for s in w]
done=[s for s in allse if (s.get('realise') or {}).get('statut') in ('fait','partiel')]
d['SAISON2026']={'sorties':len(done),
  'km':round(sum((s.get('realise') or {}).get('km',0) for s in done)),
  'elev':round(sum((s.get('realise') or {}).get('dplus',0) for s in done)),
  'mois':'2026'}
json.dump(d,open('data.json','w',encoding='utf-8'),ensure_ascii=False)
print('Semaines:',len(d['SBW']),'| Seances:',sum(len(v) for v in d['SBW'].values()),'| Saison:',d['SAISON2026']['sorties'],'sorties /',d['SAISON2026']['km'],'km')
