# Cursor Chat Context Storage & Summarization Guide

## Storage Locations

### Primary Storage Location

**Global Chat History & Summaries:**
```
~/Library/Application Support/Cursor/User/globalStorage/state.vscdb
```
- **Size:** ~2.1 GB (SQLite database)
- **Tables:** `ItemTable` and `cursorDiskKV`
- **Contains:** Chat history, summaries, and context

### Additional Storage Files

1. **DIPS (Database Indexed Persistent Storage):**
   ```
   ~/Library/Application Support/Cursor/DIPS
   ```
   - SQLite database for persistent indexing

2. **Workspace-Specific State Files:**
   ```
   ~/Library/Application Support/Cursor/User/workspaceStorage/<workspace-id>/state.vscdb
   ```
   - Separate state file per workspace

3. **Backup Files:**
   ```
   ~/Library/Application Support/Cursor/User/globalStorage/state.vscdb.backup
   ```
   - Automatic backups of state database

## How to Access Your Summaries

### Option 1: Query SQLite Database
```bash
# Open the database
sqlite3 ~/Library/Application\ Support/Cursor/User/globalStorage/state.vscdb

# Show tables
.tables

# Search for chat/summary entries
SELECT * FROM ItemTable WHERE key LIKE '%summary%' OR key LIKE '%chat%';
```

### Option 2: Check File Size
```bash
# Shows the size of state database (larger = more chat history)
ls -lh ~/Library/Application\ Support/Cursor/User/globalStorage/state.vscdb
```

### Option 3: Find Backup Files
```bash
# Find all backup files
find ~/Library/Application\ Support/Cursor -name "*.backup" -type f
```

## Important Notes

- Databases are SQLite format and can be opened with `sqlite3`
- Files are automatically managed by Cursor
- Backups are created automatically
- Workspace-specific summaries are in respective `workspaceStorage` folders

---

## Frequently Asked Questions

### Q1: After chat is summarized, is it automatically brought into a new chat or manually?

**Answer:** 
- **Automatically**: Cursor automatically includes summarized context from previous chats when starting a new conversation in the same workspace
- The summarization happens automatically when the conversation gets too long (typically after reaching token limits)
- You don't need to manually bring it in - Cursor handles this transparently
- The summary is used to maintain context across new chat sessions

### Q2: Are all chat histories summarized in one SQL database or elsewhere?

**Answer:**
- **Yes, primarily in one database**: All chat histories and summaries are stored in the main `state.vscdb` file located at:
  ```
  ~/Library/Application Support/Cursor/User/globalStorage/state.vscdb
  ```
- **Additional storage**: Workspace-specific data may also be stored in:
  ```
  ~/Library/Application Support/Cursor/User/workspaceStorage/<workspace-id>/state.vscdb
  ```
- **Format**: All stored as SQLite databases
- **Structure**: 
  - Global storage = All chats across all workspaces
  - Workspace storage = Workspace-specific chat context

## How Cursor's Summarization Works

1. **Automatic Summarization**: When a conversation exceeds token limits, Cursor automatically creates a summary
2. **Context Preservation**: The summary preserves key information, decisions, and code changes
3. **Seamless Integration**: New chats automatically include the summary as context
4. **Workspace Awareness**: Summaries are workspace-aware - each workspace maintains its own context

## Technical Details

- **Database Type**: SQLite 3.x
- **Storage Format**: Key-value pairs in `ItemTable` and `cursorDiskKV` tables
- **Backup Strategy**: Automatic backups created (`.backup` files)
- **Size Management**: Database grows with chat history (currently ~2.1 GB)

---

**Last Updated:** January 25, 2025
**Cursor Version:** 2.3 (as of file inspection)
