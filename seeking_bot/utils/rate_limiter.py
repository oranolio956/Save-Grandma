"""
Rate Limiter Module - Intelligent request throttling and circuit breaking
Implements token bucket algorithm with adaptive rate limiting
"""

import time
import asyncio
from typing import Dict, Optional, Tuple, List, Any
from datetime import datetime, timedelta
from collections import deque, defaultdict
from enum import Enum
import threading
from dataclasses import dataclass, field
from loguru import logger
import json
import redis


class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    ADAPTIVE = "adaptive"


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    requests_per_second: float = 1.0
    requests_per_minute: int = 20
    requests_per_hour: int = 100
    requests_per_day: int = 500
    burst_size: int = 10
    cooldown_seconds: int = 30
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60


@dataclass
class CircuitBreakerState:
    """Circuit breaker state tracking"""
    failures: int = 0
    last_failure: Optional[datetime] = None
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    last_state_change: datetime = field(default_factory=datetime.now)


class RateLimiter:
    """
    Advanced rate limiter with multiple strategies and circuit breaker
    Prevents overwhelming target systems and detection
    """
    
    def __init__(self, 
                 messages_per_hour: int = 20,
                 messages_per_day: int = 100,
                 config: Optional[RateLimitConfig] = None,
                 redis_client: Optional[redis.Redis] = None):
        """
        Initialize rate limiter
        
        Args:
            messages_per_hour: Hourly message limit
            messages_per_day: Daily message limit
            config: Detailed configuration
            redis_client: Redis client for distributed rate limiting
        """
        self.messages_per_hour = messages_per_hour
        self.messages_per_day = messages_per_day
        self.config = config or RateLimitConfig()
        self.redis_client = redis_client
        
        # Token bucket implementation
        self.tokens = self.config.burst_size
        self.max_tokens = self.config.burst_size
        self.refill_rate = self.config.requests_per_second
        self.last_refill = time.time()
        
        # Sliding window tracking
        self.request_times = deque(maxlen=1000)
        self.endpoint_requests = defaultdict(deque)
        
        # Circuit breaker
        self.circuit_breakers = defaultdict(CircuitBreakerState)
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'allowed_requests': 0,
            'rejected_requests': 0,
            'circuit_breaker_trips': 0
        }
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        # Token refill task
        def refill_tokens():
            while True:
                time.sleep(1)
                with self.lock:
                    self._refill_tokens()
        
        # Circuit breaker reset task
        def reset_circuit_breakers():
            while True:
                time.sleep(10)
                self._check_circuit_breakers()
        
        # Start threads
        threading.Thread(target=refill_tokens, daemon=True).start()
        threading.Thread(target=reset_circuit_breakers, daemon=True).start()
    
    def _refill_tokens(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Add tokens based on refill rate
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def can_send_message(self, endpoint: str = "default") -> bool:
        """
        Check if a message can be sent
        
        Args:
            endpoint: Specific endpoint/action to check
            
        Returns:
            True if message allowed, False otherwise
        """
        with self.lock:
            self.stats['total_requests'] += 1
            
            # Check circuit breaker first
            if self.config.enable_circuit_breaker:
                if not self._check_circuit_breaker(endpoint):
                    self.stats['rejected_requests'] += 1
                    return False
            
            # Apply rate limiting based on strategy
            if self.config.strategy == RateLimitStrategy.TOKEN_BUCKET:
                allowed = self._check_token_bucket()
            elif self.config.strategy == RateLimitStrategy.SLIDING_WINDOW:
                allowed = self._check_sliding_window()
            elif self.config.strategy == RateLimitStrategy.FIXED_WINDOW:
                allowed = self._check_fixed_window()
            elif self.config.strategy == RateLimitStrategy.ADAPTIVE:
                allowed = self._check_adaptive()
            else:
                allowed = self._check_token_bucket()
            
            if allowed:
                self.stats['allowed_requests'] += 1
                self.request_times.append(time.time())
                self.endpoint_requests[endpoint].append(time.time())
                
                # Reset circuit breaker on success
                if endpoint in self.circuit_breakers:
                    self.circuit_breakers[endpoint].failures = 0
            else:
                self.stats['rejected_requests'] += 1
                self._record_failure(endpoint)
            
            return allowed
    
    def _check_token_bucket(self) -> bool:
        """Token bucket algorithm implementation"""
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
    
    def _check_sliding_window(self) -> bool:
        """Sliding window algorithm implementation"""
        now = time.time()
        
        # Remove old requests outside window
        window_start = now - 3600  # 1 hour window
        while self.request_times and self.request_times[0] < window_start:
            self.request_times.popleft()
        
        # Check limits
        hour_requests = len(self.request_times)
        if hour_requests >= self.messages_per_hour:
            return False
        
        # Check minute limit
        minute_start = now - 60
        minute_requests = sum(1 for t in self.request_times if t > minute_start)
        if minute_requests >= self.config.requests_per_minute:
            return False
        
        return True
    
    def _check_fixed_window(self) -> bool:
        """Fixed window algorithm implementation"""
        # Simple implementation - can be enhanced with Redis
        now = datetime.now()
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        
        # Count requests in current hour
        hour_requests = sum(1 for t in self.request_times 
                          if t > current_hour.timestamp())
        
        return hour_requests < self.messages_per_hour
    
    def _check_adaptive(self) -> bool:
        """Adaptive rate limiting based on response patterns"""
        # Start with sliding window
        if not self._check_sliding_window():
            return False
        
        # Adapt based on recent success/failure ratio
        if self.stats['total_requests'] > 10:
            success_rate = self.stats['allowed_requests'] / self.stats['total_requests']
            
            # If high success rate, allow more
            if success_rate > 0.9:
                return True
            # If low success rate, be more restrictive
            elif success_rate < 0.5:
                # Additional throttling
                return random.random() < 0.5
        
        return True
    
    def _check_circuit_breaker(self, endpoint: str) -> bool:
        """
        Check circuit breaker state
        
        Args:
            endpoint: Endpoint to check
            
        Returns:
            True if circuit is closed (allowing requests)
        """
        breaker = self.circuit_breakers[endpoint]
        
        if breaker.state == "OPEN":
            # Check if timeout has passed
            if breaker.last_failure:
                elapsed = (datetime.now() - breaker.last_failure).seconds
                if elapsed > self.config.circuit_breaker_timeout:
                    # Move to half-open state
                    breaker.state = "HALF_OPEN"
                    breaker.last_state_change = datetime.now()
                    logger.info(f"Circuit breaker for {endpoint} moved to HALF_OPEN")
                else:
                    return False
            else:
                return False
        
        elif breaker.state == "HALF_OPEN":
            # Allow limited requests to test
            return random.random() < 0.2  # Allow 20% of requests
        
        return True  # CLOSED state
    
    def _record_failure(self, endpoint: str):
        """Record a failure for circuit breaker"""
        breaker = self.circuit_breakers[endpoint]
        breaker.failures += 1
        breaker.last_failure = datetime.now()
        
        # Check if we should trip the circuit breaker
        if breaker.failures >= self.config.circuit_breaker_threshold:
            if breaker.state != "OPEN":
                breaker.state = "OPEN"
                breaker.last_state_change = datetime.now()
                self.stats['circuit_breaker_trips'] += 1
                logger.warning(f"Circuit breaker tripped for {endpoint}")
    
    def _check_circuit_breakers(self):
        """Periodic check to reset circuit breakers"""
        with self.lock:
            for endpoint, breaker in self.circuit_breakers.items():
                if breaker.state == "OPEN" and breaker.last_failure:
                    elapsed = (datetime.now() - breaker.last_failure).seconds
                    if elapsed > self.config.circuit_breaker_timeout:
                        breaker.state = "HALF_OPEN"
                        logger.info(f"Circuit breaker for {endpoint} reset to HALF_OPEN")
    
    async def wait_if_needed(self) -> float:
        """
        Calculate and wait for the necessary delay
        
        Returns:
            Actual wait time in seconds
        """
        with self.lock:
            # Calculate wait time based on current rate
            if self.tokens < 1:
                # Need to wait for token refill
                wait_time = (1 - self.tokens) / self.refill_rate
            else:
                # Check if we're close to limits
                recent_requests = sum(1 for t in self.request_times 
                                    if t > time.time() - 60)
                
                if recent_requests >= self.config.requests_per_minute * 0.8:
                    # Getting close to limit, add delay
                    wait_time = self.config.cooldown_seconds
                else:
                    wait_time = 0
        
        if wait_time > 0:
            logger.debug(f"Rate limiting: waiting {wait_time:.2f} seconds")
            await asyncio.sleep(wait_time)
        
        return wait_time
    
    def get_remaining_capacity(self) -> Dict[str, int]:
        """
        Get remaining capacity for different time windows
        
        Returns:
            Dictionary with remaining capacity
        """
        now = time.time()
        
        # Hour capacity
        hour_requests = sum(1 for t in self.request_times if t > now - 3600)
        hour_remaining = max(0, self.messages_per_hour - hour_requests)
        
        # Day capacity
        day_requests = sum(1 for t in self.request_times if t > now - 86400)
        day_remaining = max(0, self.messages_per_day - day_requests)
        
        # Minute capacity
        minute_requests = sum(1 for t in self.request_times if t > now - 60)
        minute_remaining = max(0, self.config.requests_per_minute - minute_requests)
        
        return {
            'tokens': int(self.tokens),
            'minute': minute_remaining,
            'hour': hour_remaining,
            'day': day_remaining
        }
    
    def reset_endpoint(self, endpoint: str):
        """
        Reset rate limiting for specific endpoint
        
        Args:
            endpoint: Endpoint to reset
        """
        with self.lock:
            if endpoint in self.circuit_breakers:
                self.circuit_breakers[endpoint] = CircuitBreakerState()
            if endpoint in self.endpoint_requests:
                self.endpoint_requests[endpoint].clear()
            logger.info(f"Rate limiter reset for endpoint: {endpoint}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        with self.lock:
            stats = self.stats.copy()
            stats['remaining_capacity'] = self.get_remaining_capacity()
            stats['circuit_breakers'] = {
                endpoint: {
                    'state': breaker.state,
                    'failures': breaker.failures
                }
                for endpoint, breaker in self.circuit_breakers.items()
            }
            return stats
    
    def emergency_stop(self):
        """Emergency stop - block all requests"""
        with self.lock:
            logger.critical("EMERGENCY STOP activated - blocking all requests")
            self.tokens = 0
            self.max_tokens = 0
            self.refill_rate = 0
            
            # Open all circuit breakers
            for breaker in self.circuit_breakers.values():
                breaker.state = "OPEN"
    
    def resume_normal_operation(self):
        """Resume normal operation after emergency stop"""
        with self.lock:
            logger.info("Resuming normal rate limiting operation")
            self.tokens = self.config.burst_size
            self.max_tokens = self.config.burst_size
            self.refill_rate = self.config.requests_per_second
            
            # Reset circuit breakers
            for breaker in self.circuit_breakers.values():
                breaker.state = "CLOSED"
                breaker.failures = 0
    
    # Distributed rate limiting with Redis
    async def check_distributed_limit(self, key: str, limit: int, 
                                     window: int) -> bool:
        """
        Check distributed rate limit using Redis
        
        Args:
            key: Redis key for the limit
            limit: Maximum requests in window
            window: Time window in seconds
            
        Returns:
            True if under limit
        """
        if not self.redis_client:
            return True  # Fall back to local limiting
        
        try:
            pipe = self.redis_client.pipeline()
            now = time.time()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, now - window)
            
            # Count current entries
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(now): now})
            
            # Set expiry
            pipe.expire(key, window)
            
            results = pipe.execute()
            current_count = results[1]
            
            return current_count < limit
            
        except Exception as e:
            logger.error(f"Redis rate limiting error: {e}")
            return True  # Fail open


import random  # Add this import at the top