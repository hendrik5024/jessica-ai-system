"""
Phase 4: Production Configuration Manager

Handles separation of prod/test modes with safety constraints.
- Configuration validation
- Resource limit enforcement
- Environment isolation
- Secrets management
- Version tracking
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class DeploymentMode(Enum):
    """Deployment environment."""
    TEST = "test"
    PRODUCTION = "production"


class OperatorVersion(Enum):
    """Operator version tracking."""
    PHASE_3 = "phase_3"
    PHASE_3_5 = "phase_3_5"  # Current frozen version
    PHASE_3_5_REFINED = "phase_3_5_refined"


@dataclass
class SafetyConfig:
    """Safety constraints for production."""
    enabled: bool = True
    operator_timeout_ms: int = 30000  # 30 second timeout
    memory_limit_mb: int = 500  # 500 MB max
    max_retries: int = 3
    rollback_on_violation: bool = True
    
    def validate(self) -> list[str]:
        """Validate safety configuration."""
        errors = []
        
        if self.operator_timeout_ms < 1000:
            errors.append("operator_timeout_ms must be >= 1000 (1 second)")
        if self.operator_timeout_ms > 300000:
            errors.append("operator_timeout_ms must be <= 300000 (5 minutes)")
            
        if self.memory_limit_mb < 100:
            errors.append("memory_limit_mb must be >= 100")
        if self.memory_limit_mb > 2000:
            errors.append("memory_limit_mb must be <= 2000")
            
        if self.max_retries < 1 or self.max_retries > 10:
            errors.append("max_retries must be between 1 and 10")
            
        return errors


@dataclass
class ObservabilityConfig:
    """Observability and logging configuration."""
    operator_tracing: bool = True
    trace_buffer_size: int = 10000
    export_format: str = "json"  # json | csv
    telemetry_export_interval_sec: int = 300  # 5 minutes
    telemetry_enabled: bool = True
    dashboard_enabled: bool = True
    
    def validate(self) -> list[str]:
        """Validate observability configuration."""
        errors = []
        
        if self.trace_buffer_size < 100:
            errors.append("trace_buffer_size must be >= 100")
        if self.trace_buffer_size > 100000:
            errors.append("trace_buffer_size must be <= 100000")
            
        if self.export_format not in ["json", "csv"]:
            errors.append("export_format must be 'json' or 'csv'")
            
        if self.telemetry_export_interval_sec < 10:
            errors.append("telemetry_export_interval_sec must be >= 10")
        if self.telemetry_export_interval_sec > 3600:
            errors.append("telemetry_export_interval_sec must be <= 3600")
            
        return errors


@dataclass
class PerformanceConfig:
    """Performance optimization configuration."""
    batch_processing: bool = True
    max_batch_size: int = 50
    cache_enabled: bool = True
    cache_ttl_sec: int = 3600  # 1 hour
    async_logging: bool = True
    
    def validate(self) -> list[str]:
        """Validate performance configuration."""
        errors = []
        
        if self.max_batch_size < 1 or self.max_batch_size > 500:
            errors.append("max_batch_size must be between 1 and 500")
            
        if self.cache_ttl_sec < 0:
            errors.append("cache_ttl_sec must be >= 0")
        if self.cache_ttl_sec > 86400:
            errors.append("cache_ttl_sec must be <= 86400 (24 hours)")
            
        return errors


@dataclass
class OperatorConfig:
    """Operator configuration (FROZEN in Phase 4)."""
    frozen_version: str = OperatorVersion.PHASE_3_5.value
    detect_bottleneck: str = "detect_bottleneck_refined"
    fallback_to_phase_3: bool = True
    allow_runtime_modification: bool = False  # MUST be False
    
    def validate(self) -> list[str]:
        """Validate operator configuration."""
        errors = []
        
        if self.frozen_version not in [v.value for v in OperatorVersion]:
            errors.append(f"frozen_version must be one of: {[v.value for v in OperatorVersion]}")
            
        if self.allow_runtime_modification:
            errors.append("allow_runtime_modification MUST be False in Phase 4")
            
        return errors


@dataclass
class ProductionConfig:
    """Complete production configuration."""
    mode: str = DeploymentMode.PRODUCTION.value
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    observability: ObservabilityConfig = field(default_factory=ObservabilityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    operators: OperatorConfig = field(default_factory=OperatorConfig)
    
    # Deployment metadata
    deployment_id: str = ""
    deployment_timestamp: str = ""
    phase: str = "4"
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate entire configuration."""
        errors = []
        
        # Validate mode
        if self.mode not in [m.value for m in DeploymentMode]:
            errors.append(f"mode must be one of: {[m.value for m in DeploymentMode]}")
        
        # Validate sub-configurations
        errors.extend(self.safety.validate())
        errors.extend(self.observability.validate())
        errors.extend(self.performance.validate())
        errors.extend(self.operators.validate())
        
        # Phase 4 specific constraints
        if self.operators.frozen_version != OperatorVersion.PHASE_3_5.value:
            errors.append(f"Phase 4 requires frozen_version={OperatorVersion.PHASE_3_5.value}")
        
        if self.operators.allow_runtime_modification:
            errors.append("Phase 4 forbids runtime operator modification")
        
        return (len(errors) == 0, errors)
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> tuple[ProductionConfig, list[str]]:
        """Load configuration from YAML file."""
        errors = []
        
        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
        except FileNotFoundError:
            return None, [f"Configuration file not found: {yaml_path}"]
        except yaml.YAMLError as e:
            return None, [f"Invalid YAML: {str(e)}"]
        
        try:
            config = cls(
                mode=data.get('mode', 'production'),
                safety=SafetyConfig(**data.get('safety', {})),
                observability=ObservabilityConfig(**data.get('observability', {})),
                performance=PerformanceConfig(**data.get('performance', {})),
                operators=OperatorConfig(**data.get('operators', {})),
                deployment_id=data.get('deployment_id', ''),
                deployment_timestamp=data.get('deployment_timestamp', ''),
            )
        except TypeError as e:
            return None, [f"Invalid configuration structure: {str(e)}"]
        
        # Validate loaded config
        is_valid, validation_errors = config.validate()
        if not is_valid:
            errors.extend(validation_errors)
        
        return config, errors
    
    def to_yaml(self, output_path: str) -> tuple[bool, str]:
        """Export configuration to YAML file."""
        try:
            data = {
                'mode': self.mode,
                'safety': {
                    'enabled': self.safety.enabled,
                    'operator_timeout_ms': self.safety.operator_timeout_ms,
                    'memory_limit_mb': self.safety.memory_limit_mb,
                    'max_retries': self.safety.max_retries,
                    'rollback_on_violation': self.safety.rollback_on_violation,
                },
                'observability': {
                    'operator_tracing': self.observability.operator_tracing,
                    'trace_buffer_size': self.observability.trace_buffer_size,
                    'export_format': self.observability.export_format,
                    'telemetry_export_interval_sec': self.observability.telemetry_export_interval_sec,
                },
                'performance': {
                    'batch_processing': self.performance.batch_processing,
                    'max_batch_size': self.performance.max_batch_size,
                    'cache_enabled': self.performance.cache_enabled,
                    'cache_ttl_sec': self.performance.cache_ttl_sec,
                },
                'operators': {
                    'frozen_version': self.operators.frozen_version,
                    'detect_bottleneck': self.operators.detect_bottleneck,
                    'fallback_to_phase_3': self.operators.fallback_to_phase_3,
                    'allow_runtime_modification': self.operators.allow_runtime_modification,
                },
                'deployment_id': self.deployment_id,
                'deployment_timestamp': self.deployment_timestamp,
                'phase': self.phase,
            }
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
            
            return True, f"Configuration saved to {output_path}"
        except Exception as e:
            return False, f"Failed to save configuration: {str(e)}"


