@echo off
setlocal
cd /d "%~dp0"
if not "%~1"=="" goto custom
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error example.tex
if errorlevel 1 exit /b 1
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error example-color.tex
exit /b %errorlevel%
:custom
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error %*
exit /b %errorlevel%
