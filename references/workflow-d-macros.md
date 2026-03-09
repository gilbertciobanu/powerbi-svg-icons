# Workflow D — VBA Macros

Both macros live in `factory/macro-seed.pptm` (standard Module). The folder picker and `%TEMP%` copy are required for OneDrive compatibility.

## `ExportIconAsSVG` — single-icon export

```vba
Sub ExportIconAsSVG()
    Dim fd As FileDialog
    Set fd = Application.FileDialog(msoFileDialogFolderPicker)
    fd.Title = "Select the factory folder"
    fd.InitialFileName = Environ("USERPROFILE") & "\"
    If fd.Show = False Then Exit Sub

    Dim factoryFolder As String
    factoryFolder = fd.SelectedItems(1)

    Dim fso As Object
    Set fso = CreateObject("Scripting.FileSystemObject")

    Dim pptxPath As String
    pptxPath = factoryFolder & "\working.pptx"
    If Not fso.FileExists(pptxPath) Then
        MsgBox "working.pptx not found at: " & pptxPath, vbExclamation
        Exit Sub
    End If

    Dim tempPath As String
    tempPath = Environ("TEMP") & "\wd_export.pptx"
    fso.CopyFile pptxPath, tempPath, True

    Dim pres As Presentation
    Set pres = Presentations.Open(tempPath, msoFalse, msoFalse, msoTrue)

    Dim outputPath As String
    outputPath = factoryFolder & "\output.svg"

    pres.Slides(1).Shapes(1).Export outputPath, ppShapeFormatSVG
    pres.Saved = True
    pres.Close
    fso.DeleteFile tempPath

    If fso.FileExists(outputPath) Then
        MsgBox "Done! output.svg saved to: " & factoryFolder, vbInformation
    Else
        MsgBox "Macro ran but output.svg not found.", vbExclamation
    End If
End Sub
```

## `ExportBatchSVGs` — batch export (one SVG per slide)

```vba
Sub ExportBatchSVGs()
    Dim fd As FileDialog
    Set fd = Application.FileDialog(msoFileDialogFolderPicker)
    fd.Title = "Select the factory folder"
    fd.InitialFileName = Environ("USERPROFILE") & "\"
    If fd.Show = False Then Exit Sub

    Dim factoryFolder As String
    factoryFolder = fd.SelectedItems(1)

    Dim fso As Object
    Set fso = CreateObject("Scripting.FileSystemObject")

    Dim pptxPath As String
    pptxPath = factoryFolder & "\working.pptx"
    If Not fso.FileExists(pptxPath) Then
        MsgBox "working.pptx not found at: " & pptxPath, vbExclamation
        Exit Sub
    End If

    ' Copy to %TEMP% to bypass OneDrive Protected View
    Dim tempPath As String
    tempPath = Environ("TEMP") & "\wd_export.pptx"
    fso.CopyFile pptxPath, tempPath, True

    Dim pres As Presentation
    Set pres = Presentations.Open(tempPath, msoFalse, msoFalse, msoTrue)

    Dim n As Long
    n = pres.Slides.Count
    Dim exported As Long
    exported = 0

    Dim i As Long
    For i = 1 To n
        If pres.Slides(i).Shapes.Count > 0 Then
            Dim outputPath As String
            outputPath = factoryFolder & "\output_" & i & ".svg"
            pres.Slides(i).Shapes(1).Export outputPath, ppShapeFormatSVG
            If fso.FileExists(outputPath) Then exported = exported + 1
        End If
    Next i

    pres.Saved = True
    pres.Close
    fso.DeleteFile tempPath

    MsgBox "Done! Exported " & exported & " of " & n & " SVGs to: " & factoryFolder, vbInformation
End Sub
```
