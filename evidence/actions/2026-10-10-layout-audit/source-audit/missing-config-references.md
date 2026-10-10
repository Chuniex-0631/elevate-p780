# Removed symbols: actual source references

Source-level inventory only. A missing Kconfig symbol does not prove missing functionality.

| Symbol | Device | TINNO references | Candidate references |
|---|---|---:|---:|
| CONFIG_ABOV_SAR | y | 2 | 0 |
| CONFIG_AW9610X_SAR | y | 0 | 0 |
| CONFIG_BATTERY_PROTECT_LIMIT | n | 0 | 0 |
| CONFIG_EXFAT_FS | n | 3 | 0 |
| CONFIG_F2FS_CHECK_FS | n | 31 | 30 |
| CONFIG_FINGERPRINT_FOCAL_FT9801_QSEE | n | 4 | 0 |
| CONFIG_FINGERPRINT_GOODIX_GF9628_QSEE | y | 2 | 0 |
| CONFIG_FORTIFY_SOURCE | y | 10 | 10 |
| CONFIG_INPUT_FINGERPRINT | y | 2 | 0 |
| CONFIG_IPA_ETH | n | 3 | 2 |
| CONFIG_JEITA_WARM_OV_PROTECT | y | 0 | 0 |
| CONFIG_LOWBATT_PWROFF | y | 5 | 0 |
| CONFIG_NFC_PN533_I2C | n | 2 | 2 |
| CONFIG_NFC_PN533_USB | n | 2 | 2 |
| CONFIG_NFC_QTI_I3C_GPIO | n | 2 | 1 |
| CONFIG_NFC_ST54J | m | 4 | 0 |
| CONFIG_NVM | n | 10 | 10 |
| CONFIG_REFCOUNT_FULL | y | 7 | 2 |
| CONFIG_SCC_SUPPORT | y | 9 | 0 |
| CONFIG_TINNO_DEMOMODECHG_CONTROL | y | 9 | 0 |
| CONFIG_TINNO_LONGCHG_CONTROL | y | 0 | 0 |
| CONFIG_TINNO_PRODUCT_INFO | y | 16 | 0 |
| CONFIG_TINNO_WARM_RECHARGE_CONTROL | y | 0 | 0 |
| CONFIG_USB_SWITCH | y | 4 | 0 |

## CONFIG_ABOV_SAR

### tinno
- `drivers/misc/Makefile:72` — `obj-$(CONFIG_ABOV_SAR)		+= abov/`
- `drivers/misc/abov/Kconfig:1` — `config ABOV_SAR`

### candidate
- No references in scanned C/H/S/Kconfig/Makefile files.

## CONFIG_AW9610X_SAR

### tinno
- No references in scanned C/H/S/Kconfig/Makefile files.

### candidate
- No references in scanned C/H/S/Kconfig/Makefile files.

## CONFIG_BATTERY_PROTECT_LIMIT

### tinno
- No references in scanned C/H/S/Kconfig/Makefile files.

### candidate
- No references in scanned C/H/S/Kconfig/Makefile files.

## CONFIG_EXFAT_FS

### tinno
- `fs/Makefile:87` — `obj-$(CONFIG_EXFAT_FS)		+= exfat/`
- `fs/exfat/Kconfig:3` — `config EXFAT_FS`
- `fs/exfat/Makefile:5` — `obj-$(CONFIG_EXFAT_FS) += exfat.o`

### candidate
- No references in scanned C/H/S/Kconfig/Makefile files.

## CONFIG_F2FS_CHECK_FS

