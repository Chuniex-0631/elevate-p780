# DSU read-only follow-up tools

Python standard-library tools for exported P780 files and the existing raw ext4 Android15 A image. No image download, mounting, execution or repair.

```powershell
python tools/dsu/read_gsi_vintf.py SYSTEM_IMG --output CAPTURE/gsi-vintf
python tools/dsu/dsu_vintf_subset.py --capture CAPTURE --config CONFIG_GZ --image SYSTEM_IMG
```

CAPTURE must contain the ADB-exported vendor-manifest.xml and vendor-compatibility-matrix.xml. The ext4 reader supports bounded regular files/directories with extent trees only. It does not validate filesystem checksums or implement a general ext4 driver. The subset checker verifies selected 5.4.61 FCM5 kernel configs and streams the image SHA256; it is not checkvintf and does not merge APEX/ODM/framework fragments, match all HALs or prove bootability.

`dsu_state_readonly.py --output CAPTURE` is a fixed ADB status/property/dumpsys whitelist. It does not install/enable/disable/remove/reboot. Status queries can start the lazy GSID service. Do not rerun completed snapshots without an evidence need. Denied metadata paths are documented rather than probed by this tool.

See [the report](../../docs/research/p780-dsu-readonly-followup-20261019.md) and [the input/condition rows](../../evidence/dsu/20261019-readonly/vintf-subset.json). Full image and other extracted XML remain on the owner's PC. Git contains selected XML originals, hashes, state excerpts and derived comparison only.
