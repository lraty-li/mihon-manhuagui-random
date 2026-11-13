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

注意：Debug APK 使用开发签名，不适合作为长期可升级的正式发行渠道。后续发布稳定版本应配置固定签名密钥，私钥不要提交到仓库。

GitHub Actions 的 build workflow 仅用于构建验证并上传临时 Debug APK，不发布 Releases。

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
