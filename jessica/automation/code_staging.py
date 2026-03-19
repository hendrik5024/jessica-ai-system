"""
Code Staging System - Safely stage code changes before deployment
Provides isolated environment for testing generated code
"""

import os
import json
import logging
import shutil
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger("jessica.automation.code_staging")


class StagingEnvironment:
    """Manages staged code in isolation"""

    def __init__(self, base_path: str = "jessica/_staged_updates"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.staging_dir = self.base_path / "staging"
        self.testing_dir = self.base_path / "testing"
        self.deployed_dir = self.base_path / "deployed"
        self.rejected_dir = self.base_path / "rejected"
        
        for dir_path in [self.staging_dir, self.testing_dir, self.deployed_dir, self.rejected_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.staging_manifest = self.base_path / "staging_manifest.json"
        self._load_manifest()
        
        logger.info(f"StagingEnvironment initialized at {self.base_path}")

    def _load_manifest(self):
        """Load staging manifest"""
        if self.staging_manifest.exists():
            try:
                with open(self.staging_manifest, 'r') as f:
                    self.manifest = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load manifest: {e}")
                self.manifest = {'staged': {}, 'testing': {}, 'deployed': [], 'rejected': []}
        else:
            self.manifest = {'staged': {}, 'testing': {}, 'deployed': [], 'rejected': []}

    def _save_manifest(self):
        """Save staging manifest"""
        try:
            with open(self.staging_manifest, 'w') as f:
                json.dump(self.manifest, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save manifest: {e}")

    def stage_code(self, proposal_id: str, module_name: str, code: str, metadata: Dict) -> str:
        """
        Stage generated code for testing
        
        Args:
            proposal_id: Unique proposal identifier
            module_name: Name of module
            code: Generated code content
            metadata: Additional metadata
            
        Returns:
            Staged file path
        """
        staged_file = self.staging_dir / f"{proposal_id}_{module_name}.py"
        
        try:
            with open(staged_file, 'w') as f:
                f.write(code)
            
            # Create metadata file
            metadata_file = self.staging_dir / f"{proposal_id}_{module_name}_meta.json"
            meta_data = {
                'proposal_id': proposal_id,
                'module_name': module_name,
                'staged_at': datetime.now().isoformat(),
                'staged_file': str(staged_file),
                'metadata': metadata,
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(meta_data, f, indent=2)
            
            # Update manifest
            self.manifest['staged'][proposal_id] = {
                'module': module_name,
                'file': str(staged_file),
                'metadata_file': str(metadata_file),
                'staged_at': datetime.now().isoformat(),
            }
            self._save_manifest()
            
            logger.info(f"Staged code: {proposal_id} -> {staged_file}")
            return str(staged_file)
            
        except Exception as e:
            logger.error(f"Failed to stage code: {e}")
            raise

    def move_to_testing(self, proposal_id: str) -> str:
        """Move staged code to testing environment"""
        if proposal_id not in self.manifest['staged']:
            logger.error(f"Proposal not found in staging: {proposal_id}")
            raise ValueError(f"Proposal {proposal_id} not in staging")
        
        staged_info = self.manifest['staged'][proposal_id]
        module_name = staged_info['module']
        
        staged_file = Path(staged_info['file'])
        testing_file = self.testing_dir / staged_file.name
        
        try:
            shutil.copy(staged_file, testing_file)
            
            # Copy metadata
            staged_meta = Path(staged_info['metadata_file'])
            testing_meta = self.testing_dir / staged_meta.name
            shutil.copy(staged_meta, testing_meta)
            
            # Update manifest
            self.manifest['testing'][proposal_id] = {
                'module': module_name,
                'file': str(testing_file),
                'moved_at': datetime.now().isoformat(),
            }
            
            del self.manifest['staged'][proposal_id]
            self._save_manifest()
            
            logger.info(f"Moved to testing: {proposal_id}")
            return str(testing_file)
            
        except Exception as e:
            logger.error(f"Failed to move to testing: {e}")
            raise

    def promote_to_deployed(self, proposal_id: str) -> str:
        """Promote tested code to deployed"""
        if proposal_id not in self.manifest['testing']:
            logger.error(f"Proposal not in testing: {proposal_id}")
            raise ValueError(f"Proposal {proposal_id} not in testing")
        
        testing_info = self.manifest['testing'][proposal_id]
        testing_file = Path(testing_info['file'])
        deployed_file = self.deployed_dir / testing_file.name
        
        try:
            shutil.copy(testing_file, deployed_file)
            
            # Copy metadata
            testing_meta = self.testing_dir / f"{proposal_id}_*_meta.json"
            # Find and copy metadata
            for meta_file in self.testing_dir.glob(f"{proposal_id}_*_meta.json"):
                deployed_meta = self.deployed_dir / meta_file.name
                shutil.copy(meta_file, deployed_meta)
                break
            
            # Update manifest
            self.manifest['deployed'].append({
                'proposal_id': proposal_id,
                'module': testing_info['module'],
                'file': str(deployed_file),
                'promoted_at': datetime.now().isoformat(),
            })
            
            del self.manifest['testing'][proposal_id]
            self._save_manifest()
            
            logger.info(f"Promoted to deployed: {proposal_id}")
            return str(deployed_file)
            
        except Exception as e:
            logger.error(f"Failed to promote: {e}")
            raise

    def reject_proposal(self, proposal_id: str, reason: str) -> bool:
        """Reject a proposal and move to rejected folder"""
        source_info = None
        source_dir = None
        
        if proposal_id in self.manifest['staged']:
            source_info = self.manifest['staged'][proposal_id]
            source_dir = 'staged'
        elif proposal_id in self.manifest['testing']:
            source_info = self.manifest['testing'][proposal_id]
            source_dir = 'testing'
        else:
            logger.error(f"Proposal not found: {proposal_id}")
            return False
        
        try:
            source_file = Path(source_info['file'])
            rejected_file = self.rejected_dir / source_file.name
            
            shutil.move(str(source_file), str(rejected_file))
            
            # Move metadata too
            for meta_file in (self.staging_dir if source_dir == 'staged' else self.testing_dir).glob(f"{proposal_id}_*_meta.json"):
                rejected_meta = self.rejected_dir / meta_file.name
                shutil.move(str(meta_file), str(rejected_meta))
                break
            
            # Update manifest
            self.manifest['rejected'].append({
                'proposal_id': proposal_id,
                'module': source_info['module'],
                'file': str(rejected_file),
                'reason': reason,
                'rejected_at': datetime.now().isoformat(),
            })
            
            if source_dir == 'staged':
                del self.manifest['staged'][proposal_id]
            else:
                del self.manifest['testing'][proposal_id]
            
            self._save_manifest()
            
            logger.info(f"Rejected proposal: {proposal_id} - {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reject proposal: {e}")
            return False

    def get_staged_files(self) -> List[Dict]:
        """Get list of staged files"""
        return [
            {
                'proposal_id': pid,
                'module': info['module'],
                'file': info['file'],
                'staged_at': info['staged_at'],
            }
            for pid, info in self.manifest['staged'].items()
        ]

    def get_testing_files(self) -> List[Dict]:
        """Get list of files in testing"""
        return [
            {
                'proposal_id': pid,
                'module': info['module'],
                'file': info['file'],
                'moved_at': info['moved_at'],
            }
            for pid, info in self.manifest['testing'].items()
        ]

    def get_deployed_files(self) -> List[Dict]:
        """Get list of deployed files"""
        return self.manifest['deployed']

    def get_rejected_files(self) -> List[Dict]:
        """Get list of rejected files"""
        return self.manifest['rejected']

    def cleanup_old_staged(self, days: int = 7) -> int:
        """Clean up old staged files not moved to testing"""
        import time
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        cleaned = 0
        
        for file_path in self.staging_dir.glob("*.py"):
            if os.path.getmtime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    # Also remove metadata
                    meta_file = file_path.parent / f"{file_path.stem}_meta.json"
                    if meta_file.exists():
                        os.remove(meta_file)
                    cleaned += 1
                except Exception as e:
                    logger.error(f"Failed to cleanup {file_path}: {e}")
        
        if cleaned > 0:
            self._save_manifest()
            logger.info(f"Cleaned up {cleaned} old staged files")
        
        return cleaned

    def get_statistics(self) -> Dict:
        """Get staging statistics"""
        return {
            'staged_count': len(self.manifest['staged']),
            'testing_count': len(self.manifest['testing']),
            'deployed_count': len(self.manifest['deployed']),
            'rejected_count': len(self.manifest['rejected']),
            'total_count': (len(self.manifest['staged']) + len(self.manifest['testing']) + 
                           len(self.manifest['deployed']) + len(self.manifest['rejected'])),
        }
