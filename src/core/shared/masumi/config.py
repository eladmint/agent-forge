"""
Masumi Network Configuration

Configuration management for Masumi Network integration using the provided
hacker guidelines credentials and endpoints.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class MasumiConfig:
    """Configuration for Masumi Network integration."""
    
    # Masumi hosted payment service (from hacker guidelines)
    payment_service_url: str = "https://payment.masumi.network"
    payment_bearer_token: str = os.getenv("MASUMI_PAYMENT_TOKEN", "your_masumi_payment_token_here")
    
    # Registry API configuration
    registry_api_key: str = os.getenv("MASUMI_REGISTRY_API_KEY", "your_masumi_registry_key_here")
    
    # OpenAI API key for testing (from hacker guidelines)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
    
    # Network configuration
    network: str = "preprod"  # preprod for testing, mainnet for production
    
    # CrewAI integration
    crewai_template_url: str = "https://github.com/masumi-network/crewai-masumi-quickstart-template"
    
    # Kodosumi deployment
    kodosumi_docs_url: str = "https://docs.kodosumi.io/"
    
    # Community support
    telegram_support: str = "https://t.me/+FtkeBaITmjlkZDky"
    discord_support: str = "https://discord.gg/WVDHxZQdzp"
    
    # tAda faucet for testing
    tada_faucet_url: str = "https://dispenser.masumi.network/"
    
    @classmethod
    def from_env(cls) -> 'MasumiConfig':
        """Create configuration from environment variables."""
        return cls(
            payment_service_url=os.getenv('MASUMI_PAYMENT_URL', cls.payment_service_url),
            payment_bearer_token=os.getenv('MASUMI_PAYMENT_TOKEN', cls.payment_bearer_token),
            registry_api_key=os.getenv('MASUMI_REGISTRY_KEY', cls.registry_api_key),
            openai_api_key=os.getenv('OPENAI_API_KEY', cls.openai_api_key),
            network=os.getenv('MASUMI_NETWORK', cls.network)
        )
    
    @classmethod 
    def for_testing(cls) -> 'MasumiConfig':
        """Create configuration optimized for testing with provided credentials."""
        return cls(
            network="preprod",
            # Use all the testing credentials from hacker guidelines
        )
    
    @classmethod
    def for_production(cls) -> 'MasumiConfig':
        """Create configuration for production use."""
        return cls(
            network="mainnet",
            # Production would use environment variables or secure config
            payment_service_url=os.getenv('MASUMI_PAYMENT_URL', 'https://payment.masumi.network'),
            payment_bearer_token=os.getenv('MASUMI_PAYMENT_TOKEN'),
            registry_api_key=os.getenv('MASUMI_REGISTRY_KEY'),
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'payment_service_url': self.payment_service_url,
            'network': self.network,
            'registry_api_key': self.registry_api_key,
            'crewai_template_url': self.crewai_template_url,
            'kodosumi_docs_url': self.kodosumi_docs_url,
            'support': {
                'telegram': self.telegram_support,
                'discord': self.discord_support,
                'faucet': self.tada_faucet_url
            }
        }
    
    def validate(self) -> bool:
        """Validate configuration completeness."""
        required_fields = [
            'payment_service_url',
            'payment_bearer_token', 
            'registry_api_key'
        ]
        
        for field in required_fields:
            if not getattr(self, field):
                return False
        
        return True