# MSVG Tools

**MSVG Tools** is an open-source collection of utilities for working with **MSVG** (Multi-Page-SVG) files — a format for combining multiple `<svg>` pages into a single structured document.

---

## 🖼 What is MSVG?

An **MSVG** file is an XML-based container format that can hold multiple SVG pages in a single file.

### Structure example:
```xml
<MSVG version="1.0">
  <pageSet>
    <Page>
      <!-- SVG page 1 -->
    </Page>
    <Page>
      <!-- SVG page 2 -->
    </Page>
    ...
  </pageSet>
</MSVG>
```

Each `<Page>` typically contains a complete <svg> element, including its own viewBox and style definitions.

The MSVG format is fully transparent — it’s just plain text XML. You can open it with any text editor to inspect or edit its contents. Because it doesn’t contain executable code, it’s safe by design and cannot carry malware.

---

#### MSVG is useful for:

-    Digital books made from multiple vector pages

-    Large diagrams split into pages

-    multi-page documents with vectors and raster layers 

---
	
## 📄 MSVG Viewer (Python)

A standalone desktop application for viewing `.msvg` files with multiple pages.  
Built with [pywebview](https://pywebview.flowrl.com/) for a browser-free, cross-platform experience.

### Features
- View **multi-page SVG documents** in a continuous scroll layout
- Zoom in/out with toolbar buttons or `Ctrl + Mouse Wheel`
- Preserves **vector quality** at all zoom levels
- Warns about missing `viewBox` attributes
- Supports both `.msvg` and single `.svg` files
	
	
---

## 🔄 SVG → MSVG Converter (Go)

A fast command-line tool that merges multiple `.svg` files into one `.msvg` file.

### Features
- Reads all `.svg` files from an `input_svgs/` folder
- Sorts them numerically (page1.svg, page2.svg, etc.)
- Strips XML headers
- Wraps each page in `<Page>` tags inside a `<pageSet>` container

---
	

## 📥 Downloads

You can get ready-to-use Windows executables for both the viewer and converter from the
Releases page.

Each release includes:

-    MSVG Viewer.exe (Python, built with PyInstaller)

-    svg2msvg.exe (Go, compiled binary)

-    Instructions
	
	
---
## 🛠 Building from Source

### MSVG Viewer (Python)

Requirements:
```
pip install pywebview
```
Run:
```
python msvg_viewer.py
```

Build executable:
```
pyinstaller --onefile --noconsole --name "MSVG Viewer" msvg_viewer.py
```


### Converter (Go)

Compile:
```
go build -o svg2msvg.exe main.go
```





