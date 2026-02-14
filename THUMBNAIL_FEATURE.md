# Project Thumbnail Feature Implementation

## Overview
Added the ability for users to upload and display thumbnail images for each project in the portfolio UI.

## Features Implemented

### 1. Backend API Endpoints

#### POST `/api/portfolio/project/thumbnail`
- **Purpose**: Upload a thumbnail image for a specific project
- **Parameters**:
  - `project_id` (form field): The project signature/ID
  - `image` (file): The image file to upload
- **Validation**:
  - Checks that uploaded file is an image
  - Stores image in `app/data/thumbnails/` directory
  - Updates database with thumbnail path
  - Removes old thumbnail if one exists
- **Response**: Returns success status, thumbnail path, and thumbnail URL

#### GET `/api/portfolio/project/thumbnail/{project_id}`
- **Purpose**: Retrieve and serve the thumbnail image for a project
- **Parameters**:
  - `project_id` (path): The project signature/ID
- **Response**: Returns the image file directly
- **Error Handling**: Returns 404 if thumbnail not found

### 2. Backend Integration

#### Files Modified:
1. **`app/main.py`**
   - Imported and registered the thumbnail router
   - Added router with `/api` prefix

2. **`app/api/routes/post_thumbnail.py`**
   - Enhanced POST endpoint to use proper thumbnail directory
   - Added GET endpoint for serving thumbnails
   - Implemented proper file handling and cleanup

3. **`app/utils/generate_portfolio.py`**
   - Modified `build_portfolio_model()` function
   - Added thumbnail URL to project data
   - Checks database for thumbnail_path and includes URL in response

### 3. Frontend Implementation

#### Files Modified:
1. **`app/static/portfolio.js`**
   
   **Added `uploadThumbnail()` method**:
   - Creates a hidden file input for image selection
   - Validates file type (must be image)
   - Validates file size (max 5MB)
   - Uploads thumbnail using FormData
   - Refreshes portfolio to display new thumbnail
   
   **Enhanced `renderTopProjects()` method**:
   - Added thumbnail display section to project cards
   - Shows existing thumbnail with "Change" button if available
   - Shows "Add Thumbnail" button if no thumbnail exists
   - Thumbnail images are styled with max dimensions and rounded corners

### 4. Database Schema
- **Existing column used**: `PROJECT.thumbnail_path` (TEXT)
- Stores relative path: `data/thumbnails/{project_id}.{ext}`

## User Experience

### Upload Flow:
1. User views portfolio dashboard at `http://localhost:8000/api/portfolio-dashboard`
2. Each project card shows either:
   - "📷 Add Thumbnail" button (if no thumbnail)
   - Existing thumbnail image with "Change" button overlay
3. Clicking either button opens file picker
4. User selects an image file (JPG, PNG, GIF, WebP, BMP)
5. Image is validated and uploaded
6. Portfolio refreshes to show the new thumbnail

### Display:
- Thumbnails are displayed prominently in each project card
- Images are automatically resized to fit (max 200px height)
- Rounded corners and border for professional appearance
- Responsive design maintains layout on different screen sizes

## Technical Details

### File Storage:
- **Directory**: `app/data/thumbnails/`
- **Naming**: `{project_id}.{extension}`
- **Supported formats**: JPG, JPEG, PNG, GIF, WebP, BMP
- **Size limit**: 5MB (enforced in frontend)

### API URLs:
- **Upload**: `POST /api/portfolio/project/thumbnail`
- **Retrieve**: `GET /api/portfolio/project/thumbnail/{project_id}`
- **Portfolio Dashboard**: `http://localhost:8000/api/portfolio-dashboard`

## Benefits

1. **Visual Enhancement**: Projects are more visually appealing with custom thumbnails
2. **Quick Recognition**: Users can quickly identify projects by their thumbnails
3. **Professional Presentation**: Portfolio looks more polished and complete
4. **Easy Management**: Simple upload/change workflow
5. **Responsive Design**: Works on desktop and mobile devices

## Testing

To test the feature:

```bash
# 1. Start the server (if not already running)
cd /Users/shreyasaxena/Desktop/Capstone/capstone-project-team-3
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000

# 2. Open the portfolio dashboard
# Navigate to: http://localhost:8000/api/portfolio-dashboard

# 3. Test upload:
# - Click "Add Thumbnail" on any project
# - Select an image file
# - Verify the image appears in the card

# 4. Test replacement:
# - Click "Change" on a project with existing thumbnail
# - Select a different image
# - Verify the new image replaces the old one

# 5. Test GET endpoint directly:
# Navigate to: http://localhost:8000/api/portfolio/project/thumbnail/{project_id}
```

## Error Handling

- **Invalid file type**: Frontend shows alert, rejects non-image files
- **File too large**: Frontend shows alert for files > 5MB
- **Project not found**: Backend returns proper error
- **Thumbnail not found**: Backend returns 404 with message
- **Upload failure**: Frontend shows error message, doesn't update UI

## Future Enhancements

Potential improvements:
1. Image preview before upload
2. Crop/resize functionality
3. Multiple images per project (gallery)
4. Drag-and-drop upload
5. Default placeholder thumbnails
6. Thumbnail optimization/compression
7. Cloud storage integration (S3, Azure Blob, etc.)

## Dependencies

No new dependencies required. Uses existing:
- FastAPI for file upload handling
- Standard Python pathlib and os for file operations
- Native browser File API for file selection
- FormData for multipart form upload
