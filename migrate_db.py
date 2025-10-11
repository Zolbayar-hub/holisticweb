#!/usr/bin/env python3
"""
Manual database migration script to add num_people column
"""

import sqlite3
import os

def add_num_people_column():
    """Add num_people column to booking table if it doesn't exist"""
    
    db_path = os.path.join('instance', 'data.sqlite')
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        print(f"📂 Connecting to database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current table structure
        print("📋 Current table structure:")
        cursor.execute('PRAGMA table_info(booking)')
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Add num_people column if it doesn't exist
        if 'num_people' not in column_names:
            print("\n🔧 Adding num_people column...")
            cursor.execute('ALTER TABLE booking ADD COLUMN num_people INTEGER DEFAULT 1 NOT NULL')
            conn.commit()
            print("✅ Successfully added num_people column")
            
            # Verify the column was added
            cursor.execute('PRAGMA table_info(booking)')
            new_columns = cursor.fetchall()
            print("\n📋 Updated table structure:")
            for col in new_columns:
                print(f"  - {col[1]} ({col[2]})")
                
        else:
            print("\n✅ num_people column already exists")
        
        # Update any existing bookings that have null num_people
        cursor.execute('UPDATE booking SET num_people = 1 WHERE num_people IS NULL')
        updated_count = cursor.rowcount
        if updated_count > 0:
            print(f"✅ Updated {updated_count} existing bookings to have num_people = 1")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("🗄️ Database Migration Script")
    print("=" * 40)
    
    success = add_num_people_column()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Start your Flask app")
        print("2. Go to http://localhost:5000/booking/debug/schema to verify")
        print("3. Test the booking functionality")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above and try again.")