### tinno
- `fs/f2fs/Kconfig:71` — `config F2FS_CHECK_FS`
- `fs/f2fs/extent_cache.c:171` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/f2fs.h:31` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/f2fs.h:939` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/gc.c:393` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/gc.c:649` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/inode.c:170` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/inode.c:642` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/node.c:1229` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/node.c:2080` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/node.c:3120` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/node.c:3256` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/node.h:188` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/node.h:234` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/node.h:453` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:820` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:1047` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:2133` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:2154` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:2184` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:3937` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:4025` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:4043` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:4076` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:4832` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.h:183` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.h:219` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.h:349` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.h:481` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.h:719` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.h:750` — `#ifdef CONFIG_F2FS_CHECK_FS`

### candidate
- `fs/f2fs/Kconfig:71` — `config F2FS_CHECK_FS`
- `fs/f2fs/extent_cache.c:171` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/f2fs.h:973` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/gc.c:393` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/gc.c:672` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/inode.c:173` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/inode.c:660` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/node.c:1281` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/node.c:2187` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/node.c:3264` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/node.c:3400` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/node.h:189` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/node.h:235` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/node.h:454` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:838` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:1066` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:2161` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:2182` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:2212` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:4043` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:4131` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:4149` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:4182` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.c:4958` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.h:184` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.h:220` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.h:353` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.h:485` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.h:732` — `#ifdef CONFIG_F2FS_CHECK_FS`
- `fs/f2fs/segment.h:763` — `#ifdef CONFIG_F2FS_CHECK_FS`

## CONFIG_FINGERPRINT_FOCAL_FT9801_QSEE

### tinno
- `drivers/input/fingerprint/Kconfig:17` — `config FINGERPRINT_FOCAL_FT9801_QSEE`
- `drivers/input/fingerprint/Makefile:9` — `obj-$(CONFIG_FINGERPRINT_FOCAL_FT9801_QSEE)	+= focal_FT9801/`
- `drivers/input/fingerprint/focal_FT9801/Makefile:46` — `obj-$(CONFIG_FINGERPRINT_FOCAL_FT9801_QSEE) := focaltech_fp.o`
- `drivers/input/fingerprint/focal_FT9801/Makefile:111` — `make -C $(KBUILDDIR) ARCH=$(ARCH) CROSS_COMPILE=$(CROSS_COMPILE) M=$(MODULEPWD) CONFIG_FINGERPRINT_FOCAL_FT9801_QSEE=m modules`

### candidate
- No references in scanned C/H/S/Kconfig/Makefile files.

## CONFIG_FINGERPRINT_GOODIX_GF9628_QSEE

### tinno
- `drivers/input/fingerprint/Kconfig:11` — `config FINGERPRINT_GOODIX_GF9628_QSEE`
- `drivers/input/fingerprint/Makefile:7` — `obj-$(CONFIG_FINGERPRINT_GOODIX_GF9628_QSEE)	+= goodix_GF9628/`

### candidate
- No references in scanned C/H/S/Kconfig/Makefile files.

## CONFIG_FORTIFY_SOURCE

### tinno
- `arch/Kconfig:233` — `build and run with CONFIG_FORTIFY_SOURCE.`
- `arch/s390/include/asm/string.h:105` — `#if !defined(IN_ARCH_STRING_C) && (!defined(CONFIG_FORTIFY_SOURCE) || defined(__NO_FORTIFY))`
- `arch/x86/include/asm/string_32.h:148` — `#ifndef CONFIG_FORTIFY_SOURCE`
- `arch/x86/include/asm/string_32.h:185` — `#endif /* !CONFIG_FORTIFY_SOURCE */`
- `arch/x86/include/asm/string_32.h:191` — `#ifndef CONFIG_FORTIFY_SOURCE`
- `arch/x86/include/asm/string_32.h:227` — `#ifndef CONFIG_FORTIFY_SOURCE`
- `arch/x86/include/asm/string_32.h:229` — `#endif /* !CONFIG_FORTIFY_SOURCE */`
- `arch/x86/lib/memcpy_32.c:10` — `#if defined(CONFIG_X86_USE_3DNOW) && !defined(CONFIG_FORTIFY_SOURCE)`
- `include/linux/string.h:273` — `#if !defined(__NO_FORTIFY) && defined(__OPTIMIZE__) && defined(CONFIG_FORTIFY_SOURCE)`
- `security/Kconfig:191` — `config FORTIFY_SOURCE`

