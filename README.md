# PDF

# 打包

```
pyinstaller -F -w --upx-exclude=vcruntime140.dll main.py
```
修改 main.spec 中的
```
excludes=["numpy", "scipy", "opencv", "PySide6"],
```
再次执行
```
pyinstaller main.spec
```