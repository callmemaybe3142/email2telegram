"""
Domain Management CLI
Interactive command-line tool for managing email domains
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import database module
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal, init_db, Domain


class DomainManager:
    """Domain CRUD operations manager"""
    
    def __init__(self):
        self.session: AsyncSession = None
    
    async def __aenter__(self):
        self.session = AsyncSessionLocal()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    async def list_domains(self):
        """List all domains"""
        result = await self.session.execute(select(Domain))
        domains = result.scalars().all()
        
        if not domains:
            print("\n📭 No domains found.")
            return
        
        print("\n" + "="*80)
        print("📋 DOMAIN LIST")
        print("="*80)
        
        for domain in domains:
            status = "✅ Active" if domain.is_active else "❌ Inactive"
            expiry = domain.expiry_date.strftime("%Y-%m-%d") if domain.expiry_date else "No expiry"
            
            print(f"\nID: {domain.id}")
            print(f"Domain: {domain.domain_name}")
            print(f"Status: {status}")
            print(f"Expiry: {expiry}")
            print(f"Created: {domain.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 40)
    
    async def add_domain(self, domain_name: str, expiry_date: str = None):
        """Add a new domain"""
        # Check if domain already exists
        result = await self.session.execute(
            select(Domain).where(Domain.domain_name == domain_name)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"\n❌ Domain '{domain_name}' already exists!")
            return False
        
        # Parse expiry date if provided
        expiry = None
        if expiry_date:
            try:
                expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
            except ValueError:
                print("\n❌ Invalid date format. Use YYYY-MM-DD")
                return False
        
        # Create new domain
        new_domain = Domain(
            domain_name=domain_name,
            expiry_date=expiry,
            is_active=True
        )
        
        self.session.add(new_domain)
        await self.session.commit()
        
        print(f"\n✅ Domain '{domain_name}' added successfully!")
        print(f"   ID: {new_domain.id}")
        return True
    
    async def update_domain(self, domain_id: int, **kwargs):
        """Update domain details"""
        result = await self.session.execute(
            select(Domain).where(Domain.id == domain_id)
        )
        domain = result.scalar_one_or_none()
        
        if not domain:
            print(f"\n❌ Domain with ID {domain_id} not found!")
            return False
        
        # Update fields
        if 'domain_name' in kwargs:
            domain.domain_name = kwargs['domain_name']
        
        if 'is_active' in kwargs:
            domain.is_active = kwargs['is_active']
        
        if 'expiry_date' in kwargs:
            if kwargs['expiry_date']:
                try:
                    domain.expiry_date = datetime.strptime(kwargs['expiry_date'], "%Y-%m-%d")
                except ValueError:
                    print("\n❌ Invalid date format. Use YYYY-MM-DD")
                    return False
            else:
                domain.expiry_date = None
        
        await self.session.commit()
        print(f"\n✅ Domain '{domain.domain_name}' updated successfully!")
        return True
    
    async def delete_domain(self, domain_id: int):
        """Delete a domain"""
        result = await self.session.execute(
            select(Domain).where(Domain.id == domain_id)
        )
        domain = result.scalar_one_or_none()
        
        if not domain:
            print(f"\n❌ Domain with ID {domain_id} not found!")
            return False
        
        # Check if domain has associated emails
        # TODO: Add check for associated emails once UserEmail queries are implemented
        
        domain_name = domain.domain_name
        await self.session.delete(domain)
        await self.session.commit()
        
        print(f"\n✅ Domain '{domain_name}' deleted successfully!")
        return True
    
    async def toggle_status(self, domain_id: int):
        """Toggle domain active status"""
        result = await self.session.execute(
            select(Domain).where(Domain.id == domain_id)
        )
        domain = result.scalar_one_or_none()
        
        if not domain:
            print(f"\n❌ Domain with ID {domain_id} not found!")
            return False
        
        domain.is_active = not domain.is_active
        await self.session.commit()
        
        status = "activated" if domain.is_active else "deactivated"
        print(f"\n✅ Domain '{domain.domain_name}' {status}!")
        return True


async def show_menu():
    """Display main menu"""
    print("\n" + "="*80)
    print("🌐 DOMAIN MANAGEMENT SYSTEM")
    print("="*80)
    print("\n1. List all domains")
    print("2. Add new domain")
    print("3. Update domain")
    print("4. Delete domain")
    print("5. Toggle domain status (active/inactive)")
    print("6. Exit")
    print("\n" + "="*80)


async def main():
    """Main CLI loop"""
    # Initialize database
    await init_db()
    
    print("\n✅ Database initialized")
    
    try:
        while True:
            await show_menu()
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            async with DomainManager() as dm:
                if choice == "1":
                    # List domains
                    await dm.list_domains()
                    input("\nPress Enter to continue...")
                
                elif choice == "2":
                    # Add domain
                    print("\n📝 ADD NEW DOMAIN")
                    domain_name = input("Enter domain name (e.g., example.com): ").strip()
                    
                    if not domain_name:
                        print("❌ Domain name cannot be empty!")
                        continue
                    
                    expiry = input("Enter expiry date (YYYY-MM-DD) or press Enter to skip: ").strip()
                    await dm.add_domain(domain_name, expiry if expiry else None)
                    input("\nPress Enter to continue...")
                
                elif choice == "3":
                    # Update domain
                    await dm.list_domains()
                    print("\n✏️ UPDATE DOMAIN")
                    
                    try:
                        domain_id = int(input("Enter domain ID to update: ").strip())
                    except ValueError:
                        print("❌ Invalid ID!")
                        continue
                    
                    print("\nLeave blank to keep current value")
                    new_name = input("New domain name: ").strip()
                    new_expiry = input("New expiry date (YYYY-MM-DD): ").strip()
                    
                    update_data = {}
                    if new_name:
                        update_data['domain_name'] = new_name
                    if new_expiry:
                        update_data['expiry_date'] = new_expiry
                    
                    if update_data:
                        await dm.update_domain(domain_id, **update_data)
                    else:
                        print("❌ No changes made")
                    
                    input("\nPress Enter to continue...")
                
                elif choice == "4":
                    # Delete domain
                    await dm.list_domains()
                    print("\n🗑️ DELETE DOMAIN")
                    
                    try:
                        domain_id = int(input("Enter domain ID to delete: ").strip())
                    except ValueError:
                        print("❌ Invalid ID!")
                        continue
                    
                    confirm = input(f"Are you sure you want to delete domain ID {domain_id}? (yes/no): ").strip().lower()
                    
                    if confirm == "yes":
                        await dm.delete_domain(domain_id)
                    else:
                        print("❌ Deletion cancelled")
                    
                    input("\nPress Enter to continue...")
                
                elif choice == "5":
                    # Toggle status
                    await dm.list_domains()
                    print("\n🔄 TOGGLE DOMAIN STATUS")
                    
                    try:
                        domain_id = int(input("Enter domain ID to toggle: ").strip())
                    except ValueError:
                        print("❌ Invalid ID!")
                        continue
                    
                    await dm.toggle_status(domain_id)
                    input("\nPress Enter to continue...")
                
                elif choice == "6":
                    # Exit
                    print("\n👋 Goodbye!")
                    break
                
                else:
                    print("\n❌ Invalid choice! Please enter 1-6")
                    input("\nPress Enter to continue...")
    finally:
        # Cleanup
        from database import engine
        await engine.dispose()



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Ensure clean exit
        import sys
        sys.exit(0)

