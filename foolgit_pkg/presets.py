"""
FoolGit 预设功能库与元数据定义
定义出厂默认核心功能与通俗易懂的备选扩展功能。
"""

# 出厂默认启用的核心功能 ID 列表 (仅 6 个日常最高频项)
DEFAULT_ACTIVE_IDS = ["sync", "pull", "status", "undo", "branch", "stash"]

# 所有官方预设功能的详细说明与行为定义
PRESET_LIBRARY = {
    # ── 出厂默认 6 大核心功能 ──
    "sync": {
        "id": "sync",
        "name": "一键保存并同步",
        "tag": "推荐",
        "short_desc": "自动拉取 ➔ 保存改动 ➔ 提交 ➔ 推送远端",
        "detail": "最核心的日常命令！执行 safe pull，添加所有改动，生成提交信息并推送到远端仓库。",
        "is_builtin": True,
        "default_enabled": True,
    },
    "pull": {
        "id": "pull",
        "name": "一键拉取最新代码",
        "tag": "常用",
        "short_desc": "从远程仓库下载最新更新并安全合并",
        "detail": "每天开始工作前必备，检查并下载团队伙伴推送到远程的最新代码。",
        "is_builtin": True,
        "default_enabled": True,
    },
    "status": {
        "id": "status",
        "name": "查看代码改动详情",
        "tag": "状态",
        "short_desc": "清晰展示当前分支、改动文件清单及超前/落后状态",
        "detail": "列出哪些文件新增、修改或删除，以及本地是否领先或落后远程。",
        "is_builtin": True,
        "default_enabled": True,
    },
    "undo": {
        "id": "undo",
        "name": "后悔药 / 撤销改动",
        "tag": "安全",
        "short_desc": "一键撤销写乱的代码、丢弃修改或撤回上次提交",
        "detail": "防呆必备！提供三级后悔药：1. 撤销指定文件；2. 放弃所有未提交修改；3. 撤回上一次提交(代码保留)。",
        "is_builtin": True,
        "default_enabled": True,
    },
    "branch": {
        "id": "branch",
        "name": "切换或新建分支",
        "tag": "分支",
        "short_desc": "直接按编号秒切分支，或一键输入新名称创建分支",
        "detail": "不用记 checkout / switch 参数，列出本地分支一键切换，或直接根据当前分支切出新特性分支。",
        "is_builtin": True,
        "default_enabled": True,
    },
    "stash": {
        "id": "stash",
        "name": "暂存保存 / 恢复改动",
        "tag": "储藏",
        "short_desc": "临时封存没写完的代码，随时一键恢复",
        "detail": "代码写了一半但需要紧急拉取最新代码或切分支时，一键存盘放入暂存箱，随时一键取回。",
        "is_builtin": True,
        "default_enabled": True,
    },

    # ── 备选功能库 (供用户自选开启) ──
    "history": {
        "id": "history",
        "name": "查看简明提交历史",
        "tag": "扩展",
        "short_desc": "按时间倒序列出最近的 10 次提交与作者",
        "detail": "查看最近大家都改了什么，展示简洁的一行式版本流水线。",
        "is_builtin": False,
        "default_enabled": False,
    },
    "diff": {
        "id": "diff",
        "name": "查看具体代码差异",
        "tag": "扩展",
        "short_desc": "逐行对比改动代码的高亮变化 (diff)",
        "detail": "显示工作区中每一行代码的修改对比，绿色代表新增，红色代表删除。",
        "is_builtin": False,
        "default_enabled": False,
    },
    "clean": {
        "id": "clean",
        "name": "清理未跟踪垃圾文件",
        "tag": "扩展",
        "short_desc": "一键清理本地新建但未加入 git 的临时文件和空目录",
        "detail": "执行 git clean，清理本地误建或者构建生成的未跟踪杂质文件，保持工作区干净。",
        "is_builtin": False,
        "default_enabled": False,
    },
    "tag": {
        "id": "tag",
        "name": "版本标签 (Release Tag)",
        "tag": "扩展",
        "short_desc": "打上版本标记 (如 v1.0.0) 并可一键推送到远程",
        "detail": "发布产品版本时使用，给当前提交盖上一个版本标签印章并同步到 GitHub/GitLab。",
        "is_builtin": False,
        "default_enabled": False,
    },
    "remote": {
        "id": "remote",
        "name": "查看远程仓库地址",
        "tag": "扩展",
        "short_desc": "查看当前绑定的 GitHub/GitLab 远程仓库链接",
        "detail": "快速检查当前仓库关联的 origin 远端地址与连接配置。",
        "is_builtin": False,
        "default_enabled": False,
    },
    "multi_sync": {
        "id": "multi_sync",
        "name": "多仓库批量巡检与同步",
        "tag": "批量",
        "short_desc": "扫描子目录下所有 Git 项目并进行批量一键同步",
        "detail": "继承 gsyn 的多仓库管理能力：自动查找子目录的 Git 仓库，表格化列出状态并一键批量推送。",
        "is_builtin": False,
        "default_enabled": False,
    },
}
