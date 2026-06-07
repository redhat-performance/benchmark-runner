# provision-disk.ps1

param(
    [string]$DiskID
)

$setup = "c:\tools\fio"
$diskExists = Get-Disk -Number $DiskID -ErrorAction SilentlyContinue
$diskExists = ($null -ne $diskExists)

if ($diskExists) {
    set-disk -Number $DiskID -IsOffline $true
    set-disk -Number $DiskID -IsReadOnly $false

    get-disk

    echo "select disk $DiskID" > "$setup\data-disk-part.txt"
    echo "online disk" >> "$setup\data-disk-part.txt"
    echo "clean" >> "$setup\data-disk-part.txt"
    echo "convert gpt" >> "$setup\data-disk-part.txt"
    echo "create partition primary" >> "$setup\data-disk-part.txt"
    echo "format quick fs=ntfs label=DataDisk" >> "$setup\data-disk-part.txt"
    echo "assign letter=D" >> "$setup\data-disk-part.txt"

    $content = get-content -Path "$setup\data-disk-part.txt" -Raw
    set-content -Path "$setup\data-disk-part.txt" -Value $content -NoNewline

    diskpart /s "$setup\data-disk-part.txt" > "$setup\disk-part.out"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: diskpart failed with exit code $LASTEXITCODE"
        Get-Content "$setup\disk-part.out"
        exit 1
    }
    Write-Host "Disk $DiskID partitioned and formatted"
} else {
    Write-Host "ERROR: Disk $DiskID not found"
    exit 1
}
