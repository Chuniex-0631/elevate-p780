# P780 source-vs-device configuration drift

Original 5238; resolved 5541

## changed (2)
- CONFIG_CC_VERSION_TEXT: "Android (6877366 based on r383902b1) clang version 11.0.2 (https://android.googlesource.com/toolchain/llvm-project b397f81060ce6d701042b782172ed13bee898b79)" -> "Ubuntu clang version 14.0.0-1ubuntu1.1"
- CONFIG_CLANG_VERSION: 110002 -> 140000

## removed (24)
- CONFIG_ABOV_SAR: y -> (absent)
- CONFIG_AW9610X_SAR: y -> (absent)
- CONFIG_BATTERY_PROTECT_LIMIT: n -> (absent)
- CONFIG_EXFAT_FS: n -> (absent)
- CONFIG_F2FS_CHECK_FS: n -> (absent)
- CONFIG_FINGERPRINT_FOCAL_FT9801_QSEE: n -> (absent)
- CONFIG_FINGERPRINT_GOODIX_GF9628_QSEE: y -> (absent)
- CONFIG_FORTIFY_SOURCE: y -> (absent)
- CONFIG_INPUT_FINGERPRINT: y -> (absent)
- CONFIG_IPA_ETH: n -> (absent)
- CONFIG_JEITA_WARM_OV_PROTECT: y -> (absent)
- CONFIG_LOWBATT_PWROFF: y -> (absent)
- CONFIG_NFC_PN533_I2C: n -> (absent)
- CONFIG_NFC_PN533_USB: n -> (absent)
- CONFIG_NFC_QTI_I3C_GPIO: n -> (absent)
- CONFIG_NFC_ST54J: m -> (absent)
- CONFIG_NVM: n -> (absent)
- CONFIG_REFCOUNT_FULL: y -> (absent)
- CONFIG_SCC_SUPPORT: y -> (absent)
- CONFIG_TINNO_DEMOMODECHG_CONTROL: y -> (absent)
- CONFIG_TINNO_LONGCHG_CONTROL: y -> (absent)
- CONFIG_TINNO_PRODUCT_INFO: y -> (absent)
- CONFIG_TINNO_WARM_RECHARGE_CONTROL: y -> (absent)
- CONFIG_USB_SWITCH: y -> (absent)

## added (327)
**Newly enabled:** 44 of 327; others recorded in config-changes.json
- CONFIG_ARM64_ERRATUM_1742098: (absent) -> y
- CONFIG_BLOCK_SUPPORT_STLOG: (absent) -> y
- CONFIG_CC_HAS_ASM_GOTO_OUTPUT: (absent) -> y
- CONFIG_CC_HAS_ASM_GOTO_TIED_OUTPUT: (absent) -> y
- CONFIG_CC_HAS_ASM_INLINE: (absent) -> y
- CONFIG_CC_HAS_AUTO_VAR_INIT_ZERO_ENABLER: (absent) -> y
- CONFIG_CC_HAVE_STACKPROTECTOR_SYSREG: (absent) -> y
- CONFIG_CRYPTO_LIB_BLAKE2S_GENERIC: (absent) -> y
- CONFIG_DIRECT_RECLAIM_FILE_PAGES_ONLY: (absent) -> y
- CONFIG_F2FS_SEC_BLOCK_OPERATIONS_DEBUG: (absent) -> y
- CONFIG_F2FS_STRICT_BUG_ON: (absent) -> y
- CONFIG_FAT_SUPPORT_STLOG: (absent) -> y
- CONFIG_FAT_UEVENT: (absent) -> y
- CONFIG_FUSE_SUPPORT_STLOG: (absent) -> y
- CONFIG_HYFI_BRIDGE_HOOKS: (absent) -> y
- CONFIG_INCREASE_MAXIMUM_SWAPPINESS: (absent) -> y
- CONFIG_ION_RBIN_HEAP: (absent) -> y
- CONFIG_MEMBLOCK_MEMSIZE: (absent) -> y
- CONFIG_MEMCG_FORCE_USE_VM_SWAPPINESS: (absent) -> y
- CONFIG_MEMCG_HEIMDALL: (absent) -> y
- CONFIG_MITIGATE_SPECTRE_BRANCH_HISTORY: (absent) -> y
- CONFIG_MMC_SUPPORT_STLOG: (absent) -> y
- CONFIG_NET_ANALYTICS: (absent) -> y
- CONFIG_PAGE_BOOST: (absent) -> y
- CONFIG_PAGE_BOOST_RECORDING: (absent) -> y
- CONFIG_PROC_DLOG: (absent) -> y
- CONFIG_PROC_FSLOG: (absent) -> y
- CONFIG_PROC_STLOG: (absent) -> y
- CONFIG_RBIN: (absent) -> y
- CONFIG_RELR: (absent) -> y
- CONFIG_SAMSUNG_LMKD_DEBUG: (absent) -> y
- CONFIG_SDFAT_ALIGNED_MPAGE_WRITE: (absent) -> y
- CONFIG_SDFAT_DBG_MSG: (absent) -> y
- CONFIG_SDFAT_DEBUG: (absent) -> y
- CONFIG_SDFAT_DELAYED_META_DIRTY: (absent) -> y
- CONFIG_SDFAT_FS: (absent) -> y
- CONFIG_SDFAT_STATISTICS: (absent) -> y
- CONFIG_SDFAT_SUPPORT_STLOG: (absent) -> y
- CONFIG_SDFAT_UEVENT: (absent) -> y
- CONFIG_SEC_EXT: (absent) -> y
- CONFIG_SEC_MM: (absent) -> y
- CONFIG_SEC_SS_CNSS_FEATURE_SYSFS: (absent) -> y
- CONFIG_STACKPROTECTOR_PER_TASK: (absent) -> y
- CONFIG_TOOLS_SUPPORT_RELR: (absent) -> y
