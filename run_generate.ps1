Param(
    [switch]$NoOpen  # pass -NoOpen to skip opening the PDF after generation
)

# Stop on errors
$ErrorActionPreference = 'Stop'

try {
    # Change to the script's directory (works even with special chars in path)
    if ($PSScriptRoot) {
        Set-Location -LiteralPath $PSScriptRoot
    } else {
        Set-Location -LiteralPath (Split-Path -Parent $MyInvocation.MyCommand.Definition)
    }

    Write-Host "Working directory: $PWD"

    # Locate and dot-source the virtualenv PowerShell activation script
    $activate = Join-Path -Path $PWD -ChildPath 'venv\Scripts\Activate.ps1'
    if (-not (Test-Path -LiteralPath $activate)) {
        Write-Error "Virtualenv activation script not found: $activate"
        exit 1
    }

    Write-Host "Activating virtualenv: $activate"
    . $activate

    # Run the generator
    Write-Host "Running generate.py..."
    python .\generate.py

    # Open the resulting PDF unless suppressed
    if (-not $NoOpen) {
        $pdf = Join-Path -Path $PWD -ChildPath 'warmup.pdf'
        if (Test-Path -LiteralPath $pdf) {
            Write-Host "Opening $pdf"
            Start-Process -FilePath $pdf
        } else {
            Write-Warning "PDF not found: $pdf"
        }
    }

} catch {
    Write-Error "An error occurred: $_"
    exit 1
}