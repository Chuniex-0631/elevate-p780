"""Evidence-specific adversarial checks; no phone operations."""
import argparse,pathlib,json
from compare_policy_records import compare
p=argparse.ArgumentParser();p.add_argument('policy',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
raw=a.policy.read_bytes();off=0x25602;checks={}
r=compare(raw,raw,off);assert r['binary_equal'] and r['all_compared_records_equal'];checks['identity']='passed'
changed=bytearray(raw);changed[off+12]^=1
r=compare(raw,bytes(changed),off);s=r['sections']['unconditional_avtab'];assert not r['all_compared_records_equal'] and s['only_live']==s['only_disk']==1;checks['one_avtab_datum_change_detected']='passed'
changed=bytearray(raw);start=r['sections']['ordered_type_attribute_bitmaps']['live']['offset'];changed[start+16]^=1
r=compare(raw,bytes(changed),off);assert not r['sections']['ordered_type_attribute_bitmaps']['record_multiset_equal'];checks['attribute_bitmap_change_detected']='passed'
for name,changed in [('truncated',raw[:-1]),('changed_symbol_prefix',raw[:100]+bytes([raw[100]^1])+raw[101:])]:
 try:compare(raw,changed,off)
 except (AssertionError,ValueError):checks[name+'_rejected']='passed'
 else:raise AssertionError(name+' accepted')
changed=bytearray(raw);co=r['live']['header']['config_offset'];changed[co+3]^=0x80
r=compare(raw,bytes(changed),off);assert not r['binary_equal'] and r['live']['header']!=r['disk']['header'];checks['header_difference_retained']='passed'
a.output.write_text(json.dumps(dict(checks=checks,scope='Custom pair-specific comparator checks, not independent SETools validation'),indent=2)+'\n',encoding='utf-8');print(json.dumps(checks))

