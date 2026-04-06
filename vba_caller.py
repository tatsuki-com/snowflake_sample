"""VBA連携用モジュール

ファイル一覧.xlsm にボタンを2つ配置し、以下のVBAマクロを割り当ててください。

=== VBA サンプルコード ===

' 収集ボタン用マクロ
Sub RunCollect()
    Dim startCell As Range
    Set startCell = ThisWorkbook.Sheets("一覧").Range("J1")  ' 開始日時セル

    If IsEmpty(startCell.Value) Then
        MsgBox "開始日時(J1セル)を入力してください。", vbExclamation
        Exit Sub
    End If

    Dim startDatetime As String
    startDatetime = Format(startCell.Value, "yyyy-mm-dd hh:nn:ss")

    Dim pythonPath As String
    pythonPath = "python"  ' 必要に応じてフルパスに変更

    Dim scriptDir As String
    scriptDir = ThisWorkbook.Path

    Dim cmd As String
    cmd = "cmd /c cd /d """ & scriptDir & """ && " & _
          pythonPath & " main.py collect --start """ & startDatetime & """"

    Shell cmd, vbNormalFocus
    MsgBox "収集処理を起動しました。", vbInformation
End Sub

' 集約ボタン用マクロ
Sub RunAggregate()
    Dim pythonPath As String
    pythonPath = "python"  ' 必要に応じてフルパスに変更

    Dim scriptDir As String
    scriptDir = ThisWorkbook.Path

    Dim cmd As String
    cmd = "cmd /c cd /d """ & scriptDir & """ && " & _
          pythonPath & " main.py aggregate"

    Shell cmd, vbNormalFocus
    MsgBox "集約処理を起動しました。", vbInformation
End Sub

=============================
"""

# このファイルはVBAサンプルコードの参照用です。
# Python側からの直接的な処理はありません。
