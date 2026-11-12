$ErrorActionPreference = "Stop"
try {
    Write-Host "Initializing PowerPoint COM..."
    $ppt = New-Object -ComObject PowerPoint.Application
    Write-Host "Opening presentation..."
    $deck = $ppt.Presentations.Open("D:\RR_PRESSURE_INDEX_2027\RR_PRESSURE_INDEX_2027_EXECUTIVE_PRESENTATION.pptx", 2, 0, 0)
    Write-Host "Saving as PDF..."
    $deck.SaveAs("D:\RR_PRESSURE_INDEX_2027\RR_PRESSURE_INDEX_2027_EXECUTIVE_PRESENTATION.pdf", 32)
    $deck.Close()
    $ppt.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
    Copy-Item "D:\RR_PRESSURE_INDEX_2027\RR_PRESSURE_INDEX_2027_EXECUTIVE_PRESENTATION.pdf" "D:\RR_PRESSURE_INDEX_2027\outputs\final_submission\executive_presentation_FINAL.pdf" -Force
    Write-Host "SUCCESS: Exported presentation to PDF via PowerPoint COM!"
} catch {
    Write-Host "PowerPoint COM Error: $($_.Exception.Message)"
}

