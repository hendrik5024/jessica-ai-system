"""
Code Versioning System - Tracks code changes and enables rollback
Maintains version history and allows reverting to previous versions
"""

import logging
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib

logger = logging.getLogger("jessica.automation.code_versioning")


class CodeVersion:
    """Represents a single code version"""
    
    def __init__(self, module_name: str, version_id: str, code: str, 
                 reason: str, metadata: Optional[Dict] = None):
        self.module_name = module_name
        self.version_id = version_id
        self.code = code
        self.reason = reason
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        self.code_hash = self._compute_hash(code)
    
    def _compute_hash(self, code: str) -> str:
        """Compute SHA256 hash of code"""
        return hashlib.sha256(code.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'module_name': self.module_name,
            'version_id': self.version_id,
            'reason': self.reason,
            'created_at': self.created_at,
            'code_hash': self.code_hash,
            'metadata': self.metadata,
        }


class CodeVersioning:
    """
    Manages version control for code changes
    Enables rollback and tracks history
    """

    def __init__(self, base_path: str = "jessica/_code_versions"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.versions_dir = self.base_path / "versions"
        self.history_file = self.base_path / "version_history.json"
        self.versions_dir.mkdir(exist_ok=True)
        
        self.history = self._load_history()
        
        logger.info(f"CodeVersioning initialized at {self.base_path}")

    def _load_history(self) -> Dict:
        """Load version history"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load history: {e}")
        
        return {'versions': {}}

    def _save_history(self):
        """Save version history"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def commit_change(self, module_name: str, code: str, reason: str, 
                     metadata: Optional[Dict] = None) -> str:
        """
        Commit a code change to version history
        
        Args:
            module_name: Name of module being versioned
            code: Code content
            reason: Reason for change (e.g., "bugfix", "optimization")
            metadata: Additional metadata about change
            
        Returns:
            Version ID
        """
        version_id = self._generate_version_id(module_name)
        
        # Create version object
        version = CodeVersion(module_name, version_id, code, reason, metadata)
        
        # Save code file
        code_file = self.versions_dir / f"{version_id}.py"
        try:
            with open(code_file, 'w') as f:
                f.write(code)
        except Exception as e:
            logger.error(f"Failed to save version file: {e}")
            raise
        
        # Update history
        if module_name not in self.history['versions']:
            self.history['versions'][module_name] = []
        
        self.history['versions'][module_name].append(version.to_dict())
        self._save_history()
        
        logger.info(f"Committed version: {version_id} for {module_name}")
        return version_id

    def get_version(self, module_name: str, version_id: str) -> Optional[str]:
        """Get code from specific version"""
        code_file = self.versions_dir / f"{version_id}.py"
        
        if not code_file.exists():
            logger.warning(f"Version file not found: {version_id}")
            return None
        
        try:
            with open(code_file, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read version: {e}")
            return None

    def get_version_history(self, module_name: str, limit: Optional[int] = None) -> List[Dict]:
        """Get version history for a module"""
        if module_name not in self.history['versions']:
            return []
        
        versions = self.history['versions'][module_name]
        
        if limit:
            versions = versions[-limit:]
        
        return versions

    def get_latest_version(self, module_name: str) -> Optional[Dict]:
        """Get latest version for a module"""
        versions = self.get_version_history(module_name)
        
        if not versions:
            return None
        
        return versions[-1]

    def rollback_to_version(self, module_name: str, version_id: str, 
                           target_path: str, reason: str = "Manual rollback") -> bool:
        """
        Rollback to specific version
        
        Args:
            module_name: Module to rollback
            version_id: Version to rollback to
            target_path: Where to write the rolled-back code
            reason: Reason for rollback
            
        Returns:
            Success status
        """
        code = self.get_version(module_name, version_id)
        
        if code is None:
            logger.error(f"Cannot rollback: version {version_id} not found")
            return False
        
        try:
            # Backup current version first
            target_file = Path(target_path)
            if target_file.exists():
                backup_file = target_file.with_suffix('.backup')
                shutil.copy(target_file, backup_file)
                logger.info(f"Backed up current version to {backup_file}")
            
            # Write rolled-back code
            with open(target_path, 'w') as f:
                f.write(code)
            
            logger.info(f"Rolled back {module_name} to {version_id}")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def compare_versions(self, module_name: str, version_id_1: str, version_id_2: str) -> Dict:
        """Compare two versions"""
        code1 = self.get_version(module_name, version_id_1)
        code2 = self.get_version(module_name, version_id_2)
        
        if code1 is None or code2 is None:
            logger.error("One or both versions not found")
            return {'error': 'Version not found'}
        
        # Simple diff - count changed lines
        lines1 = code1.split('\n')
        lines2 = code2.split('\n')
        
        changed_lines = 0
        added_lines = 0
        removed_lines = 0
        
        if len(lines1) < len(lines2):
            added_lines = len(lines2) - len(lines1)
        elif len(lines1) > len(lines2):
            removed_lines = len(lines1) - len(lines2)
        
        # Count different lines
        for l1, l2 in zip(lines1, lines2):
            if l1 != l2:
                changed_lines += 1
        
        return {
            'version_1': version_id_1,
            'version_2': version_id_2,
            'changed_lines': changed_lines,
            'added_lines': added_lines,
            'removed_lines': removed_lines,
            'total_changes': changed_lines + added_lines + removed_lines,
        }

    def tag_version(self, version_id: str, tag_name: str, description: str = "") -> bool:
        """Create a tagged version for easy reference"""
        try:
            # Find version in history
            for module_name, versions in self.history['versions'].items():
                for version in versions:
                    if version['version_id'] == version_id:
                        version['tags'] = version.get('tags', [])
                        version['tags'].append({
                            'name': tag_name,
                            'description': description,
                            'created_at': datetime.now().isoformat(),
                        })
                        self._save_history()
                        logger.info(f"Tagged version {version_id} as '{tag_name}'")
                        return True
            
            logger.error(f"Version not found: {version_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to tag version: {e}")
            return False

    def get_versions_by_tag(self, tag_name: str) -> List[Dict]:
        """Get all versions with a specific tag"""
        tagged_versions = []
        
        for module_name, versions in self.history['versions'].items():
            for version in versions:
                tags = version.get('tags', [])
                for tag in tags:
                    if tag['name'] == tag_name:
                        tagged_versions.append({
                            'module': module_name,
                            'version': version,
                            'tag': tag,
                        })
        
        return tagged_versions

    def get_statistics(self) -> Dict:
        """Get versioning statistics"""
        total_versions = 0
        module_count = 0
        
        for module_name, versions in self.history['versions'].items():
            module_count += 1
            total_versions += len(versions)
        
        return {
            'total_modules': module_count,
            'total_versions': total_versions,
            'modules': {
                module_name: {
                    'version_count': len(versions),
                    'latest_version': versions[-1] if versions else None,
                }
                for module_name, versions in self.history['versions'].items()
            }
        }

    def cleanup_old_versions(self, keep_versions: int = 10) -> int:
        """
        Remove old versions, keeping only recent ones
        
        Args:
            keep_versions: Number of versions to keep per module
            
        Returns:
            Number of versions removed
        """
        removed_count = 0
        
        for module_name, versions in self.history['versions'].items():
            if len(versions) > keep_versions:
                versions_to_remove = versions[:-keep_versions]
                
                for version in versions_to_remove:
                    version_id = version['version_id']
                    code_file = self.versions_dir / f"{version_id}.py"
                    
                    try:
                        if code_file.exists():
                            code_file.unlink()
                            removed_count += 1
                            logger.debug(f"Removed old version: {version_id}")
                    except Exception as e:
                        logger.error(f"Failed to remove version file: {e}")
                
                # Update history
                self.history['versions'][module_name] = versions[-keep_versions:]
        
        if removed_count > 0:
            self._save_history()
            logger.info(f"Cleaned up {removed_count} old versions")
        
        return removed_count

    def _generate_version_id(self, module_name: str) -> str:
        """Generate unique version ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{module_name}_{timestamp}"

    def get_change_summary(self, module_name: str, limit: int = 5) -> str:
        """Generate summary of recent changes"""
        versions = self.get_version_history(module_name, limit=limit)
        
        if not versions:
            return f"No version history for {module_name}"
        
        summary = f"Recent changes to {module_name}:\n"
        summary += "=" * 50 + "\n\n"
        
        for i, version in enumerate(reversed(versions), 1):
            summary += f"{i}. {version['version_id']}\n"
            summary += f"   Reason: {version['reason']}\n"
            summary += f"   Date: {version['created_at']}\n"
            if version.get('tags'):
                tags = ", ".join([t['name'] for t in version['tags']])
                summary += f"   Tags: {tags}\n"
            summary += "\n"
        
        return summary