### candidate
- `arch/Kconfig:249` — `build and run with CONFIG_FORTIFY_SOURCE.`
- `arch/s390/include/asm/string.h:105` — `#if !defined(IN_ARCH_STRING_C) && (!defined(CONFIG_FORTIFY_SOURCE) || defined(__NO_FORTIFY))`
- `arch/x86/include/asm/string_32.h:148` — `#ifndef CONFIG_FORTIFY_SOURCE`
- `arch/x86/include/asm/string_32.h:185` — `#endif /* !CONFIG_FORTIFY_SOURCE */`
- `arch/x86/include/asm/string_32.h:191` — `#ifndef CONFIG_FORTIFY_SOURCE`
- `arch/x86/include/asm/string_32.h:227` — `#ifndef CONFIG_FORTIFY_SOURCE`
- `arch/x86/include/asm/string_32.h:229` — `#endif /* !CONFIG_FORTIFY_SOURCE */`
- `arch/x86/lib/memcpy_32.c:10` — `#if defined(CONFIG_X86_USE_3DNOW) && !defined(CONFIG_FORTIFY_SOURCE)`
- `include/linux/string.h:273` — `#if !defined(__NO_FORTIFY) && defined(__OPTIMIZE__) && defined(CONFIG_FORTIFY_SOURCE)`
- `security/Kconfig:191` — `config FORTIFY_SOURCE`

## CONFIG_INPUT_FINGERPRINT

### tinno
- `drivers/input/Makefile:30` — `obj-$(CONFIG_INPUT_FINGERPRINT) += fingerprint/`
- `drivers/input/fingerprint/Kconfig:5` — `config INPUT_FINGERPRINT`

### candidate
- No references in scanned C/H/S/Kconfig/Makefile files.

## CONFIG_IPA_ETH

### tinno
- `drivers/platform/msm/Kconfig:198` — `config IPA_ETH`
- `drivers/platform/msm/Makefile:16` — `obj-$(CONFIG_IPA_ETH) += ethernet/`
- `drivers/platform/msm/ethernet/Makefile:7` — `obj-$(CONFIG_IPA_ETH) += ipa-eth.o`

### candidate
- `techpack/dataipa/drivers/platform/msm/ipa/ipa_v3/ipa_i.h:3164` — `#ifdef CONFIG_IPA_ETH`
- `techpack/dataipa/drivers/platform/msm/ipa/ipa_v3/ipa_i.h:3170` — `#endif // CONFIG_IPA_ETH`

## CONFIG_JEITA_WARM_OV_PROTECT

### tinno
- No references in scanned C/H/S/Kconfig/Makefile files.

### candidate
- No references in scanned C/H/S/Kconfig/Makefile files.

## CONFIG_LOWBATT_PWROFF

### tinno
- `drivers/power/reset/msm-poweroff.c:531` — `#ifdef CONFIG_LOWBATT_PWROFF`
- `drivers/power/supply/qcom/Kconfig:105` — `config LOWBATT_PWROFF`
- `drivers/power/supply/qcom/qpnp-qg.c:51` — `#ifdef CONFIG_LOWBATT_PWROFF`
- `drivers/power/supply/qcom/qpnp-qg.c:1480` — `#ifdef CONFIG_LOWBATT_PWROFF`
- `drivers/power/supply/qcom/qpnp-qg.c:1560` — `#ifdef CONFIG_LOWBATT_PWROFF`

### candidate
- No references in scanned C/H/S/Kconfig/Makefile files.

## CONFIG_NFC_PN533_I2C

### tinno
- `drivers/nfc/pn533/Kconfig:19` — `config NFC_PN533_I2C`
- `drivers/nfc/pn533/Makefile:10` — `obj-$(CONFIG_NFC_PN533_I2C) += pn533_i2c.o`

