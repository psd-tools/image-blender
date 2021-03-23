cython -w .\src image_blender.pyx
@if errorlevel 1 goto error

pip install -U .
@if errorlevel 1 goto error

@goto :eof

:error
@echo/
@pause
