# Some modifications to this file copied from the VisPy project
# which is released under a BSD 3-clause license

$MESA_GL_URL = "https://github.com/vispy/demo-data/raw/master/mesa/"

function DownloadMesaOpenGL ($architecture) {
    $webclient = New-Object System.Net.WebClient
    $basedir = $pwd.Path + "\"
    $filepath = $basedir + "opengl32.dll"
    # Download and retry up to 3 times in case of network transient errors.
    $url = $MESA_GL_URL + "opengl32_mingw_" + $architecture + ".dll"
    Write-Host "Downloading" $url
    $retry_attempts = 2
    for($i=0; $i -lt $retry_attempts; $i++){
        try {
            $webclient.DownloadFile($url, $filepath)
            break
        }
        Catch [Exception]{
            Start-Sleep 1
        }
    }
    if (Test-Path $filepath) {
        Write-Host "File saved at" $filepath
    } else {
        # Retry once to get the error message if any at the last try
        $webclient.DownloadFile($url, $filepath)
    }
}

function main () {
    DownloadMesaOpenGL $env:PYTHON_ARCH
}

main
