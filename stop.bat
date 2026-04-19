@echo off

taskkill -f -im python*
quarc_run -q -Q *.rt-win64

