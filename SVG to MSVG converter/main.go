package main

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
)

func extractNumber(name string) int {
	re := regexp.MustCompile(`\d+`)
	matches := re.FindStringSubmatch(name)
	if len(matches) > 0 {
		var num int
		fmt.Sscanf(matches[0], "%d", &num)
		return num
	}
	return 0
}

func main() {
	inputDir := "input_svgs"
	outputFile := "output.msvg"

	files, err := os.ReadDir(inputDir)
	if err != nil {
		fmt.Println("Error reading input_svgs folder:", err)
		return
	}

	var svgFiles []string
	for _, f := range files {
		if !f.IsDir() && filepath.Ext(f.Name()) == ".svg" {
			svgFiles = append(svgFiles, f.Name())
		}
	}

	sort.Slice(svgFiles, func(i, j int) bool {
		return extractNumber(svgFiles[i]) < extractNumber(svgFiles[j])
	})

	// Open output file
	out, err := os.Create(outputFile)
	if err != nil {
		fmt.Println("Failed to create output.msvg:", err)
		return
	}
	defer out.Close()

	// Write header
	out.WriteString("<MSVG version=\"1.0\">\r\n\r\n<pageSet>\r\n")

	// Write pages
	for _, file := range svgFiles {
		content, err := os.ReadFile(filepath.Join(inputDir, file))
		if err != nil {
			fmt.Printf("Failed to read %s: %v\n", file, err)
			continue
		}

		// Strip XML header only
		xmlHeader := regexp.MustCompile(`(?i)<\?xml[^>]*\?>\s*`)
		cleaned := xmlHeader.ReplaceAll(content, nil)

		// Append page
		out.WriteString("\r\n<Page>\r\n\r\n")
		out.Write(cleaned)
		out.WriteString("\r\n\r\n</Page>\r\n")
	}

	// Write footer
	out.WriteString("\r\n</pageSet>\r\n\r\n</MSVG>\r\n")

	fmt.Println("✅ output.msvg written successfully.")
}
