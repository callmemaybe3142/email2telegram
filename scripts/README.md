# Domain Management CLI

## Overview

Interactive command-line tool for managing email domains in the Email2Telegram service.

## Features

- ✅ **List all domains** - View all domains with status and expiry
- ✅ **Add new domain** - Register new email domains
- ✅ **Update domain** - Modify domain name or expiry date
- ✅ **Delete domain** - Remove domains from the system
- ✅ **Toggle status** - Activate/deactivate domains

## Usage

### Running the CLI

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run the domain manager
python scripts\manage_domains.py
```

### Main Menu

```
================================================================================
🌐 DOMAIN MANAGEMENT SYSTEM
================================================================================

1. List all domains
2. Add new domain
3. Update domain
4. Delete domain
5. Toggle domain status (active/inactive)
6. Exit

================================================================================
```

## Operations

### 1. List All Domains

Displays all domains with:
- Domain ID
- Domain name
- Status (Active/Inactive)
- Expiry date
- Creation date

**Example Output:**
```
================================================================================
📋 DOMAIN LIST
================================================================================

ID: 1
Domain: example.com
Status: ✅ Active
Expiry: 2025-12-31
Created: 2025-12-23 10:30:00
----------------------------------------

ID: 2
Domain: test.com
Status: ❌ Inactive
Expiry: No expiry
Created: 2025-12-23 11:00:00
----------------------------------------
```

### 2. Add New Domain

Prompts for:
- **Domain name** (required) - e.g., `example.com`
- **Expiry date** (optional) - Format: `YYYY-MM-DD`

**Example:**
```
📝 ADD NEW DOMAIN
Enter domain name (e.g., example.com): mydomain.com
Enter expiry date (YYYY-MM-DD) or press Enter to skip: 2025-12-31

✅ Domain 'mydomain.com' added successfully!
   ID: 3
```

**Validation:**
- Checks for duplicate domain names
- Validates date format
- Domain name cannot be empty

### 3. Update Domain

Allows updating:
- Domain name
- Expiry date

**Example:**
```
✏️ UPDATE DOMAIN
Enter domain ID to update: 1

Leave blank to keep current value
New domain name: newdomain.com
New expiry date (YYYY-MM-DD): 2026-01-01

✅ Domain 'newdomain.com' updated successfully!
```

**Notes:**
- Leave fields blank to keep current values
- Only specified fields are updated

### 4. Delete Domain

Permanently removes a domain from the database.

**Example:**
```
🗑️ DELETE DOMAIN
Enter domain ID to delete: 2
Are you sure you want to delete domain ID 2? (yes/no): yes

✅ Domain 'test.com' deleted successfully!
```

**Safety:**
- Requires confirmation (`yes`)
- Shows domain ID before deletion
- Cannot be undone

**Future Enhancement:**
- Check for associated user emails before deletion
- Prevent deletion if emails exist

### 5. Toggle Domain Status

Quickly activate or deactivate a domain.

**Example:**
```
🔄 TOGGLE DOMAIN STATUS
Enter domain ID to toggle: 1

✅ Domain 'example.com' deactivated!
```

**Use Cases:**
- Temporarily disable a domain
- Prevent new email creation on specific domains
- Manage domain availability

## Domain States

### Active Domain
- ✅ Users can create email addresses
- Shows in available domains list
- Fully functional

### Inactive Domain
- ❌ Users cannot create new emails
- Existing emails still receive messages
- Hidden from domain selection

## Database Schema

The CLI manages the `domains` table:

```sql
CREATE TABLE domains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain_name VARCHAR(255) UNIQUE NOT NULL,
    expiry_date DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Error Handling

The CLI handles:
- ✅ Invalid domain IDs
- ✅ Duplicate domain names
- ✅ Invalid date formats
- ✅ Database connection errors
- ✅ Keyboard interrupts (Ctrl+C)

## Best Practices

1. **Regular Backups**
   ```bash
   cp email2telegram.db email2telegram.db.backup
   ```

2. **Check Before Delete**
   - Always verify domain ID
   - Confirm deletion carefully

3. **Set Expiry Dates**
   - Track domain renewals
   - Prevent service disruption

4. **Use Inactive Instead of Delete**
   - Safer than deletion
   - Can be reactivated later

## Future Enhancements

- [ ] Bulk operations (add/update multiple domains)
- [ ] Import domains from CSV
- [ ] Export domain list
- [ ] Show email count per domain
- [ ] Prevent deletion if emails exist
- [ ] Domain expiry notifications
- [ ] Search/filter domains

## Troubleshooting

### Database Not Found
```
Error: no such table: domains
```
**Solution:** Run the main application first to initialize the database:
```bash
python main.py
```

### Permission Denied
```
Error: database is locked
```
**Solution:** Close the main application before using the CLI.

### Invalid Date Format
```
❌ Invalid date format. Use YYYY-MM-DD
```
**Solution:** Use the correct format: `2025-12-31`

## Integration with Main Application

The domain manager uses the same database as the main application:
- Changes are immediately reflected
- No restart required for main app
- Shared database connection pool

## Security Notes

- No authentication required (local tool)
- Direct database access
- Use only on trusted machines
- Consider adding admin password for production

## Example Workflow

### Setting Up Initial Domains

```bash
# 1. Run the CLI
python scripts\manage_domains.py

# 2. Add your first domain
Choose option: 2
Domain name: yourdomain.com
Expiry: 2025-12-31

# 3. Add more domains
Choose option: 2
Domain name: mail.yourdomain.com
Expiry: [Enter]

# 4. Verify
Choose option: 1
# See all domains listed

# 5. Exit
Choose option: 6
```

Now users can create email addresses on these domains!