### candidate
- `drivers/nfc/pn533/Kconfig:19` — `config NFC_PN533_I2C`
- `drivers/nfc/pn533/Makefile:10` — `obj-$(CONFIG_NFC_PN533_I2C) += pn533_i2c.o`

## CONFIG_NFC_PN533_USB

### tinno
- `drivers/nfc/pn533/Kconfig:8` — `config NFC_PN533_USB`
- `drivers/nfc/pn533/Makefile:9` — `obj-$(CONFIG_NFC_PN533_USB) += pn533_usb.o`

### candidate
- `drivers/nfc/pn533/Kconfig:8` — `config NFC_PN533_USB`
- `drivers/nfc/pn533/Makefile:9` — `obj-$(CONFIG_NFC_PN533_USB) += pn533_usb.o`

## CONFIG_NFC_QTI_I3C_GPIO

### tinno
- `drivers/nfc/Kconfig:77` — `config NFC_QTI_I3C_GPIO`
- `drivers/nfc/qti/Makefile:12` — `obj-$(CONFIG_NFC_QTI_I3C_GPIO)	+= nfc_i3c_gpio_cfg.o`

### candidate
- `drivers/nfc/qti/Makefile:12` — `obj-$(CONFIG_NFC_QTI_I3C_GPIO)	+= nfc_i3c_gpio_cfg.o`

## CONFIG_NFC_ST54J

### tinno
- `drivers/nfc/Makefile:21` — `obj-$(CONFIG_NFC_ST54J)	+= st54j/`
- `drivers/nfc/st54j/Kconfig:1` — `config NFC_ST54J`
- `drivers/nfc/st54j/Makefile:14` — `obj-$(CONFIG_NFC_ST54J) += st21nfc/`
- `drivers/nfc/st54j/st21nfc/Makefile:5` — `obj-$(CONFIG_NFC_ST54J) +=st21nfc.o`

### candidate
- No references in scanned C/H/S/Kconfig/Makefile files.

## CONFIG_NVM

### tinno
- `drivers/Makefile:71` — `obj-$(CONFIG_NVM)		+= lightnvm/`
- `drivers/lightnvm/Kconfig:6` — `menuconfig NVM`
- `drivers/lightnvm/Makefile:6` — `obj-$(CONFIG_NVM)		:= core.o`
- `drivers/nvme/host/Makefile:15` — `nvme-core-$(CONFIG_NVM)			+= lightnvm.o`
- `drivers/nvme/host/core.c:3163` — `#ifdef CONFIG_NVM`
- `drivers/nvme/host/nvme.h:639` — `#ifdef CONFIG_NVM`
- `drivers/nvme/host/nvme.h:657` — `#endif /* CONFIG_NVM */`
- `include/linux/lightnvm.h:113` — `#ifdef CONFIG_NVM`
- `include/linux/lightnvm.h:687` — `#else /* CONFIG_NVM */`
- `include/linux/lightnvm.h:699` — `#endif /* CONFIG_NVM */`

### candidate
- `drivers/Makefile:73` — `obj-$(CONFIG_NVM)		+= lightnvm/`
- `drivers/lightnvm/Kconfig:6` — `menuconfig NVM`
- `drivers/lightnvm/Makefile:6` — `obj-$(CONFIG_NVM)		:= core.o`
- `drivers/nvme/host/Makefile:15` — `nvme-core-$(CONFIG_NVM)			+= lightnvm.o`
- `drivers/nvme/host/core.c:3210` — `#ifdef CONFIG_NVM`
- `drivers/nvme/host/nvme.h:686` — `#ifdef CONFIG_NVM`
- `drivers/nvme/host/nvme.h:704` — `#endif /* CONFIG_NVM */`
- `include/linux/lightnvm.h:113` — `#ifdef CONFIG_NVM`
- `include/linux/lightnvm.h:687` — `#else /* CONFIG_NVM */`
- `include/linux/lightnvm.h:699` — `#endif /* CONFIG_NVM */`

