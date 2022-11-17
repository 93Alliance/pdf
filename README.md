# PDF

## 书签工具

![](./doc/bookmarks.png)

1. 支持txt文件导入书签
2. 支持4级目录添加
3. 追加书签和覆盖书签两种模式（追加模式只能保持源pdf的4级目录）

# 打包

windows
```
pyinstaller -F -w --upx-exclude=vcruntime140.dll main.py
```
linux
```
pyinstaller -F -w main.py
```
修改 main.spec 中的
```
excludes=["numpy", "scipy", "opencv", "PySide6"],
```
再次执行
```
pyinstaller main.spec
```
