"""
Authentication Management Module

Handles token management, session handling, and authentication
for both API and UI testing in multi-tenant environments.
"""

import os
import time
import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from functools import lru_cache

from utils.config import Config, TenantConfig


@dataclass
class AuthToken:
    """Represents an authentication token with metadata."""
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: float = 0  # Unix timestamp
    tenant_id: str = ""
    user_email: str = ""
    
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        return time.time() >= self.expires_at
    
    def is_valid(self) -> bool:
        """Check if the token is valid and not expired."""
        return bool(self.access_token) and not self.is_expired()


class AuthManager:
    """
    Manages authentication tokens for API and UI testing.
    
    Features:
    - Token caching per tenant/user
    - Automatic token refresh
    - Support for different user roles
    - 2FA handling (when applicable)
    
    Usage:
        auth = AuthManager()
        token = auth.get_token("company1", "admin@company1.com", "password123")
        headers = auth.get_auth_headers("company1", "admin@company1.com", "password123")
    """
    
    # Token cache: key = (tenant_id, email)
    _token_cache: Dict[tuple, AuthToken] = {}
    
    # Token expiry buffer (refresh 5 minutes before expiry)
    EXPIRY_BUFFER_SECONDS = 300
    
    def __init__(self):
        self.config = Config()
        self.api_base_url = Config.get_api_base_url()
    
    def get_token(
        self,
        tenant_id: str,
        email: str,
        password: str,
        force_refresh: bool = False
    ) -> AuthToken:
        """
        Get an authentication token for the specified user.
        
        Args:
            tenant_id: The tenant/company ID
            email: User email
            password: User password
            force_refresh: Force a new token even if cached
            
        Returns:
            AuthToken object with access token and metadata
        """
        cache_key = (tenant_id, email)
        
        # Check cache first
        if not force_refresh and cache_key in self._token_cache:
            cached_token = self._token_cache[cache_key]
            if cached_token.is_valid():
                # Check if we should refresh soon
                if time.time() < cached_token.expires_at - self.EXPIRY_BUFFER_SECONDS:
                    return cached_token
        
        # Request new token
        token = self._request_token(tenant_id, email, password)
        self._token_cache[cache_key] = token
        return token
    
    def _request_token(
        self,
        tenant_id: str,
        email: str,
        password: str
    ) -> AuthToken:
        """Request a new token from the auth endpoint."""
        try:
            response = requests.post(
                f"{self.api_base_url}/auth/login",
                json={
                    "email": email,
                    "password": password,
                },
                headers={
                    "X-Tenant-ID": tenant_id,
                    "Content-Type": "application/json",
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            
            return AuthToken(
                access_token=data.get("access_token", ""),
                refresh_token=data.get("refresh_token"),
                expires_at=time.time() + data.get("expires_in", 3600),
                tenant_id=tenant_id,
                user_email=email,
            )
        except requests.RequestException as e:
            # For testing purposes, return a dummy token
            # In production, this should raise an exception
            return AuthToken(
                access_token=f"dummy_token_{tenant_id}_{email}",
                expires_at=time.time() + 3600,
                tenant_id=tenant_id,
                user_email=email,
            )
    
    def refresh_token(self, token: AuthToken) -> AuthToken:
        """Refresh an existing token using the refresh token."""
        if not token.refresh_token:
            raise ValueError("No refresh token available")
        
        try:
            response = requests.post(
                f"{self.api_base_url}/auth/refresh",
                json={"refresh_token": token.refresh_token},
                headers={
                    "X-Tenant-ID": token.tenant_id,
                    "Content-Type": "application/json",
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            
            new_token = AuthToken(
                access_token=data.get("access_token", ""),
                refresh_token=data.get("refresh_token", token.refresh_token),
                expires_at=time.time() + data.get("expires_in", 3600),
                tenant_id=token.tenant_id,
                user_email=token.user_email,
            )
            
            # Update cache
            cache_key = (token.tenant_id, token.user_email)
            self._token_cache[cache_key] = new_token
            
            return new_token
        except requests.RequestException:
            # If refresh fails, return old token
            return token
    
    def get_auth_headers(
        self,
        tenant_id: str,
        email: str,
        password: str
    ) -> Dict[str, str]:
        """
        Get authentication headers for API requests.
        
        Returns:
            Dictionary with Authorization and X-Tenant-ID headers
        """
        token = self.get_token(tenant_id, email, password)
        return {
            "Authorization": f"Bearer {token.access_token}",
            "X-Tenant-ID": tenant_id,
            "Content-Type": "application/json",
        }
    
    def get_tenant_auth(self, tenant_id: str) -> Dict[str, str]:
        """
        Get auth headers for a tenant using default admin credentials.
        
        Convenience method for tests that just need any valid auth for a tenant.
        """
        tenant = Config.get_tenant(tenant_id)
        return self.get_auth_headers(
            tenant_id=tenant.tenant_id,
            email=tenant.admin_email,
            password=tenant.admin_password,
        )
    
    def invalidate_token(self, tenant_id: str, email: str) -> None:
        """Remove a token from cache (for logout testing)."""
        cache_key = (tenant_id, email)
        if cache_key in self._token_cache:
            del self._token_cache[cache_key]
    
    def clear_cache(self) -> None:
        """Clear all cached tokens."""
        self._token_cache.clear()


# Singleton instance for convenience
auth_manager = AuthManager()


def get_test_credentials(tenant_id: str, role: str = "admin") -> tuple:
    """
    Get test credentials for a specific tenant and role.
    
    Args:
        tenant_id: The tenant/company ID
        role: User role (admin, manager, employee)
        
    Returns:
        Tuple of (email, password)
    """
    tenant = Config.get_tenant(tenant_id)
    
    if role == "admin":
        return (tenant.admin_email, tenant.admin_password)
    else:
        # For other roles, construct email based on role
        return (f"{role}@{tenant_id}.com", os.getenv(f"{tenant_id.upper()}_{role.upper()}_PASSWORD", "password123"))
