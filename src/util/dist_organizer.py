"""Organize dist/ directory structure for better file management."""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class DistOrganizer:
    """Organize and manage the dist/ directory structure."""
    
    def __init__(self, dist_root: str = "dist"):
        self.dist_root = Path(dist_root)
        self.organize_structure()
    
    def organize_structure(self):
        """Create organized directory structure."""
        # Main directories
        self.dirs = {
            'conversations': self.dist_root / 'conversations',
            'summaries': self.dist_root / 'summaries', 
            'analysis': self.dist_root / 'analysis',
            'reports': self.dist_root / 'reports',
            'golden_set': self.dist_root / 'golden_set',
            'archives': self.dist_root / 'archives'
        }
        
        # Create directories
        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.dirs['conversations'] / 'raw').mkdir(exist_ok=True)
        (self.dirs['conversations'] / 'processed').mkdir(exist_ok=True)
        (self.dirs['summaries'] / 'drafts').mkdir(exist_ok=True)
        (self.dirs['summaries'] / 'final').mkdir(exist_ok=True)
        (self.dirs['analysis'] / 'coverage').mkdir(exist_ok=True)
        (self.dirs['analysis'] / 'signals').mkdir(exist_ok=True)
        (self.dirs['reports'] / 'daily').mkdir(exist_ok=True)
        (self.dirs['reports'] / 'weekly').mkdir(exist_ok=True)
    
    def organize_existing_files(self):
        """Organize existing files in dist/ directory."""
        if not self.dist_root.exists():
            return
        
        # Find all files in dist/
        for item in self.dist_root.iterdir():
            if item.is_file():
                self._organize_file(item)
            elif item.is_dir() and item.name not in self.dirs:
                self._organize_directory(item)
    
    def _organize_file(self, file_path: Path):
        """Organize a single file based on its type and content."""
        file_name = file_path.name
        file_ext = file_path.suffix.lower()
        
        # Determine file type and destination
        if file_name.startswith('post_'):
            # Summary files
            if file_ext == '.md':
                dest = self.dirs['summaries'] / 'drafts' / file_name
            elif file_ext == '.html':
                dest = self.dirs['summaries'] / 'drafts' / file_name
            else:
                dest = self.dirs['summaries'] / 'drafts' / file_name
        elif file_name.startswith('full_conversation'):
            # Conversation files
            if file_ext == '.json':
                dest = self.dirs['conversations'] / 'processed' / file_name
            elif file_ext == '.md':
                dest = self.dirs['conversations'] / 'processed' / file_name
            else:
                dest = self.dirs['conversations'] / 'raw' / file_name
        elif 'conversation_vs_summary_analysis' in file_name:
            # Analysis files
            dest = self.dirs['analysis'] / 'coverage' / file_name
        elif 'golden_set_test_report' in file_name:
            # Golden set reports
            dest = self.dirs['golden_set'] / file_name
        elif file_name.endswith('.json') and 'analysis' in file_name:
            # Analysis JSON files
            dest = self.dirs['analysis'] / 'coverage' / file_name
        elif file_name.endswith('.md') and 'report' in file_name:
            # General reports
            dest = self.dirs['reports'] / 'daily' / file_name
        else:
            # Default to archives
            dest = self.dirs['archives'] / file_name
        
        # Move file
        try:
            shutil.move(str(file_path), str(dest))
            print(f"Moved {file_name} to {dest.relative_to(self.dist_root)}")
        except Exception as e:
            print(f"Error moving {file_name}: {e}")
    
    def _organize_directory(self, dir_path: Path):
        """Organize a directory based on its content."""
        dir_name = dir_path.name
        
        # Check if it's a test directory
        if any(test_name in dir_name for test_name in ['test-', 'golden-test-', 'debug-', 'consistency-']):
            # Move to archives with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"{dir_name}_{timestamp}"
            dest = self.dirs['archives'] / new_name
            try:
                shutil.move(str(dir_path), str(dest))
                print(f"Moved directory {dir_name} to {dest.relative_to(self.dist_root)}")
            except Exception as e:
                print(f"Error moving directory {dir_name}: {e}")
        else:
            # Move to appropriate location
            dest = self.dirs['archives'] / dir_name
            try:
                shutil.move(str(dir_path), str(dest))
                print(f"Moved directory {dir_name} to {dest.relative_to(self.dist_root)}")
            except Exception as e:
                print(f"Error moving directory {dir_name}: {e}")
    
    def create_topic_folder(self, topic_name: str, conversation_id: str) -> Path:
        """Create a topic-specific folder for organized output."""
        # Clean topic name for folder
        clean_topic = self._clean_topic_name(topic_name)
        
        # Create topic folder
        topic_folder = self.dirs['summaries'] / 'drafts' / clean_topic
        topic_folder.mkdir(exist_ok=True)
        
        # Create subfolders
        (topic_folder / 'conversation').mkdir(exist_ok=True)
        (topic_folder / 'summary').mkdir(exist_ok=True)
        (topic_folder / 'analysis').mkdir(exist_ok=True)
        
        return topic_folder
    
    def _clean_topic_name(self, topic_name: str) -> str:
        """Clean topic name for use as folder name."""
        # Remove special characters and replace with underscores
        import re
        clean = re.sub(r'[^\w\s-]', '', topic_name.lower())
        clean = re.sub(r'[-\s]+', '-', clean)
        clean = clean.strip('-')
        
        # Limit length
        if len(clean) > 50:
            clean = clean[:50].rstrip('-')
        
        return clean or 'untitled'
    
    def save_conversation_files(self, topic_folder: Path, conversation_id: str, 
                              conversation_data: Dict[str, Any], 
                              summary_data: Dict[str, Any],
                              analysis_data: Dict[str, Any]):
        """Save all files for a conversation in organized structure."""
        
        # Save conversation data
        conv_file = topic_folder / 'conversation' / f'{conversation_id}_conversation.json'
        with open(conv_file, 'w') as f:
            json.dump(conversation_data, f, indent=2)
        
        # Save summary data
        summary_file = topic_folder / 'summary' / f'{conversation_id}_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        # Save analysis data
        analysis_file = topic_folder / 'analysis' / f'{conversation_id}_analysis.json'
        with open(analysis_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        return {
            'conversation_file': conv_file,
            'summary_file': summary_file,
            'analysis_file': analysis_file
        }
    
    def generate_index(self) -> str:
        """Generate an index of all organized files."""
        index = {
            'generated_at': datetime.now().isoformat(),
            'structure': {},
            'files': {}
        }
        
        # Scan all directories
        for dir_name, dir_path in self.dirs.items():
            if dir_path.exists():
                index['structure'][dir_name] = {
                    'path': str(dir_path.relative_to(self.dist_root)),
                    'files': []
                }
                
                for file_path in dir_path.rglob('*'):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(self.dist_root)
                        file_info = {
                            'path': str(rel_path),
                            'size': file_path.stat().st_size,
                            'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        }
                        index['structure'][dir_name]['files'].append(file_info)
                        index['files'][str(rel_path)] = file_info
        
        # Save index
        index_file = self.dist_root / 'index.json'
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
        
        return str(index_file)
    
    def cleanup_old_files(self, days_old: int = 30):
        """Clean up old files from archives."""
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        for file_path in self.dirs['archives'].rglob('*'):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    print(f"Deleted old file: {file_path.name}")
                except Exception as e:
                    print(f"Error deleting {file_path.name}: {e}")


def organize_dist_directory(dist_root: str = "dist"):
    """Public interface for organizing dist directory."""
    organizer = DistOrganizer(dist_root)
    organizer.organize_existing_files()
    index_file = organizer.generate_index()
    print(f"Dist directory organized. Index saved to: {index_file}")


if __name__ == "__main__":
    organize_dist_directory()
