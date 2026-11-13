# Mihon ManHuaGui Random

非官方、独立维护的 Mihon 扩展，基于 [Keiyoushi extensions-source](https://github.com/keiyoushi/extensions-source) 中的 ManHuaGui（漫画柜）扩展，加入在原有筛选条件下随机浏览的功能。

本项目与 Mihon、Keiyoushi 和漫画柜官方无关联，不计划将随机功能提交至上游扩展仓库。

## 功能

在漫画柜·随机 → 搜索 → 筛选 → **排序方式** 选择 **随机浏览**，可以同时保留年份、地区、类型、连载状态等筛选条件。

- 首次请求筛选结果第一页，读取网站分页总数。
- 随机打乱所有远端页码，Mihon 的连续翻页按随机页序访问。
- 每页内部再次随机打乱漫画条目；同一轮不重复抽取同一远端页码。
- 重新加载第一页会重新生成随机顺序；漫画详情与章节逻辑仍遵循 Keiyoushi 上游。

**当前状态：** 已通过 Kotlin 编译和 APK 打包，仍待 Mihon 实机验证滚动、刷新、并发加载和网络失败处理。随机状态只在内存中保存；网站数据变动时仍可能出现漫画重复。输入非空搜索关键词时延续上游普通搜索行为。

## 独立身份

| 项目 | 本项目 |
| --- | --- |
| APK applicationId | `eu.kanade.tachiyomi.extension.zh.manhuaguirandom` |
| 漫画源名称 | 漫画柜·随机 |
| 固定漫画源 ID | `3671038168652510143` |
| 模块目录 | `src/zh/manhuagui` |
| Kotlin 包路径 | 保持上游路径 |

APK 包名与漫画源 ID 均与原版不同，可以共存，但两者书架条目不会自动共享。

## 本地编译

需要 JDK 25、Android SDK Platform 37.0、Build-Tools；使用项目自带的 Gradle Wrapper，无需 WSL 或 Android Studio。

在项目根目录创建本地（不入库）配置文件 `local.properties`：

```properties
sdk.dir=D:/.sdk/android-sdk
```

设置 `JAVA_HOME` 指向 JDK 25，在 Windows PowerShell 运行：

```powershell
.\gradlew.bat :src:zh:manhuagui:assembleDebug
```

编译 APK 位于 `src/zh/manhuagui/build/outputs/apk/debug/`。

Debug APK 使用调试签名，只适合本地测试。**GitHub Actions 只在推送版本 Tag 时创建 Release**，不会因为推送 `main`、PR 或普通提交而执行编译。

### 发布流程

先在本地完整测试对应的提交。发布前修改 `src/zh/manhuagui/build.gradle.kts` 中的 `versionCode`，确保版本标签与 `libVersion.versionCode` 一致，例如当前 `libVersion = "1.6"`、`versionCode = 1` 对应标签 `v1.6.1`。

工作流 `.github/workflows/release.yml` 在收到版本 Tag 后：

1. 验证 Git Tag 与 APK 版本一致。
2. 使用仓库加密 Secrets 还原固定签名文件（完成后删除）。
3. 执行 `assembleRelease` 编译、签名并验证 APK。
4. 在 GitHub Releases 创建同名版本并上传正式 APK。

在本地验证并提交后，发布示例：

```powershell
git tag v1.6.1
git push origin v1.6.1
```

仓库需要 `SIGNING_KEYSTORE_BASE64`、`KEY_STORE_PASSWORD`、`KEY_PASSWORD` 和 `ALIAS` 四个 Secrets。私钥和密码不可提交到仓库。**签名私钥与密码必须额外离线备份**，丢失后新 APK 将无法覆盖相同包名但签名不同的旧 APK。

首次从 Debug 测试版迁移到正式签名版时，因为签名不同，需要先备份必要数据并卸载独立测试插件；原版漫画柜是不同包名，不受影响。

## 定期同步上游（无 Pull Request）

本仓库是独立 Git 历史，**不要执行 git merge upstream/main**，否则会把 Keiyoushi 整个仓库合并进来。

提供 `tools/sync_upstream.py`，只同步上游的 `src/zh/manhuagui` 子目录，用 `tools/upstream-base` 保存的上游基准文件进行三方合并，并尝试保留本项目的少量改动。

先预览（不会改动文件）：

```powershell
python tools/sync_upstream.py
```

确认没有冲突后：

```powershell
python tools/sync_upstream.py --apply
git diff
.\gradlew.bat :src:zh:manhuagui:assembleDebug
```

测试通过后再提交。初次运行会在项目同级创建专用上游缓存目录 `.keiyoushi-manhuagui-cache`，默认只直连，不消耗本地 7890 代理流量。若发生三方合并冲突，会中止且不覆盖现有文件。

同步脚本不会覆盖新增的 `RandomBrowse.kt`。当前上游基准 commit 存于 `tools/UPSTREAM_REVISION`。

**范围说明：**脚本只同步漫画柜扩展源码。如果上游升级了 Gradle、core、compiler、lzstring 或 unpacker，构建基础设施仍需人工同步和验证。

## 主要改动

- Manhuagui.kt：新增随机浏览调用入口。
- Filters.kt：新增随机排序选项。
- RandomBrowse.kt：本项目单独维护的随机分页实现。
- build.gradle.kts：配置独立 APK 身份和源 ID。

## 许可与致谢

基于 Keiyoushi 的 ManHuaGui 扩展和 Tachiyomi/Mihon 扩展框架，保留原项目的 Apache-2.0 许可证，见 [LICENSE](LICENSE)。
