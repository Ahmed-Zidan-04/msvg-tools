import webview
import tkinter as tk
from tkinter import filedialog
import os
import xml.etree.ElementTree as ET
import tempfile
import atexit
import re
import sys
import base64

# HTML for the initial landing page that accepts a button click
INITIAL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>MSVG Viewer</title>
  <style>
    body {
      margin: 0;
      font-family: sans-serif;
      background: #f0f0f0;
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
      align-items: center;
      justify-content: center;
      text-align: center;
    }
    h1 {
      font-size: 2.5rem;
    }
    p {
      font-size: 1.2rem;
      margin-top: 10px;
      color: #555;
    }
    button {
      padding: 10px 20px;
      font-size: 16px;
      cursor: pointer;
      border: 1px solid #ccc;
      border-radius: 5px;
      background: #fff;
      margin-top: 20px;
    }
  </style>
</head>
<body>
  <h1>MSVG Viewer</h1>
  <p>To view a file, please click the button below.</p>
  <button onclick="pywebview.api.load_file()">Open File</button>
</body>
</html>
"""

# HTML template for displaying the rendered content
VIEWER_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>MSVG Viewer</title>
  <style>
    body {
      margin: 0;
      font-family: sans-serif;
      background: #f0f0f0;
      display: flex;
      flex-direction: column;
      height: 100vh;
    }
    #toolbar {
      padding: 10px;
      background: #ddd;
      display: flex;
      align-items: center;
      gap: 10px;
      flex-shrink: 0;
    }
    #scrollArea {
      flex-grow: 1;
      overflow-y: auto;
    }
    #zoomContainer {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px;
        gap: 40px;
        transform-origin: top center;
    }
    .page-frame {
      border: 1px solid #ccc;
      background: white;
      display: block;
      box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
      border-bottom: 2px solid #aaa;
    }
    .warning-message {
      color: orange;
      font-weight: bold;
      margin-top: 5px;
      text-align: center;
    }
  </style>
</head>
<body>
  <div id="toolbar">
    <h1>MSVG Viewer</h1>
    <button id="zoomOutBtn">-</button>
    <button id="zoomInBtn">+</button>
  </div>
  <div id="scrollArea">
    <div id="zoomContainer">
      {{pages_html}}
    </div>
  </div>
  <script>
    let currentZoom = 1.0;
    let originalTotalHeight = 0;
    const zoomStep = 0.01;
    const minZoom = 0.2;
    const maxZoom = 3.0;

    const zoomContainer = document.getElementById('zoomContainer');
    const scrollArea = document.getElementById('scrollArea');

    function updateLayout() {
      // Update the zoom container's height and apply the transform
      zoomContainer.style.height = `${originalTotalHeight * currentZoom}px`;
      zoomContainer.style.transform = `scale(${currentZoom})`;
    }

    document.addEventListener('DOMContentLoaded', () => {
        const pages = document.querySelectorAll('.page-frame');
        let totalPagesHeight = 0;
        pages.forEach(page => {
            totalPagesHeight += page.clientHeight;
        });
        const numPages = pages.length;
        const totalGapsHeight = (numPages - 1) * 40;
        const totalPaddingHeight = 20 * 2;
        
        originalTotalHeight = totalPagesHeight + totalGapsHeight + totalPaddingHeight;
        
        updateLayout();
    });

    function handleZoom(direction) {
      const oldZoom = currentZoom;
      const oldScrollTop = scrollArea.scrollTop;
      const viewportHeight = scrollArea.clientHeight;
      const oldRelativeCenter = (oldScrollTop + viewportHeight / 2) / (originalTotalHeight * oldZoom);

      if (direction === 'in' && currentZoom < maxZoom) {
        currentZoom = Math.min(currentZoom + zoomStep, maxZoom);
      } else if (direction === 'out' && currentZoom > minZoom) {
        currentZoom = Math.max(currentZoom - zoomStep, minZoom);
      }
      
      updateLayout();
      
      const newScrollTop = (originalTotalHeight * currentZoom * oldRelativeCenter) - (viewportHeight / 2);
      scrollArea.scrollTop = newScrollTop;
    }

    document.getElementById('zoomInBtn').addEventListener('click', () => handleZoom('in'));
    document.getElementById('zoomOutBtn').addEventListener('click', () => handleZoom('out'));
    
    scrollArea.addEventListener('wheel', (event) => {
      if (event.ctrlKey) {
        event.preventDefault();
        const direction = Math.sign(event.deltaY) > 0 ? 'out' : 'in';
        handleZoom(direction);
      }
    }, { passive: false });
  </script>
</body>
</html>
"""

