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
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.Arrays;

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

    private Button inspectButton;
    private Button resourceButton;
    private Button loopbackButton;
    private Button fileBackedUdpButton;
    private TextView outputView;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(28, 24, 28, 20);

        TextView title = new TextView(this);
        title.setText("P780 / Android 11 IPsec Diagnostics");
        title.setTextSize(19);
        root.addView(title);

        TextView warning = new TextView(this);
        warning.setText("仅使用普通应用权限。第 3 项向 127.0.0.1 各发送 1 个普通 UDP 与受 IPsec 保护的数据报。第 4 项从应用私有临时文件向本机 UDP socket 调用一次 sendfile，不启用 IPsec。\n"
                + "不访问外网，不构造原始/畸形/分片 ESP，不修改系统文件或页面缓存，不尝试 DirtyFrag/Root。");
        warning.setPadding(0, 12, 0, 12);
        root.addView(warning);

        inspectButton = new Button(this);
        inspectButton.setText("1. 只读环境检查");
        inspectButton.setOnClickListener(v -> execute(Probe.READ_ONLY));
        root.addView(inspectButton);

        resourceButton = new Button(this);
        resourceButton.setText("2. 临时 IPsec 资源检查（不发包）");
        resourceButton.setOnClickListener(v -> execute(Probe.RESOURCES));
        root.addView(resourceButton);

        loopbackButton = new Button(this);
        loopbackButton.setText("3. 普通 UDP/ESP 回环诊断（本机，各 1 包）");
        loopbackButton.setOnClickListener(v -> execute(Probe.LOOPBACK));
        root.addView(loopbackButton);

        fileBackedUdpButton = new Button(this);
        fileBackedUdpButton.setText("4. 文件支持 UDP sendfile 回环（纯 UDP）");
        fileBackedUdpButton.setOnClickListener(v -> execute(Probe.FILEBACKED_UDP));
        root.addView(fileBackedUdpButton);

        Button copyButton = new Button(this);
        copyButton.setText("复制当前结果");
        copyButton.setOnClickListener(v -> {
            ClipboardManager clipboard = getSystemService(ClipboardManager.class);
            if (clipboard != null) {
                clipboard.setPrimaryClip(ClipData.newPlainText(
                        "P780 IPsec diagnostics", outputView.getText()));
            }
        });
        root.addView(copyButton);

        outputView = new TextView(this);
        outputView.setText("尚未运行。先点“只读环境检查”。");
        outputView.setTextIsSelectable(true);
        outputView.setPadding(0, 16, 0, 0);

        ScrollView scroll = new ScrollView(this);
        scroll.addView(outputView);
        root.addView(scroll, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));
        setContentView(root);
    }

    private enum Probe {
        READ_ONLY,
        RESOURCES,
        LOOPBACK,
        FILEBACKED_UDP
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
                } else {
                    result = readOnlyProbe();
                }
            } catch (Exception e) {
                result = "Unexpected probe error: " + describe(e);
            }
            final String complete = result;
            runOnUiThread(() -> {
                outputView.setText(complete);
                setProbeButtonsEnabled(true);
            });
        }, "p780-ipsec-diagnostics").start();
    }

    private void setProbeButtonsEnabled(boolean enabled) {
        inspectButton.setEnabled(enabled);
        resourceButton.setEnabled(enabled);
        loopbackButton.setEnabled(enabled);
        fileBackedUdpButton.setEnabled(enabled);
    }

    private String readOnlyProbe() {
        StringBuilder report = new StringBuilder();
        report.append("P780 IPsec / UDP diagnostics 0.3.0\n");
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
        report.append("\nNO resource allocation; NO traffic.\n");
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

    private native String runFileBackedUdpProbe(String cacheDirPath);

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

