# P780 2026-10-10 实机模块观察（按原文件保留名称）

来源：先前保存的 `P780-module-inventory.txt`（UTF-16）中 `=== Loaded kernel modules ===` 部分。此处仅列出已成功恢复的模块**名称**；故意不推断所有 `.ko` 文件均可读取，也没有复制内核地址、大小或运行时系统数据。

- `rmnet_offload`
- `rmnet_shs`
- `native_dlkm`
- `wlan`
- `camera`
- `platform_dlkm`
- `aw882xx_dlkm`
- `machine_dlkm`
- `rdbg`
- `hall_sensor`
- `rx_macro_dlkm`
- `goodix_tp`
- `gf_fp`
- `bt_fm_slim`
- `abov_sar`
- `adsp_loader_dlkm`
- `wcd938x_slave_dlkm`
- `stub_dlkm`
- `pinctrl_lpi_dlkm`
- `wcd937x_slave_dlkm`
- `st54jnfc`
- `wcd937x_dlkm`
- `wcd938x_dlkm`
- `va_macro_dlkm`
- `mbhc_dlkm`
- `sar_aw9610x`
- `btpower`
- `usb_switch`
- `wcd9xxx_dlkm`
- `synaptics_tcm`
- `rmnet_core`
- `tinno_gesture`
- `wsa881x_analog_dlkm`
- `rmnet_ctl`
- `tx_macro_dlkm`
- `swr_ctrl_dlkm`
- `wcd_core_dlkm`
- `bolero_cdc_dlkm`
- `q6_dlkm`
- `apr_dlkm`
- `q6_notifier_dlkm`
- `q6_pdr_dlkm`
- `snd_event_dlkm`
- `swr_dlkm`

可列出模块文件名不等于 shell 可以读取模块内容。原始保留日志中的 `modules.load`、`tinno_gesture.ko` 访问返回 `Permission denied`，且 SELinux Enforcing。
