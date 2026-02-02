# 本地打包指南

## 打包步骤

```bash
pip install pyinstaller==6.18.0 -r requirements.txt
pyinstaller --onefile --noconsole --name screen-ocr --specpath build src/main.py
```

打包完成后，exe 文件位于 `dist/screen-ocr.exe`。

## 手动发布到 GitHub Release

### 方式一：gh 命令行

```bash
git tag v1.0.0
git push origin v1.0.0
gh release create v1.0.0 dist/screen-ocr.exe --title "v1.0.0" --notes "首次发布"
```

### 方式二：GitHub 网页

1. 进入仓库页面，点击右侧 **Releases**
2. 点击 **Create a new release**
3. 输入 Tag（如 `v1.0.0`）和标题
4. 拖拽 `dist/screen-ocr.exe` 到上传区域
5. 点击 **Publish release**
