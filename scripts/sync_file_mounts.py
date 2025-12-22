#!/usr/bin/env python3
"""
Choreo File Mount Synchronization Script

This script manages file mounts in Choreo by:
- Detecting changes in local YAML files under resources/
- Creating/updating ConfigMaps in Choreo
- Creating/updating file mounts to containers
- Cleaning up deleted files
"""

import os
import sys
import json
import hashlib
import requests
import subprocess
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


@dataclass
class ChoreoConfig:
    """Choreo API configuration"""
    base_url: str
    access_token: str
    org_uuid: str
    project_id: str
    component_id: str
    env_id: str
    app_env_id: str

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        logger.info("Loading configuration from environment variables...")
        required_vars = [
            'BASE_URL', 'ACCESS_TOKEN', 'ORG_UUID', 
            'PROJECT_ID', 'COMPONENT_ID', 'ENV_ID', 'APP_ENV_ID'
        ]
        
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            logger.error(f"Missing required environment variables: {', '.join(missing)}")
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        config = cls(
            base_url=os.getenv('BASE_URL'),
            access_token=os.getenv('ACCESS_TOKEN'),
            org_uuid=os.getenv('ORG_UUID'),
            project_id=os.getenv('PROJECT_ID'),
            component_id=os.getenv('COMPONENT_ID'),
            env_id=os.getenv('ENV_ID'),
            app_env_id=os.getenv('APP_ENV_ID')
        )
        logger.info(f"Configuration loaded successfully - Base URL: {config.base_url}")
        logger.info(f"Organization: {config.org_uuid}, Project: {config.project_id}")
        logger.info(f"Component: {config.component_id}, Environment: {config.env_id}")
        return config


@dataclass
class FileChange:
    """Represents a file change detected by git"""
    status: str  # 'A' (added), 'M' (modified), 'D' (deleted), 'R' (renamed)
    old_path: Optional[str]
    new_path: Optional[str]
    
    def get_current_path(self) -> Optional[str]:
        """Get the current path of the file"""
        return self.new_path if self.new_path else self.old_path


