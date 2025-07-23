# 4Front 2 Market Logo Instructions

## Adding the Logo to PDF Reports

The PDF report generation has been updated to include the 4Front 2 Market logo. Here's how to add the actual logo:

### 1. Logo File Requirements
- **Format**: PNG (recommended) or JPG
- **Size**: Approximately 400x200 pixels (2:1 aspect ratio)
- **Location**: `static/images/4front2market_logo.png`

### 2. Logo Description
Based on the provided logo description:
- **Icon**: Golden-yellow bar chart with upward arrow
- **Text**: "4Front" in dark blue, "2Market" in teal
- **Style**: Clean, modern design with growth/progress theme

### 3. How to Add the Logo

1. **Save the logo file** as `4front2market_logo.png`
2. **Place it in the directory**: `static/images/`
3. **Ensure the file is readable** by the application

### 4. What's Included in Reports

The updated PDF reports now include:

#### Title Page:
- ✅ 4Front 2 Market AB branding
- ✅ Company logo (if available)
- ✅ "Beta Version Report" notice
- ✅ Contact: daniel.hesse@4front2market.se
- ✅ Beta version disclaimer
- ✅ Project information

#### Footer Page:
- ✅ Company ownership information
- ✅ Contact details
- ✅ Software version (Beta)
- ✅ Confidentiality notice
- ✅ Report generation date

### 5. Fallback Behavior

If the logo file is not found:
- The report will still generate successfully
- A warning will be logged
- All other branding elements will still be included

### 6. Testing

To test the logo integration:
1. Add the logo file to `static/images/4front2market_logo.png`
2. Generate a PDF report from any project
3. Check that the logo appears on the title page

### 7. Customization

The logo size and positioning can be adjusted in `services/pdf_service.py`:
- **Width**: `2*inch` (currently set)
- **Height**: `1*inch` (currently set)
- **Alignment**: `'CENTER'` (currently set)

## Current Implementation

The PDF service now automatically:
- ✅ Includes 4Front 2 Market AB branding
- ✅ Shows "Beta Version Report" prominently
- ✅ Displays contact information
- ✅ Includes beta version disclaimers
- ✅ Adds company ownership information
- ✅ Attempts to include the logo (if file exists) 