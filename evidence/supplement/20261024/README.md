# P780 supplemental acquisition, 2026-10-24

47 original system files: 46 VINTF XML files preserved under vintf/, and one otacerts.zip preserved reversibly as otacerts.zip.b64. files.json records the original sizes and SHA-256. No device private signing key was obtained.

commands.json is a labelled acquisition transcript with host output paths replaced by CAPTURE_DIR. analysis.json contains the XML inventory, HAL declaration/requirement rows, certificate fields and historical-manifest comparison. boot-diag-processes.txt is a narrowly filtered process-label snapshot. validation.json records pre-publication validation and retains its original not-performed publication field.

The original ZIP can be restored by Base64 decoding otacerts.zip.b64; verify size and SHA-256 against files.json. The certificate is a public verification artifact. XML declarations are not evidence of runtime service availability or permission to invoke them. Missing standard update_engine paths do not establish absence of other verifier keys.

Full findings and limitations: [report](../../../docs/research/p780-supplement-20261024.md).
