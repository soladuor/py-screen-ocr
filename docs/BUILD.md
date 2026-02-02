# 打包指南（GitHub Actions）

项目已配置 GitHub Actions 自动打包，推送 tag 即可自动构建并发布。

## 使用方法

1. 编辑 `docs/RELEASE_NOTES.md`，填写本次发布的更新内容

2. 创建并推送 tag：
   ```bash
   git add .
   git commit -m "release: v1.0.0"
   git tag v1.0.0
   git push origin v1.0.0
   # git push origin main --tags
   ```

3. Actions 会自动在云端打包 exe 并上传到 Release 页面

## 文件说明

| 文件 | 说明 |
|------|------|
| `.github/workflows/release.yml` | 工作流配置 |
| `docs/RELEASE_NOTES.md` | Release 发布说明，每次发版前更新 |
