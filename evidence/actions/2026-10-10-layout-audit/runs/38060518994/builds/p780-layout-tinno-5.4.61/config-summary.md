# P780 kernel config audit

Research-only cross-device build; do NOT flash this output to the device.

- Original parsed symbols: **5238**
- Resolved parsed symbols: **5206**
- Final parsed symbols: **5206**
- olddefconfig: **0 changed, 14 added, 46 removed**
- Compilation-stage drift: **0 changed, 0 added, 0 removed**
- Overall original to final: **0 changed, 14 added, 46 removed**

## Security and platform-critical symbols

| Symbol | Device original | After olddefconfig | After compile |
|---|---|---|---|
| CONFIG_ARCH_HOLI | y | y | y |
| CONFIG_ARCH_BLAIR | y | (missing) | (missing) |
| CONFIG_FUTEX_PI | y | y | y |
| CONFIG_RT_MUTEXES | y | y | y |
| CONFIG_LTO_CLANG | y | y | y |
| CONFIG_CFI_CLANG | y | y | y |
| CONFIG_MODVERSIONS | y | y | y |
| CONFIG_KALLSYMS | y | y | y |
| CONFIG_IKHEADERS | y | y | y |
| CONFIG_CC_VERSION_TEXT | "Android (6877366 based on r383902b1) clang version 11.0.2 (https://android.googlesource.com/toolchain/llvm-project b397f81060ce6d701042b782172ed13bee898b79)" | "Android (6877366 based on r383902b1) clang version 11.0.2 (https://android.googlesource.com/toolchain/llvm-project b397f81060ce6d701042b782172ed13bee898b79)" | "Android (6877366 based on r383902b1) clang version 11.0.2 (https://android.googlesource.com/toolchain/llvm-project b397f81060ce6d701042b782172ed13bee898b79)" |
| CONFIG_LOCALVERSION | "-qgki" | "-qgki" | "-qgki" |
| CONFIG_PREEMPT | y | y | y |
| CONFIG_KASLR | (missing) | (missing) | (missing) |

## Original to resolved details

### changed: 0

### removed: 46
- CONFIG_ARCH_BLAIR: y → (missing)
- CONFIG_ARCH_SA2150P: n → (missing)
- CONFIG_ARCH_SCUBA: n → (missing)
- CONFIG_AW9610X_SAR: y → (missing)
- CONFIG_BATTERY_PROTECT_LIMIT: n → (missing)
- CONFIG_DUMP_XBL_LOG: n → (missing)
- CONFIG_GNSS_SIRF: n → (missing)
- CONFIG_HID_AKSYS_QRD: n → (missing)
- CONFIG_HID_PLAYSTATION: y → (missing)
- CONFIG_INTERCONNECT_QCOM_DIREWOLF: n → (missing)
- CONFIG_IP_NF_TARGET_TRIGGER_MODULE: n → (missing)
- CONFIG_JEITA_WARM_OV_PROTECT: y → (missing)
- CONFIG_LEDS_AW2016: n → (missing)
- CONFIG_MSM_L2_SPM: n → (missing)
- CONFIG_MSM_PM_LEGACY: n → (missing)
- CONFIG_MSM_SEB: n → (missing)
- CONFIG_MSM_SPM: n → (missing)
- CONFIG_PINCTRL_BLAIR: y → (missing)
- CONFIG_PLAYSTATION_FF: y → (missing)
- CONFIG_PROFILER: n → (missing)
- CONFIG_QCOM_AOP_SET_DDR: n → (missing)
- CONFIG_QCOM_CX_IPEAK: y → (missing)
- CONFIG_QCOM_KGSL_QDSS_STM: n → (missing)
- CONFIG_QCOM_PCI_EDMA: n → (missing)
- CONFIG_QCOM_SPMI_ADC5_GEN3: n → (missing)
- CONFIG_QCOM_SYSMON_SUBSYSTEM_STATS: n → (missing)
- CONFIG_QCS_CMN_BLK_PLL: n → (missing)
- CONFIG_QGKI_MSM_BOOT_TIME_MARKER: n → (missing)
- CONFIG_QGKI_SHOW_S2IDLE_WAKE_IRQ: y → (missing)
- CONFIG_QTI_CRYPTO_FDE: n → (missing)
- CONFIG_QTI_CX_IPEAK_COOLING_DEVICE: y → (missing)
- CONFIG_QTI_LMH_CPU_VDD_COOLING_DEVICE: n → (missing)
- CONFIG_QTI_QBG: n → (missing)
- CONFIG_REGMAP_WCD_IRQ: n → (missing)
- CONFIG_REGULATOR_QPNP: n → (missing)
- CONFIG_RPMSG_QCOM_GLINK_SLATECOM: n → (missing)
- CONFIG_SA_DEBUGCC_DIREWOLF: n → (missing)
- CONFIG_SA_GCC_DIREWOLF: n → (missing)
- CONFIG_SDW_DEBUGCC_MONACO: n → (missing)
- CONFIG_SDW_GPUCC_MONACO: n → (missing)
- CONFIG_SM_DEBUGCC_BLAIR: y → (missing)
- CONFIG_SM_DISPCC_BLAIR: y → (missing)
- CONFIG_SM_GCC_BLAIR: y → (missing)
- CONFIG_SM_GPUCC_BLAIR: y → (missing)
- CONFIG_TINNO_LONGCHG_CONTROL: y → (missing)
- CONFIG_TINNO_WARM_RECHARGE_CONTROL: y → (missing)

### added: 14
- CONFIG_DM_VERITY_AVB: (missing) → n
- CONFIG_INPUT_HALL_SENSOR: (missing) → n
- CONFIG_MSM_BOOT_TIME_MARKER: (missing) → n
- CONFIG_NFC_ST54J_SPI: (missing) → m
- CONFIG_PGTABLE_MAPPING: (missing) → n
- CONFIG_PROJECT_P780: (missing) → n
- CONFIG_PROJECT_TINNO: (missing) → n
- CONFIG_QCOM_SCM_QCPE: (missing) → n
- CONFIG_R8125_IPA_OFFLOAD: (missing) → n
- CONFIG_RELR: (missing) → y
- CONFIG_TINNO_TP_GESTURE: (missing) → n
- CONFIG_TOOLS_SUPPORT_RELR: (missing) → y
- CONFIG_TOUCHSCREEN_GOODIX_GTX8: (missing) → n
- CONFIG_TOUCHSCREEN_SYNAPTICS_TCM_TOUCH: (missing) → n


## Resolved to final details

### changed: 0

### removed: 0

### added: 0

