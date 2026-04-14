package co.edu.uptc.swii.posts_service.util;

import java.nio.charset.StandardCharsets;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class HmacSigner {

    private final String internalSecret;

    public HmacSigner(@Value("${integration.internal.secret}") String internalSecret) {
        this.internalSecret = internalSecret;
    }

    public String sign(String serviceId, String timestamp, String method, String path) {
        try {
            String payload = serviceId + ":" + timestamp + ":" + method.toUpperCase() + ":" + path;
            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec keySpec = new SecretKeySpec(internalSecret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
            mac.init(keySpec);
            byte[] hash = mac.doFinal(payload.getBytes(StandardCharsets.UTF_8));
            StringBuilder builder = new StringBuilder(hash.length * 2);
            for (byte value : hash) {
                builder.append(String.format("%02x", value));
            }
            return builder.toString();
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to sign internal request", exception);
        }
    }
}
