# Image Placeholder Fix Instructions

## Issue
The blog feature requires actual image files but currently has empty placeholder files, which may cause display issues in browsers.

## Quick Fix
Replace the empty placeholder files with actual images:

1. **default-post.jpg** (800x400px)
   - Generic, professional blog post header
   - Suitable for any topic
   - High quality, web-optimized JPG

2. **ai-wellness-hero.jpg** (800x400px)
   - AI and wellness themed image
   - Modern, tech-focused design
   - Used for the main blog post about AI in wellness

3. **meditation-science.jpg** (800x400px)
   - Scientific research theme with meditation elements
   - Used for the mindfulness science blog post

## Alternative Solutions

### Option 1: Use stock photos
- Download royalty-free images from Unsplash, Pexels, or similar
- Ensure they're 800x400px (2:1 aspect ratio)
- Save as JPG format

### Option 2: Create simple colored placeholders
```bash
# Create solid color placeholders using ImageMagick (if installed)
convert -size 800x400 xc:#4A90E2 default-post.jpg
convert -size 800x400 xc:#7ED321 ai-wellness-hero.jpg
convert -size 800x400 xc:#BD10E0 meditation-science.jpg
```

### Option 3: Use CSS-based placeholders
Modify the templates to show a CSS-styled div when images fail to load instead of broken image icons.

## Current Status
- ✅ Static URL paths fixed (no more `/blog/blog/` duplication)
- ✅ Empty placeholder files created (stops 404 errors)
- ⚠️ Images need to be replaced with actual content

## Testing
After replacing images, test the blog at:
- `/blog` - Main blog page
- `/blog/post/ai-transforming-wellness-2025` - Individual post

The images should now load correctly without 404 errors.