class ConfigurationManager:
    """Central configuration management for production deployment."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager."""
        self.config_path = config_path
        self.config: Optional[ProductionConfig] = None
        self.validation_errors: list[str] = []
        self._is_initialized = False
    
    def load_configuration(self, mode: DeploymentMode = DeploymentMode.PRODUCTION) -> bool:
        """Load and validate configuration."""
        if self.config_path:
            # Load from file
            self.config, self.validation_errors = ProductionConfig.from_yaml(self.config_path)
            if self.config is None:
                return False
        else:
            # Use defaults
            self.config = ProductionConfig(mode=mode.value)
        
        # Validate configuration
        is_valid, errors = self.config.validate()
        if not is_valid:
            self.validation_errors.extend(errors)
            return False
        
        self._is_initialized = True
        return True
    
    def get_config(self) -> Optional[ProductionConfig]:
        """Get current configuration."""
        if not self._is_initialized:
            raise RuntimeError("Configuration not loaded. Call load_configuration() first.")
        return self.config
    
    def get_errors(self) -> list[str]:
        """Get validation errors."""
        return self.validation_errors
    
    def export_config(self, output_path: str) -> tuple[bool, str]:
        """Export current configuration to YAML."""
        if not self._is_initialized:
            return False, "Configuration not loaded"
        return self.config.to_yaml(output_path)
    
    def is_production_mode(self) -> bool:
        """Check if running in production mode."""
        if not self._is_initialized:
            return False
        return self.config.mode == DeploymentMode.PRODUCTION.value
    
    def is_test_mode(self) -> bool:
        """Check if running in test mode."""
        if not self._is_initialized:
            return False
        return self.config.mode == DeploymentMode.TEST.value
    
    def get_safety_config(self) -> SafetyConfig:
        """Get safety configuration."""
        if not self._is_initialized:
            raise RuntimeError("Configuration not loaded")
        return self.config.safety
    
    def get_observability_config(self) -> ObservabilityConfig:
        """Get observability configuration."""
        if not self._is_initialized:
            raise RuntimeError("Configuration not loaded")
        return self.config.observability
    
    def get_performance_config(self) -> PerformanceConfig:
        """Get performance configuration."""
        if not self._is_initialized:
            raise RuntimeError("Configuration not loaded")
        return self.config.performance
    
    def get_operator_config(self) -> OperatorConfig:
        """Get operator configuration."""
        if not self._is_initialized:
            raise RuntimeError("Configuration not loaded")
        return self.config.operators
    
    def to_json(self) -> str:
        """Export configuration as JSON."""
        if not self._is_initialized:
            raise RuntimeError("Configuration not loaded")
        
        return json.dumps({
            'mode': self.config.mode,
            'safety': self.config.safety.__dict__,
            'observability': self.config.observability.__dict__,
            'performance': self.config.performance.__dict__,
            'operators': self.config.operators.__dict__,
            'deployment_id': self.config.deployment_id,
            'deployment_timestamp': self.config.deployment_timestamp,
        }, indent=2)


# Global configuration manager instance
_global_config_manager: Optional[ConfigurationManager] = None


def initialize_global_config(config_path: Optional[str] = None, mode: DeploymentMode = DeploymentMode.PRODUCTION) -> bool:
    """Initialize global configuration manager."""
    global _global_config_manager
    _global_config_manager = ConfigurationManager(config_path)
    return _global_config_manager.load_configuration(mode)


def get_global_config() -> ConfigurationManager:
    """Get global configuration manager."""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigurationManager()
        _global_config_manager.load_configuration()
    return _global_config_manager