class ChoreoAPIClient:
    """Client for interacting with Choreo DevOps API"""
    
    def __init__(self, config: ChoreoConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {config.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Thunder File Mount Sync'
        })
    
    @staticmethod
    def get_id(obj: Dict) -> Optional[str]:
        """Get ID from object, handling both 'id' and 'ID' keys"""
        return obj.get('id') or obj.get('ID')
    
    def _get_query_params(self) -> Dict[str, str]:
        """Get common query parameters"""
        return {
            'organization_id': self.config.org_uuid,
            'project_id': self.config.project_id
        }
    
    def get_release_containers(self) -> List[Dict]:
        """Get all containers for the release"""
        url = f"{self.config.base_url}/api/v1/components/{self.config.component_id}/release/{self.config.app_env_id}"
        logger.info(f"GET {url}")
        logger.debug(f"Query params: {self._get_query_params()}")
        
        response = self.session.get(url, params=self._get_query_params())
        logger.info(f"Response status: {response.status_code}")
        response.raise_for_status()
        
        data = response.json()
        logger.debug(f"Response data: {json.dumps(data, indent=2)}")
        containers = data.get('data', {}).get('containers', [])
        print(f"✓ Found {len(containers)} container(s)")
        logger.info(f"Retrieved {len(containers)} container(s): {[c.get('name', c.get('id')) for c in containers]}")
        return containers
    
    def get_configmaps(self) -> List[Dict]:
        """Get all ConfigMaps for the environment"""
        url = f"{self.config.base_url}/api/v1/environments/{self.config.env_id}/configmap"
        logger.info(f"GET {url}")
        
        response = self.session.get(url, params=self._get_query_params())
        logger.info(f"Response status: {response.status_code}")
        response.raise_for_status()
        
        data = response.json()
        logger.debug(f"Response data: {json.dumps(data, indent=2)}")
        configmaps = data.get('data', [])
        print(f"✓ Found {len(configmaps)} existing ConfigMap(s)")
        logger.info(f"Retrieved {len(configmaps)} ConfigMap(s): {[cm.get('name') for cm in configmaps]}")
        return configmaps
    
    def get_configmap_details(self, configmap_id: str) -> Dict:
        """Get detailed information about a ConfigMap including content"""
        url = f"{self.config.base_url}/api/v1/environments/{self.config.env_id}/configmap/{configmap_id}"
        logger.info(f"GET {url}")
        
        response = self.session.get(url, params=self._get_query_params())
        logger.info(f"Response status: {response.status_code}")
        response.raise_for_status()
        
        data = response.json().get('data', {})
        logger.debug(f"ConfigMap details for {configmap_id}: {json.dumps(data, indent=2)}")
        return data
    
    def get_config_mounts(self, container_id: str) -> List[Dict]:
        """Get all config mounts for a container"""
        url = f"{self.config.base_url}/api/v1/components/{self.config.component_id}/release/{self.config.app_env_id}/container/{container_id}/config-mount"
        logger.info(f"GET {url}")
        
        response = self.session.get(url, params=self._get_query_params())
        logger.info(f"Response status: {response.status_code}")
        response.raise_for_status()
        
        mounts = response.json().get('data', [])
        logger.debug(f"Mounts for container {container_id}: {json.dumps(mounts, indent=2)}")
        logger.info(f"Retrieved {len(mounts)} mount(s) for container {container_id}")
        return mounts
    
    def create_configmap(self, name: str, file_content: str) -> str:
        """Create a new ConfigMap"""
        url = f"{self.config.base_url}/api/v1/environments/{self.config.env_id}/configmap"
        
        payload = {
            'config_type': 'File',
            'data': {
                'data': file_content
            },
            'environment_id': self.config.env_id,
            'metadata': {},
            'name': name,
            'organization_id': self.config.org_uuid,
            'project_id': self.config.project_id,
            'app_environment_id': self.config.app_env_id,
            'isBase64': False
        }
        
        logger.info(f"POST {url}")
        logger.debug(f"Payload: {json.dumps({**payload, 'data': {'data': f'<{len(file_content)} bytes>'}}, indent=2)}")
        
        response = self.session.post(url, params=self._get_query_params(), json=payload)
        logger.info(f"Response status: {response.status_code}")
        response.raise_for_status()
        
        response_data = response.json()
        logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
        data_obj = response_data.get('data', {})
        configmap_id = self.get_id(data_obj) if data_obj else None
        
        if not configmap_id:
            logger.error(f"Created ConfigMap but no ID returned. Response: {response_data}")
            raise ValueError(f"Failed to get ConfigMap ID from create response")
        
        print(f"  ✓ Created ConfigMap: {name} (ID: {configmap_id})")
        logger.info(f"Successfully created ConfigMap '{name}' with ID: {configmap_id}")
        return configmap_id
    
    def update_configmap(self, configmap_id: str, name: str, file_content: str) -> None:
        """Update an existing ConfigMap"""
        url = f"{self.config.base_url}/api/v1/environments/{self.config.env_id}/configmap/{configmap_id}"
        
        payload = {
            'config_type': 'File',
            'data': {
                'data': file_content
            },
            'environment_id': self.config.env_id,
            'metadata': {},
            'name': name,
            'organization_id': self.config.org_uuid,
            'project_id': self.config.project_id,
            'app_environment_id': self.config.app_env_id,
            'isBase64': False
        }
        
        logger.info(f"PUT {url}")
        logger.debug(f"Payload: {json.dumps({**payload, 'data': {'data': f'<{len(file_content)} bytes>'}}, indent=2)}")
        
        response = self.session.put(url, params=self._get_query_params(), json=payload)
        logger.info(f"Response status: {response.status_code}")
        response.raise_for_status()
        
        response_data = response.json()
        logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
        print(f"  ✓ Updated ConfigMap: {name} (ID: {configmap_id})")
        logger.info(f"Successfully updated ConfigMap '{name}' (ID: {configmap_id})")
    
    def delete_configmap(self, configmap_id: str, name: str) -> None:
        """Delete a ConfigMap"""
        url = f"{self.config.base_url}/api/v1/environments/{self.config.env_id}/configmap/{configmap_id}"
        
        logger.info(f"DELETE {url}")
        
        response = self.session.delete(url, params=self._get_query_params())
        logger.info(f"Response status: {response.status_code}")
        response.raise_for_status()
        
        print(f"  ✓ Deleted ConfigMap: {name} (ID: {configmap_id})")
        logger.info(f"Successfully deleted ConfigMap '{name}' (ID: {configmap_id})")
    
    def create_config_mount(self, container_id: str, configmap_id: str, mount_path: str) -> None:
        """Create a config mount for a container"""
        url = f"{self.config.base_url}/api/v1/components/{self.config.component_id}/release/{self.config.app_env_id}/container/{container_id}/config-mount"
        
        payload = {
            'app_environment_id': self.config.app_env_id,
            'config_key': 'data',
            'configmap_id': configmap_id,
            'container_id': container_id,
            'deploy_changes': True,
            'mount_path': mount_path,
            'mount_permissions': '0644',
            'mount_type': 'File',
            'secret_id': None
        }
        
        logger.info(f"POST {url}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = self.session.post(url, params=self._get_query_params(), json=payload)
        logger.info(f"Response status: {response.status_code}")
        response.raise_for_status()
        
        response_data = response.json()
        logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
        print(f"    ✓ Created mount: {mount_path}")
        logger.info(f"Successfully created mount at '{mount_path}' for container {container_id}")
    
    def delete_config_mount(self, container_id: str, mount_id: str, mount_path: str) -> None:
        """Delete a config mount"""
        url = f"{self.config.base_url}/api/v1/components/{self.config.component_id}/release/{self.config.app_env_id}/container/{container_id}/config-mount/{mount_id}"
        
        logger.info(f"DELETE {url}")
        
        response = self.session.delete(url, params=self._get_query_params())
        logger.info(f"Response status: {response.status_code}")
        response.raise_for_status()
        
        print(f"    ✓ Deleted mount: {mount_path}")
        logger.info(f"Successfully deleted mount '{mount_path}' (ID: {mount_id}) from container {container_id}")


class FileMountSynchronizer:
    """Manages synchronization of file mounts"""
    
    MOUNT_BASE_PATH = "/opt/thunder/repository"
    
    def __init__(self, client: ChoreoAPIClient, repo_root: str):
        self.client = client
        self.repo_root = Path(repo_root)
        self.resources_dir = self.repo_root / "resources"
    
    def get_file_changes(self, base_ref: str = "HEAD^") -> List[FileChange]:
        """Get list of changed files using git diff"""
        try:
            logger.info(f"Detecting file changes: comparing {base_ref} with HEAD")
            # Get changed files compared to previous commit
            result = subprocess.run(
                ['git', 'diff', '--name-status', '--diff-filter=AMDRT', base_ref, 'HEAD', 'resources/'],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            logger.debug(f"Git diff output: {result.stdout}")
            
            changes = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('\t')
                status = parts[0][0]  # First character is the status
                
                if status == 'R':  # Renamed file
                    old_path = parts[1]
                    new_path = parts[2]
                    changes.append(FileChange(status='R', old_path=old_path, new_path=new_path))
                elif status in ['A', 'M']:
                    file_path = parts[1]
                    changes.append(FileChange(status=status, old_path=None, new_path=file_path))
                elif status == 'D':
                    file_path = parts[1]
                    changes.append(FileChange(status='D', old_path=file_path, new_path=None))
            
            print(f"\n📋 Detected {len(changes)} file change(s):")
            for change in changes:
                if change.status == 'R':
                    print(f"  • Renamed: {change.old_path} → {change.new_path}")
                elif change.status == 'A':
                    print(f"  • Added: {change.new_path}")
                elif change.status == 'M':
                    print(f"  • Modified: {change.new_path}")
                elif change.status == 'D':
                    print(f"  • Deleted: {change.old_path}")
            
            return changes
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting file changes: {e}")
            logger.error(f"Git stderr: {e.stderr}")
            print(f"Error getting file changes: {e}")
            return []
    
    def file_path_to_configmap_name(self, file_path: str) -> str:
        """Convert file path to ConfigMap name"""
        # resources/applications/application_1.yaml → thunder-applications-application_1
        rel_path = Path(file_path).relative_to('resources')
        parts = list(rel_path.parts)
        parts[-1] = Path(parts[-1]).stem  # Remove .yaml extension
        return 'thunder-' + '-'.join(parts)
    
    def file_path_to_mount_path(self, file_path: str) -> str:
        """Convert file path to mount path"""
        # resources/applications/application_1.yaml → /opt/thunder/repository/resources/applications/application_1.yaml
        return f"{self.MOUNT_BASE_PATH}/{file_path}"
    
    def read_file_content(self, file_path: str) -> str:
        """Read file content from repository"""
        full_path = self.repo_root / file_path
        with open(full_path, 'r') as f:
            return f.read()
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def sync_file_addition_or_modification(self, file_path: str, containers: List[Dict], 
                                          configmap_index: Dict[str, Dict]) -> None:
        """Sync a file that was added or modified"""
        logger.info(f"Starting sync for file: {file_path}")
        configmap_name = self.file_path_to_configmap_name(file_path)
        mount_path = self.file_path_to_mount_path(file_path)
        file_content = self.read_file_content(file_path)
        content_hash = self.calculate_content_hash(file_content)
        
        print(f"\n🔄 Processing: {file_path}")
        print(f"  ConfigMap name: {configmap_name}")
        print(f"  Mount path: {mount_path}")
        logger.info(f"ConfigMap: {configmap_name}, Mount: {mount_path}, Content hash: {content_hash[:16]}...")
        
        # Check if ConfigMap exists
        existing_configmap = configmap_index.get(configmap_name)
        existing_id = self.client.get_id(existing_configmap) if existing_configmap else None
        
        if existing_configmap and existing_id:
            # Get detailed ConfigMap to compare content
            configmap_id = existing_id
            logger.info(f"ConfigMap '{configmap_name}' exists (ID: {configmap_id}), checking for content changes...")
            
            try:
                details = self.client.get_configmap_details(configmap_id)
                existing_content = details.get('data', {}).get('data', '')
                existing_hash = self.calculate_content_hash(existing_content)
                
                logger.info(f"Existing hash: {existing_hash[:16]}..., New hash: {content_hash[:16]}...")
                if existing_hash != content_hash:
                    print(f"  ℹ Content changed, updating ConfigMap...")
                    logger.info(f"Content differs, updating ConfigMap '{configmap_name}'")
                    self.client.update_configmap(configmap_id, configmap_name, file_content)
                else:
                    print(f"  ✓ Content unchanged, skipping ConfigMap update")
                    logger.info(f"Content identical, skipping update for '{configmap_name}'")
            except Exception as e:
                # If we can't get details or update fails, try to create a new one
                logger.warning(f"Failed to get/update existing ConfigMap '{configmap_name}': {str(e)}")
                logger.info(f"Will create new ConfigMap instead")
                print(f"  ⚠ Failed to update existing ConfigMap, creating new one...")
                configmap_id = self.client.create_configmap(configmap_name, file_content)
        else:
            # Create new ConfigMap (doesn't exist or missing ID)
            if existing_configmap:
                logger.warning(f"ConfigMap '{configmap_name}' exists but has no 'id' field: {existing_configmap}")
                print(f"  ⚠ ConfigMap exists but is invalid, creating new one...")
            else:
                logger.info(f"ConfigMap '{configmap_name}' not found, creating new one")
                print(f"  ℹ ConfigMap doesn't exist, creating...")
            configmap_id = self.client.create_configmap(configmap_name, file_content)
        
        # Ensure mounts exist for all containers
        print(f"  🔗 Checking mounts across {len(containers)} container(s)...")
        for container in containers:
            container_id = self.client.get_id(container)
            if not container_id:
                logger.warning(f"Container has no ID, skipping: {container}")
                continue
            container_name = container.get('name', container_id)
            
            # Get existing mounts for this container
            mounts = self.client.get_config_mounts(container_id)
            
            # Check if mount exists for this path
            mount_exists = any(m.get('mount_path') == mount_path for m in mounts)
            
            if not mount_exists:
                print(f"  ℹ Creating mount for container: {container_name}")
                self.client.create_config_mount(container_id, configmap_id, mount_path)
            else:
                print(f"    ✓ Mount already exists for container: {container_name}")
    
    def sync_file_rename(self, old_path: str, new_path: str, containers: List[Dict],
                        configmap_index: Dict[str, Dict]) -> None:
        """Sync a file that was renamed - update mount path"""
        old_configmap_name = self.file_path_to_configmap_name(old_path)
        new_configmap_name = self.file_path_to_configmap_name(new_path)
        old_mount_path = self.file_path_to_mount_path(old_path)
        new_mount_path = self.file_path_to_mount_path(new_path)
        
        print(f"\n🔄 Processing rename: {old_path} → {new_path}")
        logger.info(f"Processing file rename: {old_path} → {new_path}")
        
        # Delete old mounts
        mounts_deleted = 0
        for container in containers:
            container_id = self.client.get_id(container)
            if not container_id:
                logger.warning(f"Container has no ID, skipping: {container}")
                continue
            try:
                mounts = self.client.get_config_mounts(container_id)
                
                for mount in mounts:
                    if mount.get('mount_path') == old_mount_path:
                        mount_id = mount.get('id')
                        if mount_id:
                            print(f"  ℹ Deleting old mount: {old_mount_path}")
                            self.client.delete_config_mount(container_id, mount_id, old_mount_path)
                            mounts_deleted += 1
            except Exception as e:
                logger.warning(f"Failed to delete old mounts for container {container_id}: {str(e)}")
                print(f"  ⚠ Failed to delete old mount from container {container_id}")
        
        if mounts_deleted == 0:
            logger.info(f"No old mounts found at path: {old_mount_path}")
            print(f"  ℹ No old mounts found")
        
        # Update ConfigMap name and content, then create new mounts
        self.sync_file_addition_or_modification(new_path, containers, configmap_index)
    
    def sync_file_deletion(self, file_path: str, containers: List[Dict],
                          configmap_index: Dict[str, Dict]) -> None:
        """Sync a file that was deleted - remove mounts and ConfigMap"""
        configmap_name = self.file_path_to_configmap_name(file_path)
        mount_path = self.file_path_to_mount_path(file_path)
        
        print(f"\n🗑️  Processing deletion: {file_path}")
        logger.info(f"Processing deletion for: {file_path}")
        
        # Get ConfigMap ID
        configmap = configmap_index.get(configmap_name)
        if not configmap:
            print(f"  ⚠ ConfigMap '{configmap_name}' not found in Choreo, nothing to delete")
            logger.info(f"ConfigMap '{configmap_name}' doesn't exist, skipping deletion")
            return
        
        configmap_id = self.client.get_id(configmap)
        if not configmap_id:
            print(f"  ⚠ ConfigMap '{configmap_name}' has no ID, skipping deletion")
            logger.warning(f"ConfigMap '{configmap_name}' exists but has no 'id' field: {configmap}")
            return
        
        logger.info(f"Found ConfigMap to delete: {configmap_name} (ID: {configmap_id})")
        
        # Delete mounts from all containers
        print(f"  ℹ Removing mounts from containers...")
        mounts_deleted = 0
        for container in containers:
            container_id = self.client.get_id(container)
            if not container_id:
                logger.warning(f"Container has no ID, skipping: {container}")
                continue
            try:
                mounts = self.client.get_config_mounts(container_id)
                
                for mount in mounts:
                    if mount.get('mount_path') == mount_path:
                        mount_id = self.client.get_id(mount)
                        if mount_id:
                            self.client.delete_config_mount(container_id, mount_id, mount_path)
                            mounts_deleted += 1
                        else:
                            logger.warning(f"Mount at '{mount_path}' has no ID, skipping")
            except Exception as e:
                logger.warning(f"Failed to get/delete mounts for container {container_id}: {str(e)}")
                print(f"  ⚠ Failed to process mounts for container {container_id}")
        
        if mounts_deleted == 0:
            print(f"  ℹ No mounts found for path: {mount_path}")
            logger.info(f"No mounts found for deletion at path: {mount_path}")
        
        # Delete ConfigMap
        try:
            self.client.delete_configmap(configmap_id, configmap_name)
        except Exception as e:
            logger.error(f"Failed to delete ConfigMap '{configmap_name}': {str(e)}")
            print(f"  ⚠ Failed to delete ConfigMap: {str(e)}")
            # Don't raise - we've done our best to clean up
    
    def sync(self, base_ref: str = "HEAD^") -> None:
        """Main synchronization process"""
        logger.info("="*70)
        logger.info("Starting Thunder File Mount Synchronization")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info(f"Repository root: {self.repo_root}")
        logger.info(f"Base reference: {base_ref}")
        logger.info("="*70)
        
        print("=" * 70)
        print("🚀 Thunder File Mount Synchronization")
        print("=" * 70)
        
        # Get file changes
        changes = self.get_file_changes(base_ref)
        
        if not changes:
            print("\n✓ No changes detected in resources/ directory")
            logger.info("No changes detected, exiting")
            return
        
        # Fetch current state from Choreo
        print("\n📡 Fetching current state from Choreo...")
        containers = self.client.get_release_containers()
        configmaps = self.client.get_configmaps()
        
        # Build ConfigMap index by name
        configmap_index = {cm['name']: cm for cm in configmaps}
        
        # Process each change
        print("\n🔧 Synchronizing changes...")
        success_count = 0
        error_count = 0
        
        for change in changes:
            try:
                logger.info(f"Processing change: {change.status} - {change.get_current_path()}")
                if change.status == 'R':
                    self.sync_file_rename(change.old_path, change.new_path, containers, configmap_index)
                elif change.status in ['A', 'M']:
                    self.sync_file_addition_or_modification(change.new_path, containers, configmap_index)
                elif change.status == 'D':
                    self.sync_file_deletion(change.old_path, containers, configmap_index)
                
                success_count += 1
                logger.info(f"Successfully processed: {change.get_current_path()}")
            
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing {change.get_current_path()}: {str(e)}")
                print(f"\n❌ Error processing {change.get_current_path()}: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                traceback.print_exc()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 Synchronization Summary")
        print("=" * 70)
        print(f"✓ Successful: {success_count}")
        print(f"✗ Failed: {error_count}")
        print("=" * 70)
        
        logger.info("="*70)
        logger.info("Synchronization Summary")
        logger.info(f"Total changes processed: {len(changes)}")
        logger.info(f"Successful: {success_count}")
        logger.info(f"Failed: {error_count}")
        logger.info(f"Completion time: {datetime.now().isoformat()}")
        logger.info("="*70)
        
        if error_count > 0:
            logger.error("Synchronization completed with errors")
            sys.exit(1)
        else:
            logger.info("Synchronization completed successfully")


def main():
    """Main entry point"""
    try:
        logger.info("Thunder File Mount Sync - Starting execution")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        # Load configuration
        config = ChoreoConfig.from_env()
        
        # Create API client
        logger.info("Creating Choreo API client...")
        client = ChoreoAPIClient(config)
        
        # Create synchronizer
        repo_root = os.getenv('GITHUB_WORKSPACE', os.getcwd())
        logger.info(f"Initializing synchronizer with repo root: {repo_root}")
        synchronizer = FileMountSynchronizer(client, repo_root)
        
        # Get base reference for comparison (default to previous commit)
        base_ref = os.getenv('BASE_REF', 'HEAD^')
        logger.info(f"Using base reference: {base_ref}")
        
        # Run synchronization
        synchronizer.sync(base_ref)
        
        logger.info("Execution completed successfully")
        
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}")
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        logger.critical(traceback.format_exc())
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