## CONFIG_REFCOUNT_FULL

### tinno
- `arch/Kconfig:1007` — `refcount state checks of CONFIG_REFCOUNT_FULL=y.`
- `arch/Kconfig:1013` — `config REFCOUNT_FULL`
- `drivers/misc/lkdtm/refcount.c:9` — `#ifdef CONFIG_REFCOUNT_FULL`
- `drivers/misc/lkdtm/refcount.c:130` — `* CONFIG_REFCOUNT_FULL refuses to move a refcount at all on an`
- `drivers/misc/lkdtm/refcount.c:213` — `* Only CONFIG_REFCOUNT_FULL provides this protection currently.`
- `include/linux/refcount.h:57` — `#ifdef CONFIG_REFCOUNT_FULL`
- `include/linux/refcount.h:109` — `#endif /* CONFIG_REFCOUNT_FULL */`

### candidate
- `drivers/misc/lkdtm/refcount.c:122` — `* CONFIG_REFCOUNT_FULL refuses to move a refcount at all on an`
- `drivers/misc/lkdtm/refcount.c:205` — `* Only CONFIG_REFCOUNT_FULL provides this protection currently.`

## CONFIG_SCC_SUPPORT

### tinno
- `drivers/power/supply/qcom/Kconfig:111` — `config SCC_SUPPORT`
- `drivers/power/supply/qcom/qpnp-smb5.c:421` — `#ifdef CONFIG_SCC_SUPPORT`
- `drivers/power/supply/qcom/qpnp-smb5.c:498` — `#ifdef CONFIG_SCC_SUPPORT`
- `drivers/power/supply/qcom/qpnp-smb5.c:567` — `#ifdef CONFIG_SCC_SUPPORT`
- `drivers/power/supply/qcom/qpnp-smb5.c:1133` — `#ifdef CONFIG_SCC_SUPPORT`
- `drivers/power/supply/qcom/smb5-lib.c:2505` — `#ifdef CONFIG_SCC_SUPPORT`
- `drivers/power/supply/qcom/smb5-lib.h:47` — `#ifdef CONFIG_SCC_SUPPORT`
- `drivers/power/supply/qcom/smb5-lib.h:527` — `#ifdef CONFIG_SCC_SUPPORT`
- `drivers/power/supply/qcom/smb5-lib.h:735` — `#ifdef CONFIG_SCC_SUPPORT`

### candidate
- No references in scanned C/H/S/Kconfig/Makefile files.

## CONFIG_TINNO_DEMOMODECHG_CONTROL

### tinno
- `drivers/power/supply/qcom/Kconfig:117` — `config TINNO_DEMOMODECHG_CONTROL`
- `drivers/power/supply/qcom/qpnp-smb5.c:32` — `#ifdef CONFIG_TINNO_DEMOMODECHG_CONTROL`
- `drivers/power/supply/qcom/qpnp-smb5.c:923` — `#ifdef CONFIG_TINNO_DEMOMODECHG_CONTROL`
- `drivers/power/supply/qcom/qpnp-smb5.c:1537` — `#ifdef CONFIG_TINNO_DEMOMODECHG_CONTROL`
- `drivers/power/supply/qcom/qpnp-smb5.c:3521` — `#ifdef CONFIG_TINNO_DEMOMODECHG_CONTROL`
- `drivers/power/supply/qcom/smb5-lib.c:1192` — `#ifdef CONFIG_TINNO_DEMOMODECHG_CONTROL`
- `drivers/power/supply/qcom/smb5-lib.c:1211` — `#ifdef CONFIG_TINNO_DEMOMODECHG_CONTROL`
- `drivers/power/supply/qcom/smb5-lib.h:43` — `#ifdef CONFIG_TINNO_DEMOMODECHG_CONTROL`
- `drivers/power/supply/qcom/smb5-lib.h:651` — `#ifdef CONFIG_TINNO_DEMOMODECHG_CONTROL`

