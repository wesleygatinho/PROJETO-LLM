@echo off
setlocal
pushd "%~dp0"
where latexmk >nul 2>&1
if errorlevel 1 (
  echo latexmk nao encontrado. Use o MiKTeX instalado no computador.
  popd
  exit /b 1
)
latexmk -pdf "previa_rascunho_sbc.tex"
if errorlevel 1 (
  echo A compilacao falhou. Consulte previa_rascunho_sbc.log.
  popd
  exit /b 1
)
echo PDF atualizado: "%~dp0previa_rascunho_sbc.pdf"
popd
endlocal