def parse_and_render(file_content):
    """Parses MSVG or single SVG content and generates HTML."""
    try:
        processed_content = re.sub(r'<\?xml.*\?>', '', file_content, flags=re.DOTALL)
        processed_content = re.sub(r'<!DOCTYPE.*?>', '', processed_content, flags=re.DOTALL)
        
        root = ET.fromstring(processed_content)

        pages_html = ""
        
        if root.find(".//image") is not None and "data:image" in ET.tostring(root, encoding='unicode'):
            return VIEWER_HTML_TEMPLATE.replace("{{pages_html}}", """
                <h1>Rendering Error:</h1>
                <p>This MSVG file contains an embedded raster image (like a JPG or PNG), which this viewer cannot render. Only vector graphics (paths and shapes) are supported.</p>
            """)

        page_nodes = root.findall(".//{*}Page")
        if not page_nodes and root.tag.endswith("svg"):
            page_nodes = [root]

        for idx, page_node in enumerate(page_nodes):
            svg_element = page_node if page_node.tag.endswith("svg") else page_node.find("{*}svg")
            if svg_element is None:
                continue

            view_box = svg_element.get("viewBox")
            
            page_width = 900
            page_height = 1000
            
            if view_box:
                parts = view_box.split()
                if len(parts) == 4:
                    vb_width = float(parts[2])
                    vb_height = float(parts[3])
                    if vb_height > 0:
                        page_height = page_width * (vb_height / vb_width)

            style = f"width: {page_width}px; height: {page_height}px;"
            warning_html = ""
            
            if view_box is None:
                warning_html = f'<div class="warning-message">Warning: No viewBox attribute found for Page {idx + 1}.</div>'

            svg_string = ET.tostring(svg_element, encoding='unicode')
            
            svg_bytes = svg_string.encode('utf-8')
            base64_bytes = base64.b64encode(svg_bytes)
            base64_string = base64_bytes.decode('utf-8')
            
            pages_html += f"""
                <div class="page-frame" style="{style}">
                    <img src="data:image/svg+xml;base64,{base64_string}" style="width:100%; height:100%; object-fit:contain;">
                </div>
                {warning_html}
            """
        
        if not pages_html:
            return VIEWER_HTML_TEMPLATE.replace("{{pages_html}}", "<h1>Could not find any renderable content in the file.</h1><p>Please ensure the file contains valid &lt;svg&gt; or &lt;Page&gt; tags.</p>")

        return VIEWER_HTML_TEMPLATE.replace("{{pages_html}}", pages_html)

    except ET.ParseError as e:
        return VIEWER_HTML_TEMPLATE.replace("{{pages_html}}", f"<h1>Error parsing file:</h1><p>The file is not a valid XML/SVG document. Error: {e}</p>")
    except Exception as e:
        return VIEWER_HTML_TEMPLATE.replace("{{pages_html}}", f"<h1>An unexpected error occurred:</h1><p>Error: {e}</p>")

class Api:
    def __init__(self):
        self.temp_file = None
        atexit.register(self.cleanup)

    def load_file(self):
        """Opens a file dialog and processes the selected file."""
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("MSVG Files", "*.msvg"), ("SVG Files", "*.svg")])
        root.destroy()

        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            html_content = parse_and_render(file_content)
            
            if self.temp_file and os.path.exists(self.temp_file):
                os.remove(self.temp_file)

            self.temp_file = tempfile.NamedTemporaryFile(suffix=".html", delete=False).name
            with open(self.temp_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            webview.windows[0].load_url(f"file:///{os.path.abspath(self.temp_file)}")
        except Exception as e:
            error_html = VIEWER_HTML_TEMPLATE.replace("{{pages_html}}", f"<h1>An error occurred:</h1><p>Could not read or process the file. Error: {e}</p>")
            if self.temp_file and os.path.exists(self.temp_file):
                os.remove(self.temp_file)
            self.temp_file = tempfile.NamedTemporaryFile(suffix=".html", delete=False).name
            with open(self.temp_file, "w", encoding="utf-8") as f:
                f.write(error_html)
            webview.windows[0].load_url(f"file:///{os.path.abspath(self.temp_file)}")

    def cleanup(self):
        if self.temp_file and os.path.exists(self.temp_file):
            os.remove(self.temp_file)

if __name__ == '__main__':
    api = Api()
    window = webview.create_window('MSVG Viewer', html=INITIAL_HTML, js_api=api)
    webview.start()