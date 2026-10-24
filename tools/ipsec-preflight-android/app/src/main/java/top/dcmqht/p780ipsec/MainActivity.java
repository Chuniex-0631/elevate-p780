package top.dcmqht.p780ipsec;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.net.IpSecAlgorithm;
import android.net.IpSecManager;
import android.net.IpSecTransform;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.net.InetAddress;
import java.security.SecureRandom;
import java.util.Arrays;

/**
 * Resource-level compatibility check, NOT a vulnerability exploit or test.
 * Never applies a transform to a socket, sends a packet, or loads a module.
 */
public final class MainActivity extends Activity {
    private static final byte[] TEST_REMOTE = {(byte) 198, 51, 100, 1};
    private static final byte[] TEST_LOCAL = {127, 0, 0, 1};

    private Button inspectButton;
    private Button resourceButton;
    private TextView outputView;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(28, 24, 28, 20);

        TextView title = new TextView(this);
        title.setText("P780 / Android 11 IPsec Preflight");
        title.setTextSize(19);
        root.addView(title);

        TextView warning = new TextView(this);
        warning.setText("只检测普通应用 IPsec API。不会发送 ESP/UDP 数据包、应用 Transform、修改文件或尝试 DirtyFrag。\n资源测试会短暂创建内核 IPsec 状态，并在结束后释放。");
        warning.setPadding(0, 12, 0, 12);
        root.addView(warning);

        inspectButton = new Button(this);
        inspectButton.setText("1. 只读环境检查");
        inspectButton.setOnClickListener(v -> execute(false));
        root.addView(inspectButton);

        resourceButton = new Button(this);
        resourceButton.setText("2. 临时 IPsec 资源检查（不发包）");
        resourceButton.setOnClickListener(v -> execute(true));
        root.addView(resourceButton);

        Button copyButton = new Button(this);
        copyButton.setText("复制当前结果");
        copyButton.setOnClickListener(v -> {
            ClipboardManager clipboard = getSystemService(ClipboardManager.class);
            if (clipboard != null) {
                clipboard.setPrimaryClip(ClipData.newPlainText("P780 IPsec preflight",
                        outputView.getText()));
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

    private void execute(boolean allocateResources) {
        inspectButton.setEnabled(false);
        resourceButton.setEnabled(false);
        outputView.setText("检查中……");
        new Thread(() -> {
            String result;
            try {
                result = allocateResources ? resourceProbe() : readOnlyProbe();
            } catch (Exception e) {
                result = "Unexpected probe error: " + describe(e);
            }
            final String complete = result;
            runOnUiThread(() -> {
                outputView.setText(complete);
                inspectButton.setEnabled(true);
                resourceButton.setEnabled(true);
            });
        }, "p780-ipsec-preflight").start();
    }

    private String readOnlyProbe() {
        StringBuilder report = new StringBuilder();
        report.append("P780 IPsec preflight 0.1.0\n");
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

    private static String describe(Exception e) {
        String message = e.getMessage();
        return e.getClass().getSimpleName()
                + (message == null ? "" : ": " + message);
    }
}
