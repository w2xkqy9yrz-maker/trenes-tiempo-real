import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import update
NOW=1793836800
class TestSources(unittest.TestCase):
 def test_header_only(self):
  rows,note=update.renfe({'header':{'timestamp':NOW}},'commuter')
  self.assertEqual(rows,[]);self.assertIn('sin entity',note)
 def test_renfe_vehicle(self):
  data={'header':{'timestamp':NOW},'entity':[{'id':'a','vehicle':{'timestamp':NOW,'vehicle':{'id':'123','label':'C3'},'position':{'latitude':40.4,'longitude':-3.7,'speed':10}}}]}
  rows,_=update.renfe(data,'commuter');self.assertEqual(rows[0]['speed'],36)
 def test_radar_nested(self):
  rows,_=update.radar({'data':{'trains':[{'id':'7','position':{'lat':41.4,'lng':2.1},'timestamp':NOW}]}})
  self.assertEqual(len(rows),1)
 def test_reject_old_and_missing_time(self):
  feeds=[{'header':{'timestamp':NOW},'entity':[]},{'header':{'timestamp':NOW},'entity':[]},{'trains':[{'id':'1','lat':40,'lon':-3,'timestamp':NOW-9000},{'id':'2','lat':40,'lon':-3}]}]
  it=iter(feeds);result=update.build(fetcher=lambda _:next(it),now=NOW)
  self.assertEqual(result['count'],0)
 def test_stale_preservation(self):
  it=iter([{'header':{}},{'header':{}},{'trains':[]}]);prev={'trains':[{'id':'old'}]}
  r=update.build(fetcher=lambda _:next(it),now=NOW,previous=prev)
  self.assertTrue(r['stale']);self.assertEqual(r['count'],1)
 def test_error_does_not_abort(self):
  r=update.build(fetcher=lambda _:(_ for _ in ()).throw(OSError('offline')),now=NOW)
  self.assertEqual(r['count'],0);self.assertFalse(r['sources']['radar']['ok'])
if __name__=='__main__':unittest.main()
