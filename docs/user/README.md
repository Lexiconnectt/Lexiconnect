# Lexiconnect User Guide

Welcome to Lexiconnect! This guide will help you get started with using Lexiconnect for linguistic documentation and research.

## Table of Contents

- [What is Lexiconnect?](#what-is-lexiconnect)
- [Getting Started](#getting-started)
- [Features](#features)
- [Using Lexiconnect](#using-lexiconnect)
  - [Uploading FLEx Files](#uploading-flex-files)
  - [Visualizing Linguistic Data](#visualizing-linguistic-data)
  - [Exporting Data](#exporting-data)
- [FAQs](#faqs)
- [Troubleshooting](#troubleshooting)

## What is Lexiconnect?

Lexiconnect is a web-based tool designed for linguistic researchers working with endangered and minority languages. It helps you:

- **Import** linguistic data from FLEx (FieldWorks Language Explorer) text files
- **Visualize** relationships between words, morphemes, and linguistic structures
- **Explore** your data through interactive graph visualizations
- **Export** your data in various formats for further analysis

Lexiconnect uses a graph database to store and represent linguistic relationships, making it easy to explore connections between different linguistic elements.

## Getting Started

### Accessing Lexiconnect

1. Open your web browser and navigate to the Lexiconnect application URL
2. You should see the main visualization page with a search interface

### First Steps

1. **Upload your first file**: Navigate to the Upload page to import a FLEx text file
2. **Explore the graph**: Use the search feature to find words or morphemes and visualize their relationships
3. **View details**: Click on nodes in the graph to see detailed information

## Features

### 📤 File Upload
- Upload FLEx text files (`.flextext` format)
- Automatic parsing and validation
- Support for complex linguistic structures

### 📊 Interactive Graph Visualization
- Visualize relationships between words, morphemes, phrases, and sections
- Interactive exploration with zoom, pan, and node selection
- Color-coded nodes by type (words, morphemes, etc.)

### 🔍 Search Functionality
- Search for words or morphemes
- Filter visualization by search terms
- View connections and relationships

### 📥 Data Export
- Export your data in FLEXText XML format
- Maintain round-trip compatibility with FLEx
- Download files for backup or further analysis

### 📈 Statistics Dashboard
- View database statistics
- See counts of texts, words, morphemes, and more
- Monitor your corpus size

## Using Lexiconnect

### Uploading FLEx Files

1. **Navigate to Upload Page**
   - Click on "Upload" in the navigation menu or go to `/upload`

2. **Select Your File**
   - Click the upload area or drag and drop your `.flextext` file
   - Supported format: FLEx Text XML files

3. **Wait for Processing**
   - The file will be automatically parsed and validated
   - You'll see a success message when processing is complete
   - Statistics about your uploaded file will be displayed

4. **What Gets Imported**
   - Text metadata (title, source, language)
   - Sections and paragraphs
   - Phrases with their surface text
   - Words with glosses and part-of-speech tags
   - Morphemes with their types (stem, prefix, suffix, etc.)
   - Linguistic relationships and connections

**Note**: Make sure your FLEx file follows the standard FLEXText XML format. Files with syntax errors may fail to upload.

### Visualizing Linguistic Data

#### Main Visualization Page

The main page provides an interactive graph visualization of your linguistic data.

1. **Search Bar**
   - Enter a word or morpheme to search
   - Select whether to search for "Word" or "Morpheme"
   - Click "Visualize" to see the graph centered on your search term

2. **Graph Interaction**
   - **Pan**: Click and drag to move around the graph
   - **Zoom**: Use your mouse wheel or trackpad to zoom in/out
   - **Select Nodes**: Click on any node to see detailed information
   - **Clear Search**: Click "Clear" to reset the visualization

3. **Node Types and Colors**
   - Different node types are color-coded for easy identification
   - Hover over nodes to see basic information
   - Click nodes to view full details in the side panel

4. **Node Details Panel**
   - When you click a node, detailed information appears in the right sidebar
   - View properties like ID, surface form, gloss, language, etc.
   - See relationships and connections

#### Understanding the Graph

- **Nodes** represent linguistic units (words, morphemes, phrases, etc.)
- **Edges** (lines) represent relationships between units
- The graph shows how linguistic elements are connected
- You can explore morphological relationships, phrase structures, and more

### Exporting Data

1. **Access Export Feature**
   - From the graph visualization, click the "Export" button
   - Select the file type (currently FLEXText format)

2. **Download Your Data**
   - The export will generate a FLEXText XML file
   - The file will automatically download to your computer
   - The filename will be based on the text ID

3. **Export Format**
   - Exported files maintain compatibility with FLEx
   - All linguistic data, relationships, and metadata are preserved
   - You can re-import exported files if needed

**Note**: Export is currently available for individual texts. Select the text you want to export before clicking the export button.

## FAQs

### What file formats are supported?

Currently, Lexiconnect supports FLEx Text XML files (`.flextext` format). This is the standard format used by FieldWorks Language Explorer.

### Can I edit data after uploading?

Currently, Lexiconnect focuses on visualization and export. For editing, you may need to use FLEx or other tools, then re-upload the modified file.

### How much data can I upload?

The system can handle files of various sizes. Very large files may take longer to process. If you encounter issues, try splitting large files into smaller sections.

### Can I export data in other formats?

Currently, FLEXText XML export is supported. Additional export formats may be added in future versions.

### Is my data secure?

Data security depends on your deployment configuration. For production use, ensure proper authentication and access controls are in place.

### Can I collaborate with others?

User permissions and collaboration features depend on your deployment. Check with your system administrator about multi-user access.

## Troubleshooting

### Upload Issues

**Problem**: File upload fails
- **Solution**: Check that your file is a valid FLEXText XML file
- Verify the file isn't corrupted
- Check file size (very large files may timeout)

**Problem**: Upload succeeds but data doesn't appear
- **Solution**: Refresh the page
- Check the search functionality to see if data is actually in the database
- Review the upload statistics to confirm what was imported

### Visualization Issues

**Problem**: Graph doesn't show anything
- **Solution**: Try searching for a specific word or morpheme
- Check that you have data uploaded
- Clear your browser cache and refresh

**Problem**: Graph is too cluttered
- **Solution**: Use the search feature to focus on specific words/morphemes
- Zoom in to see details
- The graph automatically filters based on your search

**Problem**: Can't interact with the graph
- **Solution**: Make sure JavaScript is enabled in your browser
- Try a different browser (Chrome, Firefox, Edge)
- Check browser console for errors

### Export Issues

**Problem**: Export button doesn't work
- **Solution**: Make sure you have a text selected
- Check browser console for errors
- Verify you have data in the database

**Problem**: Exported file is empty or corrupted
- **Solution**: Check that the text has data
- Try exporting a different text
- Contact support if the issue persists

### General Issues

**Problem**: Page won't load
- **Solution**: Check your internet connection
- Verify the application URL is correct
- Try clearing browser cache

**Problem**: Slow performance
- **Solution**: Large datasets may take time to render
- Try using search to filter the visualization
- Check your browser's performance settings

## Getting Help

If you encounter issues not covered in this guide:

1. Check the [Developer Documentation](../developer/README.md) for technical details
2. Review error messages in your browser's developer console
3. Contact your system administrator or the development team
4. Check the project's issue tracker (if available)

## Additional Resources

- [FLEx Documentation](https://software.sil.org/fieldworks/) - Learn more about FLEx file formats
- [FLEXText Format](https://software.sil.org/fieldworks/flextext/) - Understanding FLEXText XML structure
- [Developer Documentation](../developer/README.md) - Technical details for developers
- [Documentation Index](../README.md) - Overview of all documentation

---

**Last Updated**: This documentation is maintained as part of the Lexiconnect project. For the most current information, refer to the project repository.

