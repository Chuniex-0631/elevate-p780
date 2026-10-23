"""Offline inventory of exported XML and public OTA certificates; no device access."""
import pathlib,sys,json,hashlib,zipfile,xml.etree.ElementTree as E,argparse
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'.research-deps'))
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding
p=argparse.ArgumentParser();p.add_argument('capture',type=pathlib.Path);a=p.parse_args();d=a.capture
xmls=[];errors=[];hals=[]
for f in sorted((d/'vintf').rglob('*.xml')):
 try:r=E.fromstring(f.read_bytes())
 except Exception as e:errors.append(dict(path=f.relative_to(d).as_posix(),error=str(e)));continue
 name=f.relative_to(d).as_posix();xmls.append(dict(path=name,tag=r.tag,attributes=r.attrib,hal_entries=len(r.findall('hal'))))
 for h in r.findall('hal'):
  hals.append(dict(path=name,root=r.tag,root_attributes=r.attrib,format=h.get('format'),optional=h.get('optional'),name=h.findtext('name'),versions=[x.text for x in h.findall('version')],transport=h.findtext('transport'),fqnames=[x.text for x in h.findall('fqname')],interfaces=[dict(name=i.findtext('name'),instances=[x.text for x in i.findall('instance')],regex_instances=[x.text for x in i.findall('regex-instance')]) for i in h.findall('interface')]))
certs=[]
with zipfile.ZipFile(d/'otacerts.zip') as z:
 assert z.testzip() is None
 for info in z.infolist():
  if info.is_dir():continue
  b=z.read(info);c=x509.load_pem_x509_certificate(b) if b'BEGIN CERTIFICATE' in b else x509.load_der_x509_certificate(b)
  pub=c.public_key();spki=pub.public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
  self_signed=False
  if c.subject==c.issuer:
   try:pub.verify(c.signature,c.tbs_certificate_bytes,padding.PKCS1v15(),c.signature_hash_algorithm);self_signed=True
   except Exception:pass
  certs.append(dict(zip_entry=info.filename,raw_size=len(b),raw_sha256=hashlib.sha256(b).hexdigest(),certificate_der_sha256=c.fingerprint(hashes.SHA256()).hex(),subject=c.subject.rfc4514_string(),issuer=c.issuer.rfc4514_string(),valid_from=c.not_valid_before_utc.isoformat(),valid_until=c.not_valid_after_utc.isoformat(),key_type=type(pub).__name__,key_bits=getattr(pub,'key_size',None),spki_sha256=hashlib.sha256(spki).hexdigest(),signature_algorithm=c.signature_algorithm_oid.dotted_string,signature_hash=c.signature_hash_algorithm.name,self_signature_valid=self_signed))
old=d.parent/'13-dsu-readonly/vendor-manifest.xml';new=d/'vintf/vendor/manifest.xml'
r=dict(date='2026-10-24',xml_files=len(xmls),xml_errors=errors,xml_inventory=xmls,hal_declarations=hals,ota_certificates=certs,vendor_main_matches_20261019=old.read_bytes()==new.read_bytes(),limitations=['HAL declarations are not runtime liveness or authorization evidence.','This is not a merged libvintf check; active APEX fragments and device runtime info are not merged.','OTA cert/SPKI fingerprints are distinct encodings and trust domains from an AVB public-key blob or EDL PKHash.','A public verification certificate neither provides a signing private key nor proves payload verifier/recovery uses identical roots.'])
(d/'analysis.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:r[k] for k in ['xml_files','xml_errors','ota_certificates','vendor_main_matches_20261019']},ensure_ascii=False,indent=2))
print(json.dumps([h for h in hals if any(x in (h['name'] or '') for x in ['boot','diaghal','warehouse','qseecom'])],indent=2))
