# P780 kernel config audit

Research-only cross-device build; do NOT flash this output to the device.

- Original parsed symbols: **5238**
- Resolved parsed symbols: **5541**
- Final parsed symbols: **5541**
- olddefconfig: **2 changed, 327 added, 24 removed**
- Compilation-stage drift: **0 changed, 0 added, 0 removed**
- Overall original to final: **2 changed, 327 added, 24 removed**

## Security and platform-critical symbols

| Symbol | Device original | After olddefconfig | After compile |
|---|---|---|---|
| CONFIG_ARCH_HOLI | y | y | y |
| CONFIG_ARCH_BLAIR | y | y | y |
| CONFIG_FUTEX_PI | y | y | y |
| CONFIG_RT_MUTEXES | y | y | y |
| CONFIG_LTO_CLANG | y | y | y |
| CONFIG_CFI_CLANG | y | y | y |
| CONFIG_MODVERSIONS | y | y | y |
| CONFIG_KALLSYMS | y | y | y |
| CONFIG_IKHEADERS | y | y | y |
| CONFIG_CC_VERSION_TEXT | "Android (6877366 based on r383902b1) clang version 11.0.2 (https://android.googlesource.com/toolchain/llvm-project b397f81060ce6d701042b782172ed13bee898b79)" | "Ubuntu clang version 14.0.0-1ubuntu1.1" | "Ubuntu clang version 14.0.0-1ubuntu1.1" |
| CONFIG_LOCALVERSION | "-qgki" | "-qgki" | "-qgki" |
| CONFIG_PREEMPT | y | y | y |
| CONFIG_KASLR | (missing) | (missing) | (missing) |

## Original to resolved details

### changed: 2
- CONFIG_CC_VERSION_TEXT: "Android (6877366 based on r383902b1) clang version 11.0.2 (https://android.googlesource.com/toolchain/llvm-project b397f81060ce6d701042b782172ed13bee898b79)" → "Ubuntu clang version 14.0.0-1ubuntu1.1"
- CONFIG_CLANG_VERSION: 110002 → 140000

### removed: 24
- CONFIG_ABOV_SAR: y → (missing)
- CONFIG_AW9610X_SAR: y → (missing)
- CONFIG_BATTERY_PROTECT_LIMIT: n → (missing)
- CONFIG_EXFAT_FS: n → (missing)
- CONFIG_F2FS_CHECK_FS: n → (missing)
- CONFIG_FINGERPRINT_FOCAL_FT9801_QSEE: n → (missing)
- CONFIG_FINGERPRINT_GOODIX_GF9628_QSEE: y → (missing)
- CONFIG_FORTIFY_SOURCE: y → (missing)
- CONFIG_INPUT_FINGERPRINT: y → (missing)
- CONFIG_IPA_ETH: n → (missing)
- CONFIG_JEITA_WARM_OV_PROTECT: y → (missing)
- CONFIG_LOWBATT_PWROFF: y → (missing)
- CONFIG_NFC_PN533_I2C: n → (missing)
- CONFIG_NFC_PN533_USB: n → (missing)
- CONFIG_NFC_QTI_I3C_GPIO: n → (missing)
- CONFIG_NFC_ST54J: m → (missing)
- CONFIG_NVM: n → (missing)
- CONFIG_REFCOUNT_FULL: y → (missing)
- CONFIG_SCC_SUPPORT: y → (missing)
- CONFIG_TINNO_DEMOMODECHG_CONTROL: y → (missing)
- CONFIG_TINNO_LONGCHG_CONTROL: y → (missing)
- CONFIG_TINNO_PRODUCT_INFO: y → (missing)
- CONFIG_TINNO_WARM_RECHARGE_CONTROL: y → (missing)
- CONFIG_USB_SWITCH: y → (missing)

