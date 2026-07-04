const fs = require('fs');
const path = require('path');

// Configuration
const vaultPath = path.resolve(__dirname);
const dropBoxPath = path.join(vaultPath, 'Dropbox');
const needsActionPath = path.join(vaultPath, 'Needs_Action');

// Ensure directories exist
[dropBoxPath, needsActionPath].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    console.log(`Created directory: ${dir}`);
  }
});

// Track processed files to avoid duplicates
const processedFiles = new Set();

// Function to create markdown metadata file
function createMetadataFile(sourceFile) {
  const fileName = path.basename(sourceFile);
  const destFile = path.join(needsActionPath, `FILE_${fileName}.md`);

  const stats = fs.statSync(sourceFile);
  const processedTime = new Date().toISOString();

  const content = `---
type: file_drop
original_name: ${fileName}
size: ${stats.size}
processed: ${processedTime}
---

New file dropped for processing.

Original file: ${fileName}
File size: ${stats.size} bytes
Detected at: ${processedTime}

## Suggested Actions
- [ ] Review file contents
- [ ] Determine appropriate action
- [ ] File or process accordingly
`;

  fs.writeFileSync(destFile, content, 'utf8');
  console.log(`Created metadata file: ${destFile}`);
}

// Function to process a new file
function processNewFile(filePath) {
  try {
    // Wait a bit to ensure file is completely written
    setTimeout(() => {
      if (fs.existsSync(filePath)) {
        const destFile = path.join(needsActionPath, `FILE_${path.basename(filePath)}`);
        fs.copyFileSync(filePath, destFile);
        createMetadataFile(filePath);
        console.log(`Processed file: ${filePath}`);
      }
    }, 1000);
  } catch (error) {
    console.error(`Error processing file ${filePath}:`, error);
  }
}

// Watch for new files in the Dropbox folder
console.log(`Starting file system watcher...`);
console.log(`Watching: ${dropBoxPath}`);

fs.watch(dropBoxPath, (eventType, filename) => {
  if (eventType === 'rename' && filename) {
    const filePath = path.join(dropBoxPath, filename);

    // Check if it's a new file (not a directory) and we haven't processed it
    if (!processedFiles.has(filename) && fs.existsSync(filePath)) {
      try {
        const stats = fs.statSync(filePath);
        if (stats.isFile()) {
          processedFiles.add(filename);
          processNewFile(filePath);
        }
      } catch (error) {
        // Ignore errors (file might have been deleted quickly)
      }
    }
  }
});

console.log('File system watcher is running. Press Ctrl+C to stop.');