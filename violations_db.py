"""
Violations Database Manager
Stores violation records with screenshots for monitoring logs
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
import json

class ViolationsDB:
    """Database manager for violation logs"""
    
    def __init__(self, db_path="violations.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with violations table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                violation_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT,
                image_path TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✓ Violations database initialized: {self.db_path}")
    
    def add_violation(self, 
                     violation_type: str,
                     severity: str,
                     description: str,
                     image_path: Optional[str] = None,
                     metadata: Optional[Dict] = None) -> int:
        """
        Add a new violation record
        
        Args:
            violation_type: Type of violation (NO_PERSON, PHONE, MULTIPLE_PEOPLE, etc.)
            severity: CRITICAL, WARNING, INFO
            description: Human-readable description
            image_path: Path to saved screenshot
            metadata: Additional data (JSON serializable)
        
        Returns:
            violation_id: ID of inserted record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute('''
            INSERT INTO violations 
            (timestamp, violation_type, severity, description, image_path, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, violation_type, severity, description, image_path, metadata_json))
        
        violation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return violation_id
    
    def get_all_violations(self, severity_filter: Optional[str] = None,
                          limit: Optional[int] = None) -> List[Dict]:
        """
        Get all violations, optionally filtered by severity
        
        Args:
            severity_filter: Filter by severity (CRITICAL, WARNING, INFO)
            limit: Maximum number of records to return
        
        Returns:
            List of violation dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        
        query = "SELECT * FROM violations"
        params = []
        
        if severity_filter:
            query += " WHERE severity = ?"
            params.append(severity_filter)
        
        query += " ORDER BY created_at DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        violations = []
        for row in rows:
            violation = dict(row)
            # Parse metadata JSON if exists
            if violation['metadata']:
                try:
                    violation['metadata'] = json.loads(violation['metadata'])
                except:
                    violation['metadata'] = {}
            violations.append(violation)
        
        conn.close()
        return violations
    
    def get_critical_violations(self, limit: Optional[int] = None) -> List[Dict]:
        """Get only CRITICAL violations"""
        return self.get_all_violations(severity_filter='CRITICAL', limit=limit)
    
    def get_violation_by_id(self, violation_id: int) -> Optional[Dict]:
        """Get a specific violation by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM violations WHERE id = ?", (violation_id,))
        row = cursor.fetchone()
        
        if row:
            violation = dict(row)
            if violation['metadata']:
                try:
                    violation['metadata'] = json.loads(violation['metadata'])
                except:
                    violation['metadata'] = {}
            conn.close()
            return violation
        
        conn.close()
        return None
    
    def delete_violation(self, violation_id: int) -> bool:
        """Delete a violation record and its image"""
        violation = self.get_violation_by_id(violation_id)
        
        if violation and violation['image_path']:
            # Delete image file
            try:
                if os.path.exists(violation['image_path']):
                    os.remove(violation['image_path'])
            except Exception as e:
                print(f"Error deleting image: {e}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM violations WHERE id = ?", (violation_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def clear_old_violations(self, days: int = 30):
        """Delete violations older than specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get old violations to delete their images
        cursor.execute('''
            SELECT image_path FROM violations 
            WHERE created_at < datetime('now', '-' || ? || ' days')
        ''', (days,))
        
        old_images = cursor.fetchall()
        
        # Delete image files
        for (image_path,) in old_images:
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Error deleting old image: {e}")
        
        # Delete database records
        cursor.execute('''
            DELETE FROM violations 
            WHERE created_at < datetime('now', '-' || ? || ' days')
        ''', (days,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def get_statistics(self) -> Dict:
        """Get violation statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total violations
        cursor.execute("SELECT COUNT(*) FROM violations")
        stats['total'] = cursor.fetchone()[0]
        
        # By severity
        cursor.execute("""
            SELECT severity, COUNT(*) as count 
            FROM violations 
            GROUP BY severity
        """)
        stats['by_severity'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # By type
        cursor.execute("""
            SELECT violation_type, COUNT(*) as count 
            FROM violations 
            GROUP BY violation_type 
            ORDER BY count DESC 
            LIMIT 10
        """)
        stats['by_type'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Recent (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) FROM violations 
            WHERE created_at > datetime('now', '-1 day')
        """)
        stats['last_24h'] = cursor.fetchone()[0]
        
        conn.close()
        return stats


# Global instance
_violations_db = None

def get_violations_db() -> ViolationsDB:
    """Get or create violations database instance"""
    global _violations_db
    if _violations_db is None:
        _violations_db = ViolationsDB()
    return _violations_db


# Test
if __name__ == '__main__':
    print("Testing Violations Database...")
    
    db = ViolationsDB("test_violations.db")
    
    # Add test violations
    print("\n1. Adding test violations...")
    vid1 = db.add_violation(
        violation_type="NO_PERSON",
        severity="CRITICAL",
        description="No person detected in frame for 3+ seconds",
        image_path="static/violations/test1.jpg",
        metadata={"duration": 3.5, "confidence": 0.95}
    )
    print(f"   Added violation ID: {vid1}")
    
    vid2 = db.add_violation(
        violation_type="PHONE_DETECTED",
        severity="CRITICAL",
        description="Mobile phone detected in video frame",
        image_path="static/violations/test2.jpg"
    )
    print(f"   Added violation ID: {vid2}")
    
    vid3 = db.add_violation(
        violation_type="HEAD_DOWN",
        severity="WARNING",
        description="Head looking down for extended period"
    )
    print(f"   Added violation ID: {vid3}")
    
    # Get all violations
    print("\n2. Getting all violations...")
    all_viols = db.get_all_violations()
    print(f"   Found {len(all_viols)} violations")
    
    # Get critical only
    print("\n3. Getting CRITICAL violations...")
    critical = db.get_critical_violations()
    print(f"   Found {len(critical)} critical violations:")
    for v in critical:
        print(f"   - {v['violation_type']}: {v['description']}")
    
    # Statistics
    print("\n4. Getting statistics...")
    stats = db.get_statistics()
    print(f"   Total: {stats['total']}")
    print(f"   By severity: {stats['by_severity']}")
    print(f"   By type: {stats['by_type']}")
    
    print("\n✓ Database test complete!")