### added: 327
- CONFIG_ADSP_FACTORY: (missing) → n
- CONFIG_AFC_CHARGER_MODE: (missing) → n
- CONFIG_AK09918_FACTORY: (missing) → n
- CONFIG_ARGOS: (missing) → n
- CONFIG_ARM64_ERRATUM_1742098: (missing) → y
- CONFIG_BATTERY_AGE_FORECAST: (missing) → n
- CONFIG_BATTERY_CISD: (missing) → n
- CONFIG_BATTERY_GKI: (missing) → n
- CONFIG_BATTERY_RT5033: (missing) → n
- CONFIG_BATTERY_SAMSUNG: (missing) → n
- CONFIG_BLK_SEC_STATS: (missing) → n
- CONFIG_BLOCK_SUPPORT_STLOG: (missing) → y
- CONFIG_BPF_UNPRIV_DEFAULT_OFF: (missing) → n
- CONFIG_CAMERA_ADAPTIVE_MIPI: (missing) → n
- CONFIG_CAMERA_FRAME_CNT_CHECK: (missing) → n
- CONFIG_CAMERA_FRAME_CNT_DBG: (missing) → n
- CONFIG_CAMERA_MCLK_DELAY: (missing) → n
- CONFIG_CAMERA_SSM_I2C_ENV: (missing) → n
- CONFIG_CAMERA_SYSFS_V2: (missing) → n
- CONFIG_CC_HAS_ASM_GOTO_OUTPUT: (missing) → y
- CONFIG_CC_HAS_ASM_GOTO_TIED_OUTPUT: (missing) → y
- CONFIG_CC_HAS_ASM_INLINE: (missing) → y
- CONFIG_CC_HAS_AUTO_VAR_INIT_ZERO_ENABLER: (missing) → y
- CONFIG_CC_HAVE_STACKPROTECTOR_SYSREG: (missing) → y
- CONFIG_CHARGER_SM5714: (missing) → n
- CONFIG_COMBO_REDRIVER_PS5169: (missing) → n
- CONFIG_COMBO_REDRIVER_PTN36502: (missing) → n
- CONFIG_CPU_FREQ_LIMIT: (missing) → n
- CONFIG_CP_DYNAMIC_MEM_RESERVE: (missing) → n
- CONFIG_CRYPTO_BLAKE2B: (missing) → n
- CONFIG_CRYPTO_BLAKE2S: (missing) → n
- CONFIG_CRYPTO_FIPS: (missing) → n
- CONFIG_CRYPTO_LIB_BLAKE2S_GENERIC: (missing) → y
- CONFIG_DC_VIBRATOR: (missing) → n
- CONFIG_DDAR: (missing) → n
- CONFIG_DEV_RIL_BRIDGE: (missing) → n
- CONFIG_DIRECT_CHARGING: (missing) → n
- CONFIG_DIRECT_RECLAIM_FILE_PAGES_ONLY: (missing) → y
- CONFIG_DISPLAY_SAMSUNG: (missing) → n
- CONFIG_DM_ANDROID_VERITY_AT_MOST_ONCE_DEFAULT_ENABLED: (missing) → n
- CONFIG_DM_VERITY_AVB: (missing) → n
- CONFIG_DPM_WATCHDOG: (missing) → n
- CONFIG_DRV_SAMSUNG: (missing) → n
- CONFIG_ENABLE_FULL_BY_SOC: (missing) → n
- CONFIG_ENABLE_USB_SUSPEND_STATE: (missing) → n
- CONFIG_ENG_BATTERY_CONCEPT: (missing) → n
- CONFIG_ESE_FACTORY_ONLY: (missing) → n
- CONFIG_ESE_P3_LSI: (missing) → n
- CONFIG_ESE_SECURE: (missing) → n
- CONFIG_ESE_USE_TZ_API: (missing) → n
- CONFIG_F2FS_SEC_BLOCK_OPERATIONS_DEBUG: (missing) → y
- CONFIG_F2FS_STRICT_BUG_ON: (missing) → y
- CONFIG_FAT_SUPPORT_STLOG: (missing) → y
- CONFIG_FAT_UEVENT: (missing) → y
- CONFIG_FAULT_AROUND_4KB: (missing) → n
- CONFIG_FINGERPRINT_SECURE: (missing) → n
- CONFIG_FIVE: (missing) → n
- CONFIG_FLASH_CURRENT_JAPAN: (missing) → n
- CONFIG_FLIP_COVER_DETECTOR_FACTORY: (missing) → n
- CONFIG_FUELGAUGE_SM5714: (missing) → n
- CONFIG_FUSE_SUPPORT_STLOG: (missing) → y
- CONFIG_GAF: (missing) → n
- CONFIG_GC5035_MACRO_OTP_DD_AUTOLOAD: (missing) → n
- CONFIG_GPIO_DS_DETECT: (missing) → n
- CONFIG_HYFI_BRIDGE_HOOKS: (missing) → y
- CONFIG_ICM4X6XX_FACTORY: (missing) → n
- CONFIG_ICNSS2_RESTART_LEVEL_NOTIF: (missing) → n
- CONFIG_IF_CB_MANAGER: (missing) → n
- CONFIG_INCREASE_MAXIMUM_SWAPPINESS: (missing) → y
- CONFIG_INET_TABLE_PERTURB_ORDER: (missing) → 16
- CONFIG_INPUT_SEC_INPUT: (missing) → n
- CONFIG_INPUT_SEC_NOTIFIER: (missing) → n
- CONFIG_INPUT_SEC_SECURE_TOUCH: (missing) → n
- CONFIG_INPUT_TOUCHSCREEN_TCLMV2: (missing) → n
- CONFIG_ION_RBIN_HEAP: (missing) → y
- CONFIG_KNOX_NCM: (missing) → n
- CONFIG_LEDS_CLASS_MULTICOLOR: (missing) → n
- CONFIG_LEDS_SM5714: (missing) → n
- CONFIG_LIMIT_CHARGING_DURING_CALL: (missing) → n
- CONFIG_LPS22HH_FACTORY: (missing) → n
- CONFIG_LSM6DSL_FACTORY: (missing) → n
- CONFIG_LSM6DSO_FACTORY: (missing) → n
- CONFIG_MAKE_NODE_USING_PLATFORM_DEVICE: (missing) → n
- CONFIG_MEMBLOCK_MEMSIZE: (missing) → y
- CONFIG_MEMCG_FORCE_USE_VM_SWAPPINESS: (missing) → y
- CONFIG_MEMCG_HEIMDALL: (missing) → y
- CONFIG_MFD_SM5714: (missing) → n
- CONFIG_MITIGATE_SPECTRE_BRANCH_HISTORY: (missing) → y
- CONFIG_MMAP_READAROUND_LIMIT: (missing) → 0
- CONFIG_MMC5603X_FACTORY: (missing) → n
- CONFIG_MMC_SUPPORT_STLOG: (missing) → y
- CONFIG_MQ_IOSCHED_SSG: (missing) → n
- CONFIG_NET_ANALYTICS: (missing) → y
- CONFIG_NFC_FEATURE_SN100U: (missing) → n
- CONFIG_NFC_P61: (missing) → n
- CONFIG_NFC_PN547: (missing) → n
- CONFIG_NFC_PVDD_LATE_ENABLE: (missing) → n
- CONFIG_NVME_TCP: (missing) → n
- CONFIG_PAGE_BOOST: (missing) → y
- CONFIG_PAGE_BOOST_RECORDING: (missing) → y
- CONFIG_PDIC_NOTIFIER: (missing) → n
- CONFIG_PDIC_POLICY: (missing) → n
- CONFIG_PDIC_SM5714: (missing) → n
- CONFIG_PREVENT_USB_CONN_OVERHEAT: (missing) → n
- CONFIG_PROC_AVC: (missing) → n
- CONFIG_PROC_DLOG: (missing) → y
- CONFIG_PROC_FSLOG: (missing) → y
- CONFIG_PROC_STLOG: (missing) → y
- CONFIG_PROFILE_ALL_BRANCHES: (missing) → n
- CONFIG_PSTORE_PMSG_SSPLOG: (missing) → n
- CONFIG_QRTR_WS_DEBUG: (missing) → n
- CONFIG_QTI_DEVFREQ_VDD_COOLING_DEVICE: (missing) → n
- CONFIG_QTI_TZ_LOG: (missing) → n
- CONFIG_R8168: (missing) → n
- CONFIG_RBIN: (missing) → y
- CONFIG_REDRIVER: (missing) → n
- CONFIG_REGULATOR_S2MPB03: (missing) → n
- CONFIG_RELR: (missing) → y
- CONFIG_RTC_AUTO_PWRON: (missing) → n
- CONFIG_SAMSUNG_ACTUATOR_PREVENT_SHAKING: (missing) → n
- ... 207 additional changes in JSON report


## Resolved to final details

### changed: 0

### removed: 0

### added: 0

