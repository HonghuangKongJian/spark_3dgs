# Spark 3DGS Viewer

基于浏览器的 **3D Gaussian Splatting（3DGS）** 查看器，同时支持两类数据：

- **Spark 模型**（World Labs / `@sparkjsdev/spark`）：`.ply` / `.spz` / `.splat`
- **XGRIDS Lixel CyberColor 数据集**（`.lcc`）：通过官方 **LCC Web SDK** 加载

> 注：此处 Spark 指 World Labs 的 `@sparkjsdev/spark` 3DGS 渲染库，与 Apache Spark 无关。

纯静态 HTML + ESM `importmap` 实现，无构建步骤。配合一个本地 Python 服务（`server.py`）提供 HTTP 托管、文件夹上传与 Range 分块读取。

## 功能

- 内置默认演示模型（Spark 蝴蝶，CDN 加载）。
- 加载本地 Spark 模型（`.ply` / `.spz` / `.splat`）。
- 加载 LCC 多文件数据集（`.lcc`），支持两种方式：
  - **直接加载本地目录**（推荐）：数据已放在本服务可访问路径下（如 `lcc-result/`），免上传。
  - **选择文件夹上传**：浏览器把整个数据集 POST 到本地服务后再加载。
- 鼠标交互：左键旋转 / 右键平移 / 滚轮缩放（OrbitControls）。
- 加载失败、超时、`.lcc` 兄弟文件缺失等情况均有页面内提示，便于排查。

## 技术栈

| 组件 | 版本 | 说明 |
| --- | --- | --- |
| `@sparkjsdev/spark` | 2.1.0 | SparkJS 3DGS 渲染库（World Labs） |
| `three` | 0.185.1 | 满足 Spark 2.x 的 `peerDependency >= 0.180.0` |
| LCC Web SDK | 0.6.2 | XGRIDS 官方 LCC 渲染 SDK（`sdk/lcc-sdk-three.js`） |
| 运行时 | 浏览器 + 本地 Python 服务 | 无打包、无框架 |

> **LCC Web SDK 为 XGRIDS 闭源 / 专有组件**，仅用于合规用途。`appKey` 可选：留空仅带水印提示，不影响渲染。

## 快速开始

**方式一：一键启动（推荐）**

双击项目内的 **`启动查看器.bat`**，它会自动：

1. 在端口 `8137` 启动本地服务（`server.py`）；
2. 等待服务就绪后在浏览器打开 `http://localhost:8137/spark_3dgs.html`。

**方式二：手动启动**

```bash
# 需 Python 3.7+（server.py 使用 HTTP Range）
python server.py 8137

# 浏览器访问
# http://localhost:8137/spark_3dgs.html
```

## 使用说明

| 操作 | 入口 | 说明 |
| --- | --- | --- |
| 默认模型 | 自动 | 页面加载即显示 CDN 上的 Spark 蝴蝶 |
| 本地 Spark 模型 | “选择文件” | 选 `.ply`/`.spz`/`.splat`（须经由本地 http 打开页面） |
| LCC 直接加载 | “直接加载该目录 LCC” | 默认路径 `lcc-result/bs.lcc`，数据须在本服务路径下 |
| LCC 文件夹上传 | “选择 LCC 数据集文件夹” | 选整个数据集文件夹，浏览器上传到服务后加载 |

### 为什么必须用本地服务（不能 `file://` 直接打开）？

- **Spark 2.x** 使用 Web Worker + WASM 解码 splat，在 `file://` 的“不透明源”下 `blob:` URL 无法被 Worker `fetch`，会报 `URL scheme 'blob' is not supported`。
- **LCC SDK** 用 `new URL(dataPath)` 按文件名主干派生兄弟文件（`index.bin` / `environment.bin` / `data.bin` / `shcoef.bin` / `collision.lci`），必须以 HTTP(S) URL 作为 `dataPath`。

因此**任何本地文件 / 数据集都请通过 `http://localhost:8137/...` 打开本页**。

## 项目结构

```
spark_3dgs/
├── spark_3dgs.html        # 主查看器页面（含 Spark + LCC 双引擎路由）
├── server.py              # 本地服务：静态托管 + 文件夹上传 + HTTP Range(206)
├── 启动查看器.bat          # 一键启动脚本（端口 8137）
├── LCC-Web-0.6.2/         # LCC Web SDK（仅提交 sdk/ 与说明，示例/资源已忽略）
│   └── sdk/lcc-sdk-three.js
├── lcc-result/           # 用户 LCC 数据集（gitignore，约 1.3GB，勿入库）
└── __upload__/            # 运行时文件夹上传落盘目录（gitignore）
```

## 备注

- 需要支持 **WebGL2** 的现代浏览器（Chrome / Edge / Firefox 新版）。
- `lcc-result/` 与 `__upload__/` 已在 `.gitignore` 中忽略，避免把大型数据集 / 临时文件提交进仓库。
- 已验证：**LCC v5.0 数据集（约 1387 万点、COMPRESS 编码、5 级 LOD）可在 LCC Web SDK 0.6.2 下正常渲染**，直接加载与文件夹上传两种方式均可用。

## 许可

- 本项目代码以仓库 LICENSE 为准（如有）。
- LCC Web SDK 及其格式为 **XGRIDS 专有**，使用须遵守其许可条款。
