$ErrorActionPreference = 'SilentlyContinue'
Set-Location D:\Projects\SIH\SIH26095
$code = & backend\.venv\Scripts\python.exe -c "import urllib.request,sys; r=urllib.request.urlopen('https://drishti-api-u0qf.onrender.com/docs',timeout=20); html=r.read().decode('utf-8',errors='replace'); sys.stdout.write('STATUS='+str(r.status)+chr(10)+'LEN='+str(len(html))+chr(10)+html[:2000])"
Out-File -Encoding utf8 D:\Projects\SIH\SIH26095\check_docs_output.txt -InputObject $code