# 笔记网站（`网站/`）

把三门课的笔记（`ADS/笔记/`、`密码学基础/笔记/`、`sys2/笔记/`）发布成一个静态网站：
MkDocs + Material 主题，带侧边栏导航、全文搜索（中文分词）、深色模式与本地 MathJax 公式渲染。

## 1. 快速开始

```bash
pip install -r 网站/requirements.txt   # 只需一次（mkdocs-material、jieba）
python 网站/fetch_mathjax.py           # 只需一次：把 MathJax 下到 网站/vendor/（离线可用）
python 网站/build.py                   # 汇集 → 构建 → 自检，一条命令搞定
python 网站/build.py -s                # 本地预览：http://127.0.0.1:8000（Ctrl+C 退出）
python 网站/build.py --no-check        # 只构建，不跑自检
```

`python 网站/build.py` 依次做三件事：

1. `prepare.py`：清空并重建 `网站/.docs/`，把三个课程的 `笔记/*.md`、`笔记/assets/`、
   仓库 `README.md`、根目录 `网站首页.md` 复制进去（**只复制，不动原件**）；
2. `mkdocs build`：生成静态站点到 `网站/site/`；
3. `check_site.py`：逐条校验生成结果里的链接、锚点与图片。

## 2. 目录

| 路径 | 说明 |
|---|---|
| `mkdocs.yml` | 站点配置：主题、Markdown 扩展、`nav`（列出全部 40 篇笔记） |
| `gh_slug.py` | **标题锚点算法**：复刻 GitHub 规则，见下文 §3.1 |
| `prepare.py` | 把笔记与配图汇集到 `.docs/`（生成目录，见 §3.2 为何用点号开头） |
| `build.py` | 构建入口（prepare → mkdocs build → 自检） |
| `check_site.py` | 站点自检脚本 |
| `fetch_mathjax.py` | 下载本地 MathJax 到 `vendor/` |
| `static/` | 站点静态资源（目前是 MathJax 配置 `mathjax-config.js`） |
| `vendor/mathjax/` | 本地打包的 MathJax 3（约 1.5 MB，含字体），公式**不联网**也能渲染 |
| `.docs/`、`site/`、`.cache/` | 生成物，不入库（见 `.gitignore` §7、§8） |

站点首页正文放在仓库根目录的 `网站首页.md`（构建时复制为 `.docs/index.md`），
这样它的相对链接在仓库根目录与 `网站/.docs/` 下都成立，仓库自带的链接自检脚本也不会误报。
仓库 `README.md` 会另发一页「关于仓库」。

## 3. 关键约定

### 3.1 标题锚点必须用 GitHub 规则

笔记里有 480 余条 `其他笔记.md#小节` 链接与 470 余条同文件小节锚点，
它们都按 GitHub / VS Code 预览的 slug 规则写，并用 `ADS/assets/check_md_anchors.py` 自查。
MkDocs 默认的 slug 规则与之不同（会把连续空格 / 连字符并成一个 `-`，重名时用 `_1` 而不是 `-1`），
因此 `mkdocs.yml` 里用 `slugify: !!python/name:gh_slug.slugify` 指定了 `网站/gh_slug.py` 的算法。
**这也意味着必须从 `网站/` 目录（或用 `网站/build.py`）构建**，否则 `gh_slug` 导入不到。

### 3.2 不要直接改 `网站/.docs/`

`.docs/` 是 `prepare.py` 每次构建时清空重建的暂存目录。**目录名用点号开头是有意的**：
仓库自带的两个自检脚本会跳过 `.` 开头的目录，因此 `python3 ADS/assets/check_md_links.py .`
与 `check_md_anchors.py .` 不必传额外的 `-x`，也不会把生成副本当成笔记重复检查。

要改内容就改
`ADS/笔记/`、`密码学基础/笔记/`、`sys2/笔记/` 里的原件，以及根目录的 `网站首页.md`。

### 3.3 新增或改名笔记后

1. 在 `mkdocs.yml` 的 `nav` 里加 / 改对应条目；
2. 重新跑 `python 网站/build.py`，让 `check_site.py` 核对链接是否还有效。

### 3.4 内容范围

- 发布 `笔记/` 下的全部 `.md` 与 `assets/` 内容（含生成配图的 `.py` 脚本，便于复现）；
- 不发布 `ADS/笔记/tasks.md`（个人待办草稿）与各 `笔记/README.md`（目录说明，仓库内用）——
  两者都在 `prepare.py` 的 `SKIP_FILES` 里：MkDocs 会把 `README.md` 当作所在目录的 `index.md`，
  与 `check_site.py` 的「md → 同名 html」核对冲突，所以 `笔记/README.md` 只留在仓库里，不进站点；
- 不发布讲义原件（`ADS/Materials/`、`sys2/*.pdf`）与其他课程目录。

注意：上列 `.py`（`ADS/笔记/assets/*.py`）与两个自检脚本 `ADS/assets/check_md_anchors.py`、
`ADS/assets/check_md_links.py` 必须在仓库里（`.gitignore` §10 手工放行）。`check_site.py`
以 `check_md_anchors.py` 为锚点规则的唯一标准：CI 检出时缺这个文件会直接退出，
报「找不到锚点规则脚本」；笔记正文直接链接 `assets/*.py`，缺文件会报「站点里缺少文件」。

## 4. 自检都查什么

`python 网站/check_site.py`（通常由 `build.py` 自动调用）：

1. **标题锚点一致性**：每篇笔记的每个标题，按仓库自带规则算出的锚点必须出现在
   生成页面的 `id` 里 —— 这条能立刻发现「站点锚点算法与笔记不一致」；
2. **源文件链接**：`.docs/**/*.md` 里的 `.md#小节` 与图片等相对路径逐条核对；
3. **生成页面链接**：`site/**/*.html` 里的 `href` / `src` 是否都能落到真实文件，
   且没有残留未改写的 `.md`；
4. **站点资源**：MathJax 等 `extra_javascript` 是否存在。

完整报告写入 `网站/.cache/check_report.txt`。当前基线：39 个页面、500 条跨文件链接、
795 条同页锚点、141 条图片/附件、875 个标题锚点，全部通过（2026-10-20：加入 sys2 第 5、6 讲后重跑）。

## 5. 部署

站点是纯静态文件，`网站/site/` 整体拷到任意静态托管即可。仓库里也带了一条自动部署：

| 文件 | 作用 |
|---|---|
| `.github/workflows/pages.yml` | 推送 `master` 后：装依赖 → `python 网站/build.py` → 核对自检报告 → 发布到 GitHub Pages |

首次使用需在仓库 **Settings → Pages → Source** 选择 **GitHub Actions**。
工作流跑的就是本地的同一条命令，并且**自检不通过会让构建失败**（不会把断链的站点发上去）。

注意 `mkdocs.yml` 里的

```yaml
site_url: https://nothing793.github.io/note/
```

它决定主题资源与 `404.html` 里**根绝对地址的前缀**（`/note/assets/...`）。
换了部署位置（例如放到用户主页根目录）必须同步修改，否则资源会 404 ——
`check_site.py` 会把前缀不一致报出来。
