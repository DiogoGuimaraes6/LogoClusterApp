- [x] Run the app locally
- [x] Modify app to use port 5001
 
## Plan for Rebuilding Frontend/Backend

### Background and Motivation
The current application is a Flask-based logo clustering app that allows users to browse, compare, and export similar logos. The app uses precomputed similarity data stored in JSON files. The goal is to enhance the user experience by dynamically loading logos based on the selected letter. When a user clicks on a letter (e.g., "A"), the app should load the corresponding similarity JSON file (e.g., `block4_similarities_pngs_A_inkscape_512.json`), parse it to identify the logos mentioned, and display those logos in a grid from the appropriate directory (e.g., `pngs_ALL_inkscape_512/pngs_A_inkscape_512`).

### Key Challenges and Analysis
- **Dynamic Loading**: The app needs to dynamically load JSON files and images based on user interaction.
- **File Path Management**: Ensuring the correct file paths are used for loading JSON and image files.
- **User Interface Updates**: Updating the UI to reflect the selected logos in the grid.
- **Error Handling**: Managing potential errors, such as missing files or invalid JSON data.

### High-level Task Breakdown
1. **Backend Changes**:
   - Modify the Flask backend to handle requests for loading similarity JSON files based on the selected letter.
   - Implement a function to parse the JSON file and extract the list of logos.
   - Ensure the backend can serve the correct image files from the specified directory.

2. **Frontend Changes**:
   - Update the frontend to send requests to the backend when a letter is clicked.
   - Implement logic to display the logos in the grid based on the response from the backend.
   - Ensure the UI updates dynamically to reflect the selected logos.

3. **Testing**:
   - Write tests to ensure the backend correctly loads and parses the JSON files.
   - Test the frontend to verify that logos are displayed correctly in the grid.

4. **Documentation**:
   - Update documentation to reflect the new functionality and any changes in the codebase.

### Project Status Board
- [ ] Backend Changes
- [ ] Frontend Changes
- [ ] Testing
- [ ] Documentation

### Executor's Feedback or Assistance Requests
- Awaiting confirmation to proceed with the implementation of the backend changes.

### Lessons
- Ensure to handle file paths correctly to avoid errors when loading JSON and image files.

Executor's Feedback or Assistance Requests:
- The app is now running successfully on port 5001. You can access it at http://127.0.0.1:5001.

# Logo Cluster App - Right-Click Context Menu Feature

## Background and Motivation
The Logo Cluster App currently allows users to click on logos to view similar logos in a grid. However, there's no way to quickly switch the main logo while viewing similar logos. Adding a right-click context menu with a "Show Similar Logos" option would improve the user experience by allowing users to quickly pivot their search without going back to the main grid.

## Key Challenges and Analysis
1. The current implementation uses a grid-based view that's already set up to show similar logos
2. We need to add a context menu without modifying the existing grid functionality
3. The similar logos API endpoint already exists and works with any logo as input
4. We need to ensure the context menu appears in the correct position relative to the clicked logo

## High-level Task Breakdown

1. Add Context Menu HTML/CSS
   - Create a hidden context menu div in the HTML
   - Style it to appear on right-click
   - Position it at the cursor location
   - Add "Show Similar Logos" option

2. Add Context Menu JavaScript
   - Add right-click event listener to logo items
   - Prevent default context menu
   - Show custom context menu at click position
   - Handle "Show Similar Logos" click

3. Implement Logo Switching Logic
   - Reuse existing similar logos API call
   - Update the grid with new similar logos
   - Maintain current view state (grid vs comparison)

## Project Status Board
- [x] Add context menu HTML/CSS
- [x] Add context menu JavaScript
- [x] Implement logo switching logic
- [ ] Test the feature
- [ ] Verify no regressions in existing functionality

## Executor's Feedback or Assistance Requests
The implementation is complete and ready for testing. The context menu will appear when right-clicking any logo in both the main grid and comparison views. When "Show Similar Logos" is clicked, it will:
1. In the main grid view: Update the grid to show similar logos to the right-clicked logo
2. In the comparison view: Switch the main logo and update the similar logos accordingly

## Lessons
1. The implementation reuses existing functionality (similar logos API and grid rendering) to maintain consistency
2. The context menu is positioned using pageX/pageY to ensure it appears at the cursor location
3. The menu is hidden when clicking outside to maintain a clean user interface 

# Project Reorganization Plan

## Current Issues
1. Too many files in root directory
2. Temporary files mixed with core files
3. No clear separation between data, code, and utilities
4. Missing proper documentation
5. Development scripts included in deployment

## Proposed Structure
```
LogoClusterApp/
├── app/                    # Main application code
│   ├── __init__.py
│   ├── routes.py          # Flask routes
│   ├── static/            # Static files (CSS, JS)
│   └── templates/         # HTML templates
├── data/                  # Data files
│   ├── similarities/      # Similarity JSON files
│   └── logos/            # Logo images
├── tests/                # Test files
├── docs/                 # Documentation
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
├── Procfile             # Deployment configuration
└── .gitignore          # Git ignore file
```

## Action Items
1. Create new directory structure
2. Move files to appropriate locations
3. Update import paths in code
4. Create proper documentation
5. Add requirements.txt
6. Clean up temporary files
7. Remove development-only scripts

## Files to Delete
- .DS_Store
- __pycache__/
- dedup_out.txt
- missing_images_report.txt
- block4_head.txt
- non_ascii_json.txt
- non_ascii_filenames.txt
- missing_images.txt
- github_image_list.txt
- local_image_list.txt
- deduplicate_logos.py (development only)
- remove_duplicates.py (development only)
- ssim_storage.py (development only)

## Next Steps
1. Create new directory structure
2. Move core application files
3. Move data files
4. Clean up temporary files
5. Remove development scripts
6. Update code to reflect new structure
7. Add documentation

Would you like me to proceed with implementing this reorganization plan? 