### candidate
- No references in scanned C/H/S/Kconfig/Makefile files.

## CONFIG_TINNO_LONGCHG_CONTROL

### tinno
- No references in scanned C/H/S/Kconfig/Makefile files.

### candidate
- No references in scanned C/H/S/Kconfig/Makefile files.

## CONFIG_TINNO_PRODUCT_INFO

### tinno
- `drivers/input/touchscreen/Makefile:122` — `subdir-ccflags-$(CONFIG_TINNO_PRODUCT_INFO) += -I$(srctree)/tinno/common_features/`
- `drivers/input/touchscreen/goodix/goodix_ts_i2c.c:653` — `#ifdef CONFIG_TINNO_PRODUCT_INFO`
- `drivers/input/touchscreen/goodix/goodix_ts_i2c.c:787` — `#ifdef CONFIG_TINNO_PRODUCT_INFO`
- `drivers/mmc/core/Makefile:5` — `subdir-ccflags-$(CONFIG_TINNO_PRODUCT_INFO) += -I$(srctree)/tinno/common_features/dev_info`
- `drivers/mmc/core/mmc.c:29` — `#ifdef CONFIG_TINNO_PRODUCT_INFO  //yajun.wang`
- `drivers/mmc/core/mmc.c:2087` — `#ifdef CONFIG_TINNO_PRODUCT_INFO         //yajun.wang`
- `drivers/power/supply/qcom/Makefile:18` — `subdir-ccflags-$(CONFIG_TINNO_PRODUCT_INFO) += -I$(srctree)/tinno/common_features/dev_info`
- `drivers/power/supply/qcom/qpnp-qg.c:1230` — `#ifdef CONFIG_TINNO_PRODUCT_INFO`
- `drivers/power/supply/qcom/qpnp-qg.c:1250` — `#ifdef CONFIG_TINNO_PRODUCT_INFO`
- `drivers/power/supply/qcom/qpnp-qg.c:1279` — `#ifdef CONFIG_TINNO_PRODUCT_INFO`
- `tinno/common_features/Kconfig:1` — `config TINNO_PRODUCT_INFO`
- `tinno/common_features/Makefile:3` — `obj-$(CONFIG_TINNO_PRODUCT_INFO)    += dev_info/`
- `tinno/common_features/dev_info/dev_info.c:23` — `#ifdef CONFIG_TINNO_PRODUCT_INFO`
- `tinno/common_features/dev_info/dev_info.h:25` — `#ifdef CONFIG_TINNO_PRODUCT_INFO`
- `tinno/common_features/dev_info/external.c:3` — `#ifdef CONFIG_TINNO_PRODUCT_INFO`
- `tinno/common_features/dev_info/external.h:25` — `#ifdef CONFIG_TINNO_PRODUCT_INFO`

### candidate
- No references in scanned C/H/S/Kconfig/Makefile files.

## CONFIG_TINNO_WARM_RECHARGE_CONTROL

### tinno
- No references in scanned C/H/S/Kconfig/Makefile files.

### candidate
- No references in scanned C/H/S/Kconfig/Makefile files.

## CONFIG_USB_SWITCH

### tinno
- `drivers/misc/Makefile:69` — `obj-$(CONFIG_USB_SWITCH) += usb_switch/`
- `drivers/misc/usb_switch/Kconfig:1` — `config USB_SWITCH`
- `drivers/misc/usb_switch/Makefile:2` — `obj-$(CONFIG_USB_SWITCH)	+= usb_switch.o`
- `include/linux/soc/qcom/usb_switch_core.h:42` — `#ifdef CONFIG_USB_SWITCH`

### candidate
- No references in scanned C/H/S/Kconfig/Makefile files.
