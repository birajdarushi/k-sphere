> [!NOTE]
> Refreshed on 2026-05-25 for clarity and consistency.
> Where applicable, frontend commands use `npm` (`npm install`, `npm run dev`, `npm run build`, `npm run lint`).

# Folder Grouping Feature

## Overview
The Knowledge Base now groups files by their directory path, making it much easier to manage large numbers of indexed files, especially from the System Indexer.

## Key Features

### 1. **Automatic Grouping by Path**
- Files are automatically grouped by their source directory
- System Indexer files are grouped by their original filesystem path
- Manually uploaded files are grouped under "Uploaded Files"

### 2. **Collapsible Folder View**
- Each folder shows:
  - Folder icon
  - Shortened path (e.g., `~/Documents/Projects` instead of `/Users/username/Documents/Projects`)
  - File count (e.g., "5 files")
  - Expand/collapse chevron icon
- Click the folder header to expand/collapse and see all files inside
- Click "View All" button to open a modal with all files in that folder

### 3. **File Management**
- All file actions work the same within folders:
  - Click file to preview
  - Open in new tab
  - Download
  - Delete
- Actions available in both:
  - Collapsed view (via "View All" modal)
  - Expanded view (inline file list)

### 4. **Smart Citations**
When the AI chat references indexed content:
- ✅ Cites individual files by name (e.g., "document.pdf")
- ✅ NOT the entire folder path
- ✅ Citations work exactly as before - no change needed

## User Experience

### Before (Flat List)
```
📄 project-file-1.js
📄 project-file-2.ts
📄 project-file-3.tsx
📄 another-project-file.js
📄 document.pdf
... (1000+ more files)
```

### After (Grouped by Folder)
```
📁 ~/Documents/Projects/MyApp/src
   5 files                    [View All] [>]
   
📁 ~/Documents/Research/Papers
   12 files                   [View All] [>]
   
📁 Uploaded Files
   3 files                    [View All] [>]
```

### Expanded Folder
```
📁 ~/Documents/Projects/MyApp/src
   5 files                    [View All] [v]
   
   📄 project-file-1.js       2.3 KB • 2025-10-06 • 5 chunks [Indexed]
   📄 project-file-2.ts       1.8 KB • 2025-10-06 • 3 chunks [Indexed]
   📄 project-file-3.tsx      4.1 KB • 2025-10-06 • 8 chunks [Indexed]
   ...
```

## Technical Implementation

### Frontend Changes (`app/knowledge-base/page.tsx`)
1. **Added imports**: `ChevronDown`, `ChevronRight`, `Folder` icons
2. **New state**:
   - `expandedFolders`: Set of expanded folder paths
   - `selectedFolder`: Currently selected folder for modal view
3. **Grouping logic**:
   ```typescript
   const groupedFiles = filteredFiles.reduce((acc, file) => {
     const pathParts = file.path?.split('/') || []
     let folderPath = 'Uploaded Files' // Default
     
     if (pathParts.length > 1) {
       const dirParts = pathParts.slice(0, -1)
       folderPath = dirParts.join('/')
     }
     
     if (!acc[folderPath]) acc[folderPath] = []
     acc[folderPath].push(file)
     return acc
   }, {})
   ```
4. **UI Components**:
   - Folder header with expand/collapse
   - Inline expanded file list
   - Modal dialog for "View All"

### Backend (No Changes Required)
- ✅ Already stores full file path in database
- ✅ Already stores filename only in vector metadata
- ✅ Citations already use `file_name` from metadata
- ✅ No API changes needed

## Benefits

1. **Reduced Visual Clutter**: 1000+ files become ~10-20 folder groups
2. **Better Organization**: Files grouped by logical directory structure
3. **Faster Navigation**: Find files by their source location
4. **Same Functionality**: All existing features work unchanged
5. **Smart Citations**: Chat still cites individual files, not folders

## Usage Tips

- **System Indexer files**: Automatically grouped by their original filesystem path
- **Uploaded files**: All grouped under "Uploaded Files"
- **Search**: Still searches across all files, but results are grouped
- **Expand folders**: Click folder header to see all files inline
- **View All modal**: Better for folders with many files (20+)

## Future Enhancements

Potential improvements:
- [ ] Custom folder names/aliases
- [ ] Drag-and-drop to reorganize folders
- [ ] Folder-level actions (delete all, export all)
- [ ] Search within specific folder
- [ ] Folder statistics (total size, file types)
---

_This document is part of the K-Sphere documentation set. If you find outdated steps, please open an issue or PR._
