package co.edu.uptc.swii.posts_service.config;

import java.time.Duration;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.CacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.RedisSerializationContext;

@Configuration
public class RedisCacheConfig {

    @Bean
    CacheManager cacheManager(
        RedisConnectionFactory connectionFactory,
        @Value("${cache.ttl.feed-latest-minutes:2}") long feedLatestMinutes,
        @Value("${cache.ttl.points-minutes:5}") long pointsMinutes
    ) {
        RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
            .serializeValuesWith(
                RedisSerializationContext.SerializationPair.fromSerializer(new GenericJackson2JsonRedisSerializer())
            )
            .disableCachingNullValues();

        Map<String, RedisCacheConfiguration> cacheConfigs = Map.of(
            CacheNames.FEED_LATEST, defaultConfig.entryTtl(Duration.ofMinutes(feedLatestMinutes)),
            CacheNames.USER_POINTS, defaultConfig.entryTtl(Duration.ofMinutes(pointsMinutes))
        );

        return RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(defaultConfig)
            .withInitialCacheConfigurations(cacheConfigs)
            .build();
    }
}
